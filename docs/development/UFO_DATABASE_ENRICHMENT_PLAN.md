# UFO Database Enrichment Plan

**Target version:** v0.4.x  
**Goal:** Ingest external UFO sighting databases to enrich the Data Explorer with case-level sighting data, expanding coverage from organizational/financial data to include the underlying incident reports. Additionally, design a **generic dataset ingestion framework** that lets users add their own datasets and optionally share them with the community — with strong guarantees around privacy, security, and reliability.

---

## Table of Contents

1. [Source Databases](#source-databases)
2. [Relevance Analysis](#relevance-analysis)
3. [Data Model](#data-model)
4. [Dataset Plugin Architecture](#dataset-plugin-architecture)
5. [Ingestion Pipeline](#ingestion-pipeline)
6. [Privacy Framework](#privacy-framework)
7. [Security Hardening](#security-hardening)
8. [Reliability & Data Integrity](#reliability--data-integrity)
9. [User-Contributed Datasets & Sharing](#user-contributed-datasets--sharing)
10. [Source-Specific Parsing Notes](#source-specific-parsing-notes)
11. [Data Directory Structure](#data-directory-structure)
12. [Frontend Integration](#frontend-integration)
13. [Order of Work](#order-of-work)
14. [Dependencies](#dependencies)
15. [Risks and Mitigations](#risks-and-mitigations)
16. [Open Questions](#open-questions)

---

## Source Databases

| # | Name | Format | Cases | License / Notes | Relevance to PRH |
|---|------|--------|-------|-----------------|-------------------|
| 1 | **MUFON CMS** (6/17/2024 scrape) | CSV | 128,142 | DO NOT REDISTRIBUTE | High - largest civilian UFO investigation org; entities like MUFON already in our DB |
| 2 | **UFOCAT-2023** (CUFOS) | CSV (from Access) | 320,419 | $10 donation to CUFOS | Very high - multi-source aggregation (MUFON, NUFORC, etc.); academic provenance |
| 3 | **UPDB.app** (Publius, 8/23/2023) | CSV (from PostgreSQL) | 336,665 | Mixed (bought data) | Highest case count; overlaps with MUFON+NUFORC+phenomAInon |
| 4 | **UFO-Search / Majestic** (Rich Geldreich) | JSON (`majestic.json`) | Varies | Open source, share freely | Good - open license, unique data from Geldreich's research |
| 5 | **NUFORC Data Bank** (5/1/2024 scrape) | CSV | 148,744 | DO NOT REDISTRIBUTE | High - official NUFORC data; Peter Davenport's original reports |

**Total raw cases: ~934,000** (with significant overlap between sources).

---

## Relevance Analysis

### What PRH already has
- **Entities:** Organizations (MUFON, NRO, CIA, Lockheed Martin, etc.), individuals, programs, facilities.
- **Money flows:** Federal contracts, awards, agency-to-contractor funding.
- **FOIA targets:** Agencies and specific record requests.
- **Relationships:** Org charts, hierarchy, intel stack levels L1–L6.

### What the UFO databases add
- **Sighting/case data:** Date, location (lat/lon), description, shape, duration, witness count.
- **Geographic dimension:** Heat maps, location-based analysis (near military bases, DOE facilities).
- **Temporal dimension:** Sighting frequency over time, correlation with program timelines.
- **Cross-referencing:** Match sighting locations/dates to known facilities (Area 51, Edwards AFB, Dugway) and programs (e.g. activity spikes near program start dates).

### What's NOT directly useful
- Raw witness narratives (large text blobs) — store but don't load into the main explorer initially.
- Duplicate cases across sources — need deduplication.
- Low-quality reports (insufficient data, hoaxes) — need filtering.

---

## Data Model

### New table: `ufo_sightings`

```python
class UFOSighting(Base):
    __tablename__ = "ufo_sightings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_db = Column(String, index=True)          # 'mufon', 'nuforc', 'ufocat', 'updb', 'majestic'
    source_id = Column(String)                       # Original ID from source database
    date_occurred = Column(DateTime, index=True)     # When the sighting happened
    date_reported = Column(DateTime)                 # When it was reported
    city = Column(String)
    state = Column(String, index=True)
    country = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    shape = Column(String, index=True)               # 'disk', 'triangle', 'light', 'cigar', etc.
    duration_seconds = Column(Integer)
    description = Column(Text)                       # Witness narrative (nullable, large)
    summary = Column(String)                         # Short summary if available
    source_citation = Column(String)                 # Which CSV/database this came from

    # Deduplication
    dedupe_hash = Column(String, unique=True, index=True)  # Hash of (date, lat, lon, shape) for dedup

    # Data quality (see Reliability section)
    quality_score = Column(Float, default=0.0)       # 0.0–1.0 automated quality rating
    is_flagged = Column(Boolean, default=False)      # Flagged for manual review
    flag_reason = Column(String, nullable=True)      # Why it was flagged

    __table_args__ = (
        Index('idx_sighting_geo', 'latitude', 'longitude'),
        Index('idx_sighting_date_state', 'date_occurred', 'state'),
        Index('idx_sighting_source_dedup', 'source_db', 'source_id'),
    )
```

### New table: `sighting_entity_links` (cross-reference)

```python
class SightingEntityLink(Base):
    __tablename__ = "sighting_entity_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sighting_id = Column(Integer, ForeignKey("ufo_sightings.id"), index=True)
    entity_id = Column(String, ForeignKey("entities.entity_id"), index=True)
    link_type = Column(String)       # 'near_facility', 'during_program', 'reported_to_agency'
    confidence = Column(Float)       # 0.0–1.0
    notes = Column(String)
```

This lets us answer: "How many sightings occurred within 50 miles of Area 51?" or "Were there sighting spikes during the Kona Blue program timeline?"

### New table: `user_datasets` (user-contributed dataset registry)

```python
class UserDataset(Base):
    __tablename__ = "user_datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, unique=True, index=True)   # UUID
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_fingerprint = Column(String, index=True)          # Pseudonymous owner (see Privacy)
    schema_version = Column(String, default="1.0")          # Schema version for forward compat
    record_count = Column(Integer, default=0)
    file_hash = Column(String)                              # SHA-256 of the uploaded file
    file_size_bytes = Column(Integer)
    original_filename = Column(String)                      # Sanitized original name
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")              # pending | validated | approved | rejected
    visibility = Column(String, default="private")          # private | shared | community
    license_type = Column(String, default="unknown")        # open, restricted, do_not_redistribute, unknown
    data_classification = Column(String, default="public")  # public | contains_pii | sensitive
    validation_report = Column(Text)                        # JSON blob with validation results
    ingestion_log = Column(Text)                            # JSON blob with load stats

    __table_args__ = (
        Index('idx_dataset_owner', 'owner_fingerprint'),
        Index('idx_dataset_status', 'status'),
        Index('idx_dataset_visibility', 'visibility'),
    )
```

### New table: `dataset_audit_log`

```python
class DatasetAuditLog(Base):
    __tablename__ = "dataset_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("user_datasets.dataset_id"), index=True)
    action = Column(String, nullable=False)           # upload, validate, approve, reject, delete, share, unshare
    actor_fingerprint = Column(String, index=True)    # Who performed the action
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(Text)                            # JSON blob with action-specific details
    ip_hash = Column(String)                          # Hashed IP for abuse prevention (not raw IP)
```

---

## Dataset Plugin Architecture

To make it easy for users to add their own datasets, we use a **registry-based plugin system** where each data source is defined by a manifest + parser.

### Design Principles

1. **Convention over configuration** — sensible defaults for common CSV/JSON formats.
2. **Schema-first** — every dataset declares its schema before ingestion.
3. **Fail-safe** — validation runs before any data touches the database.
4. **Idempotent** — re-running ingestion with the same data produces the same result.

### Dataset Manifest (`dataset_manifest.yaml`)

Each dataset (built-in or user-contributed) is described by a manifest:

```yaml
# Example: NUFORC
dataset:
  id: "nuforc_2024"
  name: "NUFORC Data Bank (May 2024)"
  version: "1.0"
  license: "do_not_redistribute"
  source_url: "https://nuforc.org"

format:
  type: "csv"                         # csv | json | jsonl
  encoding: "utf-8"
  delimiter: ","
  has_header: true
  max_file_size_mb: 500               # Reject files larger than this

schema:
  fields:
    - name: "date_time"
      maps_to: "date_occurred"        # Maps to UFOSighting field
      type: "datetime"
      formats: ["MM/DD/YYYY HH:mm", "YYYY-MM-DD"]
      required: true
    - name: "city"
      maps_to: "city"
      type: "string"
      max_length: 200
    - name: "state"
      maps_to: "state"
      type: "string"
      max_length: 100
    - name: "country"
      maps_to: "country"
      type: "string"
      max_length: 100
      default: "US"
    - name: "shape"
      maps_to: "shape"
      type: "string"
      normalize: true                  # Apply shape normalization map
    - name: "duration"
      maps_to: "duration_seconds"
      type: "duration"                 # Auto-parse "5 minutes" → 300
    - name: "summary"
      maps_to: "summary"
      type: "string"
      max_length: 1000
    - name: "posted"
      maps_to: "date_reported"
      type: "datetime"

validation:
  required_fields: ["date_time"]
  min_records: 10                      # Reject trivially small files
  max_records: 1_000_000              # Safety cap
  reject_if_error_rate_above: 0.20    # If >20% of rows fail validation, reject entire file
  pii_scan: true                       # Run PII detection on text fields

dedup:
  strategy: "hash"
  hash_fields: ["date_occurred", "latitude", "longitude", "shape"]
  hash_precision:
    latitude: 2                        # Round to 2 decimal places
    longitude: 2
```

### Parser Registry

```python
# backend/ingestion/registry.py

from typing import Dict, Type
from backend.ingestion.base_parser import BaseParser

_PARSER_REGISTRY: Dict[str, Type[BaseParser]] = {}

def register_parser(source_id: str, parser_class: Type[BaseParser]):
    """Register a parser for a data source."""
    _PARSER_REGISTRY[source_id] = parser_class

def get_parser(source_id: str) -> BaseParser:
    """Get parser instance for a data source. Falls back to GenericCSVParser."""
    parser_class = _PARSER_REGISTRY.get(source_id, GenericCSVParser)
    return parser_class()
```

### Base Parser Interface

```python
# backend/ingestion/base_parser.py

from abc import ABC, abstractmethod
from typing import Generator, Dict, Any
from pathlib import Path

class BaseParser(ABC):
    """Base class for all dataset parsers.
    
    Parsers are streaming — they yield one record at a time to
    support datasets that don't fit in memory.
    """

    @abstractmethod
    def parse(self, file_path: Path, manifest: dict) -> Generator[Dict[str, Any], None, None]:
        """Yield normalized records one at a time.

        Each yielded dict must conform to the UFOSighting schema:
        {
            "source_db": str,
            "source_id": str | None,
            "date_occurred": datetime | None,
            "date_reported": datetime | None,
            "city": str | None,
            "state": str | None,
            "country": str | None,
            "latitude": float | None,
            "longitude": float | None,
            "shape": str | None,
            "duration_seconds": int | None,
            "description": str | None,
            "summary": str | None,
            "source_citation": str,
        }
        """
        ...

    def validate_record(self, record: dict, manifest: dict) -> tuple[bool, list[str]]:
        """Validate a single record. Returns (is_valid, list_of_errors)."""
        errors = []
        schema = manifest.get("schema", {})

        for field_def in schema.get("fields", []):
            target = field_def.get("maps_to")
            if field_def.get("required") and not record.get(target):
                errors.append(f"Missing required field: {target}")

            max_len = field_def.get("max_length")
            value = record.get(target)
            if max_len and isinstance(value, str) and len(value) > max_len:
                errors.append(f"Field {target} exceeds max length {max_len}")

        return (len(errors) == 0, errors)
```

### Generic CSV Parser (handles most user uploads)

```python
# backend/ingestion/generic_csv_parser.py

import csv
from pathlib import Path
from typing import Generator, Dict, Any
from backend.ingestion.base_parser import BaseParser
from backend.ingestion.normalizers import normalize_shape, parse_duration, parse_datetime_flexible

class GenericCSVParser(BaseParser):
    """Handles any CSV that provides a manifest with field mappings."""

    def parse(self, file_path: Path, manifest: dict) -> Generator[Dict[str, Any], None, None]:
        encoding = manifest.get("format", {}).get("encoding", "utf-8")
        delimiter = manifest.get("format", {}).get("delimiter", ",")
        field_map = {f["name"]: f for f in manifest.get("schema", {}).get("fields", [])}

        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_num, row in enumerate(reader, start=2):  # +2 for header + 1-indexed
                try:
                    record = {"_row_num": row_num}
                    for csv_col, field_def in field_map.items():
                        raw_value = (row.get(csv_col) or "").strip()
                        target = field_def["maps_to"]
                        field_type = field_def.get("type", "string")

                        if field_type == "datetime":
                            record[target] = parse_datetime_flexible(
                                raw_value, field_def.get("formats", [])
                            )
                        elif field_type == "duration":
                            record[target] = parse_duration(raw_value)
                        elif field_type == "float":
                            record[target] = _safe_float(raw_value)
                        elif field_type == "string" and field_def.get("normalize"):
                            record[target] = normalize_shape(raw_value)
                        else:
                            record[target] = raw_value or field_def.get("default")

                    yield record
                except Exception as e:
                    yield {"_row_num": row_num, "_error": str(e)}
```

---

## Ingestion Pipeline

The pipeline is a **5-phase process** with safety gates between each phase. Any failure in an early phase prevents data from reaching the database.

```
Upload → Quarantine → Validate → Transform → Load → Cross-Reference
              │            │           │         │          │
              ▼            ▼           ▼         ▼          ▼
         Virus scan   Schema check  Normalize  Atomic    Facility
         Size check   PII scan      Dedup      insert    proximity
         Type check   Quality score Shape map  Rollback  Timeline
                                    Duration   on error  match
```

### Phase 0: Upload & Quarantine

All uploaded files land in a **quarantine directory** before any processing.

```python
QUARANTINE_DIR = "data/quarantine/"      # Temporary holding area
MAX_UPLOAD_SIZE_MB = 500                 # Configurable per environment
ALLOWED_EXTENSIONS = {".csv", ".json", ".jsonl", ".tsv"}
ALLOWED_MIME_TYPES = {"text/csv", "application/json", "text/plain", "text/tab-separated-values"}

async def quarantine_upload(file: UploadFile, owner_fingerprint: str) -> QuarantineResult:
    """Accept an uploaded file into quarantine for validation.

    Security checks before writing to disk:
    1. File extension whitelist
    2. MIME type validation (don't trust Content-Type header alone)
    3. File size limit
    4. Filename sanitization (strip path traversal, null bytes, special chars)
    5. Magic byte verification (ensure content matches declared type)
    """
    # Sanitize filename — NEVER trust user-supplied filenames
    safe_name = sanitize_filename(file.filename)
    ext = Path(safe_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' not allowed. Accepted: {ALLOWED_EXTENSIONS}")

    # Write to quarantine with a UUID name (not the user's filename)
    quarantine_path = QUARANTINE_DIR / f"{uuid4()}{ext}"
    
    # Stream to disk with size checking (don't load entire file into memory)
    total_bytes = 0
    hasher = hashlib.sha256()
    async with aiofiles.open(quarantine_path, "wb") as out:
        while chunk := await file.read(8192):
            total_bytes += len(chunk)
            if total_bytes > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                quarantine_path.unlink(missing_ok=True)
                raise ValidationError(f"File exceeds {MAX_UPLOAD_SIZE_MB}MB limit")
            hasher.update(chunk)
            await out.write(chunk)

    return QuarantineResult(
        quarantine_path=quarantine_path,
        file_hash=hasher.hexdigest(),
        file_size_bytes=total_bytes,
        original_filename=safe_name,
    )
```

### Phase 1: Validate

```python
async def validate_dataset(quarantine_path: Path, manifest: dict) -> ValidationReport:
    """Run all validation checks on a quarantined file.

    Returns a structured report with pass/fail status and detailed findings.
    """
    report = ValidationReport()

    # 1. Structural validation — can we parse the file at all?
    try:
        parser = get_parser(manifest["dataset"]["id"])
        records = list(parser.parse(quarantine_path, manifest))
        report.total_records = len([r for r in records if "_error" not in r])
        report.parse_errors = len([r for r in records if "_error" in r])
    except Exception as e:
        report.status = "rejected"
        report.rejection_reason = f"File cannot be parsed: {e}"
        return report

    # 2. Schema compliance — do required fields exist?
    error_rate = report.parse_errors / max(len(records), 1)
    max_error_rate = manifest.get("validation", {}).get("reject_if_error_rate_above", 0.20)
    if error_rate > max_error_rate:
        report.status = "rejected"
        report.rejection_reason = f"Error rate {error_rate:.1%} exceeds threshold {max_error_rate:.0%}"
        return report

    # 3. Record count bounds
    min_records = manifest.get("validation", {}).get("min_records", 1)
    max_records = manifest.get("validation", {}).get("max_records", 1_000_000)
    if report.total_records < min_records or report.total_records > max_records:
        report.status = "rejected"
        report.rejection_reason = f"Record count {report.total_records} outside bounds [{min_records}, {max_records}]"
        return report

    # 4. PII scan (if enabled)
    if manifest.get("validation", {}).get("pii_scan", False):
        pii_findings = scan_for_pii(records)
        report.pii_findings = pii_findings
        if pii_findings.has_high_confidence_pii:
            report.data_classification = "contains_pii"
            report.warnings.append("PII detected — see Privacy Framework for handling options")

    # 5. Data quality scoring
    report.quality_scores = compute_quality_scores(records, manifest)

    report.status = "validated"
    return report
```

### Phase 2: Transform & Deduplicate

```python
def transform_and_dedup(
    records: list[dict],
    manifest: dict,
    existing_hashes: set[str],
) -> TransformResult:
    """Normalize records and remove duplicates.

    1. Apply shape normalization ('disc' → 'disk', 'triangular' → 'triangle')
    2. Parse durations ('5 minutes' → 300)
    3. Standardize country codes
    4. Compute dedupe hash
    5. Remove records that already exist in DB (by hash)
    6. Remove intra-file duplicates (keep highest quality record per hash)
    """
    SHAPE_NORMALIZATION = {
        'disc': 'disk', 'saucer': 'disk', 'flying saucer': 'disk',
        'triangular': 'triangle', 'delta': 'triangle', 'v-shaped': 'triangle',
        'spherical': 'sphere', 'ball': 'sphere', 'orb': 'sphere',
        'cylindrical': 'cylinder', 'tube': 'cylinder',
        'rectangular': 'rectangle', 'box': 'rectangle',
        'star-like': 'star', 'point of light': 'light',
        'fireball': 'fireball', 'flash': 'flash',
        'other': 'other', 'unknown': 'unknown', '': 'unknown',
    }

    normalized = []
    new_hashes = set()
    duplicates_removed = 0

    for record in records:
        if "_error" in record:
            continue

        # Normalize shape
        raw_shape = (record.get("shape") or "").lower().strip()
        record["shape"] = SHAPE_NORMALIZATION.get(raw_shape, raw_shape or "unknown")

        # Compute dedupe hash
        hash_input = "|".join([
            str(record.get("date_occurred") or ""),
            str(round(record.get("latitude") or 0, 2)),
            str(round(record.get("longitude") or 0, 2)),
            record.get("shape", "unknown"),
        ])
        record["dedupe_hash"] = hashlib.sha256(hash_input.encode()).hexdigest()

        # Check against existing DB hashes and intra-file duplicates
        if record["dedupe_hash"] in existing_hashes or record["dedupe_hash"] in new_hashes:
            duplicates_removed += 1
            continue

        new_hashes.add(record["dedupe_hash"])
        normalized.append(record)

    return TransformResult(
        records=normalized,
        duplicates_removed=duplicates_removed,
        total_output=len(normalized),
    )
```

### Phase 3: Load into Database

```python
def load_sightings_batch(
    db: Session,
    records: list[dict],
    dataset_id: str,
    batch_size: int = 1000,
) -> LoadResult:
    """Load sightings in batches with transactional safety.

    Key properties:
    - Atomic per batch — if a batch fails, only that batch rolls back
    - Idempotent — re-running with same data skips existing records (by dedupe_hash)
    - Progress tracking — logs after each batch for resumability
    """
    loaded = 0
    skipped = 0
    errors = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            for record in batch:
                # Final uniqueness check (belt-and-suspenders with unique constraint)
                existing = db.query(UFOSighting).filter(
                    UFOSighting.dedupe_hash == record["dedupe_hash"]
                ).first()
                if existing:
                    skipped += 1
                    continue

                sighting = UFOSighting(
                    source_db=record.get("source_db"),
                    source_id=record.get("source_id"),
                    date_occurred=record.get("date_occurred"),
                    date_reported=record.get("date_reported"),
                    city=sanitize_text(record.get("city")),
                    state=sanitize_text(record.get("state")),
                    country=sanitize_text(record.get("country")),
                    latitude=record.get("latitude"),
                    longitude=record.get("longitude"),
                    shape=record.get("shape"),
                    duration_seconds=record.get("duration_seconds"),
                    description=sanitize_text(record.get("description")),
                    summary=sanitize_text(record.get("summary")),
                    source_citation=record.get("source_citation"),
                    dedupe_hash=record["dedupe_hash"],
                    quality_score=record.get("quality_score", 0.0),
                )
                db.add(sighting)
                loaded += 1

            db.commit()
            logger.info(f"Batch {i // batch_size + 1}: loaded {loaded} cumulative")
        except Exception as e:
            db.rollback()
            errors += len(batch)
            logger.error(f"Batch {i // batch_size + 1} failed: {e}")

    return LoadResult(loaded=loaded, skipped=skipped, errors=errors)
```

### Phase 4: Cross-Reference with Entities

Create `data/scripts/link_sightings_to_entities.py`:

```
For each sighting with lat/lon:
  1. Check distance to known facilities (Area 51, Edwards AFB, Dugway, etc.)
     → If within 50 miles, create link (link_type='near_facility', confidence based on distance)
  2. Check date against program timelines (Kona Blue 2008-2012, etc.)
     → If sighting date falls within program dates, create link (link_type='during_program')
  3. Check if reporting agency matches an entity (MUFON, NUFORC, Air Force)
     → Create link (link_type='reported_to_agency', confidence=1.0)
```

---

## Privacy Framework

PRH is local-first, but when datasets are shared across users, privacy becomes critical. This framework follows the **principle of least data** and **privacy by design**.

### 1. Data Classification

Every dataset and field is classified at upload time:

| Classification | Description | Handling |
|---|---|---|
| **public** | No PII, publicly available data (sighting locations, shapes, dates) | Share freely; default for sighting data |
| **contains_pii** | Has names, emails, phone numbers, or precise addresses | PII must be scrubbed or redacted before sharing |
| **sensitive** | Witness identities, unpublished research, NDA-covered data | Never shared; local-only storage |

### 2. PII Detection

Automated scanning of text fields before ingestion:

```python
# backend/ingestion/pii_scanner.py

import re
from typing import List

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone_us": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "street_address": re.compile(r"\b\d{1,5}\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|blvd|court|ct)\b", re.IGNORECASE),
    "person_name_pattern": re.compile(r"\bwitness(?:ed by|:\s*|name:\s*)([\w\s]+)\b", re.IGNORECASE),
}

def scan_for_pii(records: list[dict], text_fields: list[str] = None) -> PIIReport:
    """Scan records for potential PII in text fields.
    
    Returns a report with:
    - findings: list of (field, pattern_type, sample, row_num)
    - has_high_confidence_pii: bool (email, SSN, phone found)
    - has_low_confidence_pii: bool (address patterns, name patterns)
    """
    if text_fields is None:
        text_fields = ["description", "summary", "city", "notes"]

    findings = []
    for record in records:
        for field in text_fields:
            value = record.get(field, "")
            if not value:
                continue
            for pii_type, pattern in PII_PATTERNS.items():
                matches = pattern.findall(str(value))
                if matches:
                    findings.append(PIIFinding(
                        row_num=record.get("_row_num", 0),
                        field=field,
                        pii_type=pii_type,
                        sample=matches[0][:20] + "..." if len(matches[0]) > 20 else matches[0],
                    ))

    high_confidence_types = {"email", "phone_us", "ssn"}
    return PIIReport(
        findings=findings,
        has_high_confidence_pii=any(f.pii_type in high_confidence_types for f in findings),
        has_low_confidence_pii=len(findings) > 0,
    )
```

### 3. PII Scrubbing (for shared datasets)

Before a dataset marked `contains_pii` can be shared, PII is automatically scrubbed:

```python
def scrub_pii(record: dict, pii_findings: list[PIIFinding]) -> dict:
    """Replace detected PII with redaction markers.

    - Emails → [EMAIL REDACTED]
    - Phones → [PHONE REDACTED]
    - SSNs → [SSN REDACTED]
    - Addresses → generalize to city-level (keep city, remove street)
    - Names → [NAME REDACTED]
    """
    scrubbed = record.copy()
    for finding in pii_findings:
        if finding.row_num != record.get("_row_num"):
            continue
        field = finding.field
        value = str(scrubbed.get(field, ""))
        pattern = PII_PATTERNS[finding.pii_type]
        replacement = f"[{finding.pii_type.upper()} REDACTED]"
        scrubbed[field] = pattern.sub(replacement, value)
    return scrubbed
```

### 4. User Identity & Pseudonymity

PRH operates **without user accounts by default** (local-first). When sharing datasets:

- **Owner fingerprint:** A SHA-256 hash of a user-chosen passphrase (never stored plaintext). This provides pseudonymous identity for dataset ownership without requiring accounts.
- **No email collection:** We don't need or store email addresses for dataset sharing.
- **Contributor attribution:** Optional. Users can choose to be credited by name or remain anonymous in shared datasets.
- **Right to deletion:** Dataset owners can delete their shared datasets at any time by proving ownership (re-entering their passphrase to regenerate the fingerprint).

### 5. Network Privacy (for future multi-user features)

- **No telemetry:** PRH never phones home. No analytics, no crash reports, no usage tracking.
- **Local-first sharing:** Initial sharing is via export/import of dataset bundles (`.prh` files). No central server required.
- **Optional peer discovery:** If peer sharing is added later, use zero-knowledge discovery (e.g. hash-based topic channels) so the server never learns what datasets exist.

---

## Security Hardening

Building on PRH's existing security middleware (rate limiting, security headers, input validation), the dataset ingestion system adds defense-in-depth:

### 1. File Upload Security

```python
# All file uploads pass through this gate BEFORE any processing

FILENAME_SANITIZE_PATTERN = re.compile(r'[^\w\-.]')  # Only alphanumeric, hyphens, dots
MAX_FILENAME_LENGTH = 200

def sanitize_filename(filename: str) -> str:
    """Sanitize user-supplied filename to prevent path traversal and injection.

    Rules:
    - Strip directory components (no ../ or absolute paths)
    - Remove null bytes and control characters
    - Replace special characters with underscores
    - Enforce length limit
    - Preserve extension
    """
    if not filename:
        return f"upload_{uuid4().hex[:8]}.csv"

    # Strip path components
    name = Path(filename).name

    # Remove null bytes and control characters
    name = "".join(c for c in name if ord(c) >= 32 and c != '\x7f')

    # Split name and extension
    stem = Path(name).stem
    ext = Path(name).suffix.lower()

    # Sanitize stem
    stem = FILENAME_SANITIZE_PATTERN.sub("_", stem)[:MAX_FILENAME_LENGTH]

    return f"{stem}{ext}" if stem else f"upload_{uuid4().hex[:8]}{ext}"
```

### 2. Content Validation (defense against malicious files)

```python
# Verify file content matches declared type (magic byte check)
MAGIC_BYTES = {
    ".csv": [b"", b"\xef\xbb\xbf"],    # Plain text or UTF-8 BOM
    ".json": [b"{", b"[", b" ", b"\n"],  # JSON starts with object/array
    ".tsv": [b"", b"\xef\xbb\xbf"],
}

def verify_file_content(file_path: Path, declared_ext: str) -> bool:
    """Check that file content matches declared type.

    Prevents attacks where a .csv extension hides a binary payload.
    """
    with open(file_path, "rb") as f:
        header = f.read(4096)

    # Reject binary files (look for null bytes in first 4KB)
    if b"\x00" in header:
        return False

    # For text files, verify it's valid text
    try:
        header.decode("utf-8")
    except UnicodeDecodeError:
        try:
            header.decode("latin-1")
        except UnicodeDecodeError:
            return False

    return True
```

### 3. Input Sanitization for Dataset Content

```python
def sanitize_text(value: str | None, max_length: int = 10_000) -> str | None:
    """Sanitize text fields from user-contributed datasets.

    - Remove null bytes and control characters
    - Strip leading/trailing whitespace
    - Enforce maximum length
    - Remove HTML/script injection attempts
    - Normalize Unicode (NFC)
    """
    if value is None:
        return None

    import unicodedata

    # Remove null bytes and control characters (except newlines/tabs in descriptions)
    cleaned = "".join(c for c in value if ord(c) >= 32 or c in "\n\t")

    # Normalize Unicode to NFC (consistent representation)
    cleaned = unicodedata.normalize("NFC", cleaned)

    # Strip HTML tags (simple pattern — not a full HTML parser)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)

    # Strip common XSS patterns
    cleaned = re.sub(r"javascript:", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"on\w+\s*=", "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()[:max_length] or None
```

### 4. Rate Limiting for Dataset Operations

Extend existing `backend/limiter.py`:

```python
# Dataset-specific rate limits (stricter than general API)
DATASET_RATE_LIMITS = {
    "upload": "5/hour",        # Max 5 dataset uploads per hour per IP
    "validate": "20/hour",     # Max 20 validation requests per hour
    "share": "10/hour",        # Max 10 share operations per hour
    "delete": "10/hour",       # Max 10 delete operations per hour
}
```

### 5. SQL Injection Prevention (reinforced)

The existing `validation.py` handles search sanitization. For dataset ingestion, we add:

- **Parameterized queries only** — SQLAlchemy ORM handles this by default, but explicit auditing ensures no raw SQL concatenation exists in new code.
- **Type coercion** — All user-supplied values are coerced to their declared types (float, int, datetime) before reaching the database. Invalid coercions are logged and skipped, never passed through.
- **Stored text is display-escaped** — When text from user datasets is rendered in the frontend, React's JSX escaping handles XSS prevention. But we also strip HTML on the backend as defense-in-depth.

### 6. Audit Logging

Every dataset operation is logged to `dataset_audit_log`:

```python
def log_dataset_action(
    db: Session,
    dataset_id: str,
    action: str,
    actor_fingerprint: str,
    details: dict = None,
    request: Request = None,
):
    """Log a dataset operation for audit trail.

    Actions: upload, validate, approve, reject, delete, share, unshare, export
    IP is hashed (not stored raw) to enable abuse detection without tracking users.
    """
    ip_hash = None
    if request and request.client:
        ip_hash = hashlib.sha256(request.client.host.encode()).hexdigest()[:16]

    log_entry = DatasetAuditLog(
        dataset_id=dataset_id,
        action=action,
        actor_fingerprint=actor_fingerprint,
        details=json.dumps(details) if details else None,
        ip_hash=ip_hash,
    )
    db.add(log_entry)
    db.commit()
```

---

## Reliability & Data Integrity

### 1. Transactional Safety

- **Batch commits** — Data is loaded in configurable batches (default 1000 rows). Each batch is its own transaction. If a batch fails, only that batch rolls back; previously committed batches are safe.
- **Savepoints** — For particularly large loads (>100K rows), use database savepoints to enable partial rollback within a transaction.
- **Idempotent ingestion** — The `dedupe_hash` unique constraint ensures re-running ingestion with the same data never creates duplicates. This is critical for crash recovery.

### 2. Data Quality Scoring

Every ingested record gets an automated quality score:

```python
def compute_record_quality(record: dict) -> float:
    """Score a sighting record from 0.0 (unusable) to 1.0 (excellent).

    Scoring rubric:
    - Has date_occurred: +0.25
    - Has lat/lon: +0.25
    - Has shape: +0.10
    - Has duration: +0.10
    - Has description (>50 chars): +0.15
    - Has source_id (traceable): +0.10
    - Date is plausible (1900–today): +0.05
    """
    score = 0.0

    if record.get("date_occurred"):
        score += 0.25
        # Plausibility check
        dt = record["date_occurred"]
        if isinstance(dt, datetime) and 1900 <= dt.year <= datetime.now().year:
            score += 0.05

    if record.get("latitude") and record.get("longitude"):
        lat, lon = record["latitude"], record["longitude"]
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            score += 0.25

    if record.get("shape") and record["shape"] != "unknown":
        score += 0.10

    if record.get("duration_seconds") and record["duration_seconds"] > 0:
        score += 0.10

    desc = record.get("description") or ""
    if len(desc) > 50:
        score += 0.15

    if record.get("source_id"):
        score += 0.10

    return min(score, 1.0)
```

### 3. Anomaly Detection & Flagging

Records that look suspicious are automatically flagged for manual review:

```python
ANOMALY_FLAGS = [
    # Geographic anomalies
    ("latitude == 0 and longitude == 0", "Null Island coordinates (likely missing data)"),
    ("abs(latitude) > 90 or abs(longitude) > 180", "Invalid coordinates"),
    # Temporal anomalies
    ("date_occurred > datetime.now()", "Future date"),
    ("date_occurred < datetime(1900, 1, 1)", "Implausibly old date"),
    # Content anomalies
    ("duration_seconds > 86400", "Duration exceeds 24 hours"),
    ("len(description) > 50000", "Unusually long description"),
]
```

### 4. Ingestion Checkpointing & Resume

For large datasets (>100K rows), support **resumable ingestion**:

```python
def get_last_checkpoint(dataset_id: str) -> int:
    """Get the last successfully processed row number for a dataset.
    
    Stored in user_datasets.ingestion_log as JSON:
    {"last_row": 50000, "loaded": 49823, "skipped": 177, "errors": 0}
    """
    ...

def save_checkpoint(dataset_id: str, row_num: int, stats: dict):
    """Save progress checkpoint so ingestion can resume after interruption."""
    ...
```

### 5. Database Performance for Scale

With 500K+ sightings in SQLite:

| Strategy | Implementation |
|---|---|
| **Composite indexes** | `(date_occurred, state)`, `(latitude, longitude)`, `(source_db, source_id)` |
| **Pagination** | All API endpoints use offset/limit (existing pattern, max 1000) |
| **Lazy description loading** | `description` excluded from list queries; fetched only in detail view |
| **FTS5 for text search** | Optional SQLite full-text search index on `summary` + `description` |
| **Connection pooling** | Already implemented (StaticPool for SQLite, QueuePool for PostgreSQL) |
| **Query result caching** | Cache frequently-used aggregates (total counts, shape distribution) with TTL |

---

## User-Contributed Datasets & Sharing

### User Experience Flow

```
1. User clicks "Import Dataset" in Data Explorer
2. Selects a CSV/JSON file from their computer
3. PRH auto-detects column mappings (or user maps them manually)
4. Validation runs: schema check, PII scan, quality scoring
5. User sees validation report with any warnings
6. User confirms import → data loads into their local database
7. (Optional) User clicks "Share with Community" → dataset is exported
   as a .prh bundle and uploaded via GitHub PR to the data repository
```

### Dataset Bundle Format (`.prh`)

For sharing datasets between users, we define a portable bundle format:

```
my_dataset.prh (ZIP archive)
├── manifest.yaml          # Dataset metadata and schema definition
├── data.csv               # The actual data (PII-scrubbed if applicable)
├── validation_report.json # Validation results at time of sharing
├── README.md              # Auto-generated description
└── LICENSE                # Data license declaration
```

### Auto-Detect Column Mappings

To minimize friction for non-technical users:

```python
# backend/ingestion/auto_mapper.py

# Common column name patterns that map to our schema
COLUMN_ALIASES = {
    "date_occurred": ["date", "date_time", "datetime", "date_of_event", "sighting_date",
                      "event_date", "occurred", "date_occurred", "when"],
    "date_reported": ["date_submitted", "date_reported", "reported", "report_date", "posted"],
    "city": ["city", "location_city", "nearest_city"],
    "state": ["state", "state_province", "region", "location_state"],
    "country": ["country", "country_code", "nation", "location_country"],
    "latitude": ["latitude", "lat", "location_latitude"],
    "longitude": ["longitude", "lon", "lng", "location_longitude"],
    "shape": ["shape", "ufo_shape", "object_shape", "craft_shape", "type"],
    "duration_seconds": ["duration", "duration_seconds", "duration_mins", "length"],
    "description": ["description", "text", "narrative", "report", "details", "summary_text"],
    "summary": ["summary", "short_summary", "abstract", "brief"],
}

def auto_detect_mapping(csv_headers: list[str]) -> dict[str, str]:
    """Attempt to auto-map CSV columns to our schema.

    Returns: {csv_column_name: schema_field_name}
    Uses fuzzy matching if exact match fails.
    """
    mapping = {}
    headers_lower = {h: h.lower().strip() for h in csv_headers}

    for schema_field, aliases in COLUMN_ALIASES.items():
        for header, header_lower in headers_lower.items():
            if header_lower in aliases:
                mapping[header] = schema_field
                break

    # For unmapped columns, try fuzzy matching
    unmapped_headers = [h for h in csv_headers if h not in mapping]
    unmapped_fields = [f for f in COLUMN_ALIASES if f not in mapping.values()]

    for header in unmapped_headers:
        best_match = None
        best_score = 0
        for field in unmapped_fields:
            for alias in COLUMN_ALIASES[field]:
                score = _fuzzy_ratio(header.lower(), alias)
                if score > best_score and score > 0.75:
                    best_score = score
                    best_match = field
        if best_match:
            mapping[header] = best_match
            unmapped_fields.remove(best_match)

    return mapping
```

### Sharing via GitHub PR (extends existing contribution system)

The existing `contribute.py` router and `GitHubService` handle individual record contributions. For dataset sharing, we extend this:

```python
# New endpoint: POST /api/datasets/share
async def share_dataset(
    dataset_id: str,
    owner_passphrase: str,          # Used to verify ownership
    license_type: str = "open",
    include_descriptions: bool = True,
    db: Session = Depends(get_db),
    github_token: str = Header(None, alias="X-GitHub-Token"),
):
    """Share a user dataset with the community via GitHub PR.

    Steps:
    1. Verify ownership (passphrase → fingerprint matches dataset owner)
    2. Re-run PII scan on current data
    3. Scrub any detected PII
    4. Package as .prh bundle
    5. Create GitHub PR with the bundle
    6. Log the share action in audit log
    """
    ...
```

### Import from Community

```python
# New endpoint: POST /api/datasets/import-community
async def import_community_dataset(
    prh_bundle: UploadFile,
    db: Session = Depends(get_db),
):
    """Import a .prh bundle from the community repository.

    Steps:
    1. Verify bundle integrity (manifest present, data matches hash)
    2. Re-validate data against manifest schema
    3. Show user a preview (first 10 rows, column mapping, quality stats)
    4. On confirmation, run standard ingestion pipeline
    """
    ...
```

---

## Source-Specific Parsing Notes

### 1. MUFON CMS (CSV)
- **Expected columns:** Case Number, Date Submitted, Date of Event, City, State, Country, Shape, Duration, Summary, Description, Latitude, Longitude
- **Quirks:** Some lat/lon may be approximate (city centroid). Dates in mixed formats.
- **PII risk:** Descriptions may contain witness names or contact info. Run PII scan.
- **License:** DO NOT REDISTRIBUTE — raw files must be gitignored. Only derivatives permitted for personal use.

### 2. UFOCAT-2023 (CSV from Access)
- **Expected columns:** Varies (converted from Access). Likely includes UFOCAT ID, Date, Location, Description, Source, Category.
- **Quirks:** Multi-source aggregation means some fields may be sparse. Check for column name variations.
- **Multiple files** in the Mega folder; main CSV is the case file, supplemental files may have witnesses/sources.
- **PII risk:** Low (academic aggregation), but scan descriptions.

### 3. UPDB.app (CSV from PostgreSQL)
- **Expected columns:** Similar to MUFON/NUFORC since it aggregates them. Check schema from GitHub repo.
- **Quirks:** 336K cases is the largest; expect heavy overlap with MUFON and NUFORC. Dedup is critical.
- **PII risk:** Medium — aggregated from multiple sources.

### 4. Majestic / UFO-Search (JSON)
- **Format:** `majestic.json` — array of objects. Also available as CSV.
- **Expected fields:** date, location, description, source, category.
- **Quirks:** Rich Geldreich's data is open source; may have unique cases not in other databases.
- **PII risk:** Low (curated dataset).
- **Parser note:** Needs JSON parser (use `GenericJSONParser` variant).

### 5. NUFORC Data Bank (CSV)
- **Expected columns:** Date / Time, City, State, Country, Shape, Duration, Summary, Posted, Images
- **Quirks:** Well-structured. Dates are typically "MM/DD/YYYY HH:MM". "Posted" is the NUFORC posting date.
- **PII risk:** Low (summaries are pre-moderated by NUFORC).
- **License:** DO NOT REDISTRIBUTE raw scrape.

---

## Data Directory Structure

```
data/
├── sightings/                          # UFO sighting data
│   ├── raw/                            # Original downloaded files (gitignored)
│   │   ├── mufon_cms_2024.csv
│   │   ├── ufocat_2023.csv
│   │   ├── updb_2023.csv
│   │   ├── majestic.json
│   │   └── nuforc_2024.csv
│   ├── normalized/                     # Parsed to common schema (gitignored)
│   │   ├── mufon_normalized.csv
│   │   ├── ufocat_normalized.csv
│   │   ├── updb_normalized.csv
│   │   ├── majestic_normalized.csv
│   │   └── nuforc_normalized.csv
│   ├── ufo_sightings_deduped.csv       # Final deduplicated dataset
│   └── sighting_entity_links.csv       # Cross-references to entities
├── quarantine/                         # Upload quarantine area (gitignored)
│   └── .gitkeep
├── user_datasets/                      # User-contributed datasets (gitignored)
│   ├── {dataset_uuid}/
│   │   ├── manifest.yaml
│   │   ├── data.csv
│   │   └── validation_report.json
│   └── .gitkeep
└── bundles/                            # Exported .prh bundles for sharing (gitignored)
    └── .gitkeep
```

**`.gitignore` additions:**

```
data/sightings/raw/
data/sightings/normalized/
data/quarantine/
data/user_datasets/
data/bundles/
```

---

## Frontend Integration (future)

Once the data is loaded, the Data Explorer can show:

1. **New Browse tab: "Sightings"** — searchable/filterable table of UFO sightings (date, location, shape, source).
2. **Dashboard stat:** "Total Sightings" card alongside entities, flows, awards.
3. **Dataset Manager page:** List imported datasets, view stats, import/export, share.
4. **Import wizard:** Step-by-step guided import with auto-column-mapping, preview, validation report.
5. **Map view (future):** Leaflet or Mapbox GL showing sighting locations, colored by shape or date.
6. **Entity detail enrichment:** On an entity detail panel (e.g. "Area 51"), show "N sightings within 50 miles" with a mini-timeline.
7. **Pyramid enrichment:** Programs at L6 could show "sighting activity during program timeline."

These are future features; the first milestone is ingestion + dedup + DB load.

---

## Order of Work

### Milestone 1: Infrastructure (1–2 sessions)
1. Add `UFOSighting`, `SightingEntityLink`, `UserDataset`, `DatasetAuditLog` models to `backend/database.py`.
2. Add `data/sightings/`, `data/quarantine/`, `data/user_datasets/` directories and `.gitignore` entries.
3. Create `backend/ingestion/` package:
   - `base_parser.py` — Abstract parser interface
   - `registry.py` — Parser registry
   - `generic_csv_parser.py` — Default CSV parser
   - `normalizers.py` — Shape normalization, duration parsing, date parsing
   - `pii_scanner.py` — PII detection
   - `validators.py` — Schema validation, quality scoring, anomaly detection
4. Create `backend/ingestion/pipeline.py` — Orchestrates quarantine → validate → transform → load.
5. Add `load_ufo_sightings()` to `data_loader.py`.
6. Add sanitization utilities to `backend/validation.py`.

### Milestone 2: Ingest first source — NUFORC (easiest, well-structured)
1. Download NUFORC CSV to `data/sightings/raw/`.
2. Create `backend/ingestion/parsers/nuforc_parser.py` with NUFORC-specific date/shape handling.
3. Create NUFORC `dataset_manifest.yaml`.
4. Run pipeline: quarantine → validate → transform → load. Verify via API.
5. ~148K cases loaded.

### Milestone 3: Ingest MUFON + UFOCAT
1. Download CSVs.
2. Create parsers for each (handle format differences).
3. Run full pipeline: normalize all three → dedup → load.
4. Expect ~300K–400K unique cases after dedup.

### Milestone 4: Ingest UPDB + Majestic
1. Download and parse.
2. UPDB will have heavy overlap; dedup should catch most.
3. Majestic JSON needs a JSON parser variant.
4. Final dataset: estimated **400K–500K unique cases**.

### Milestone 5: Cross-reference with entities
1. Build facility location lookup (lat/lon for Area 51, Edwards, Dugway, etc.).
2. Build program timeline lookup.
3. Run `link_sightings_to_entities.py`.
4. Load links into `sighting_entity_links` table.

### Milestone 6: User Dataset Import (generic framework)
1. Add `POST /api/datasets/upload` endpoint with quarantine flow.
2. Implement auto-column-mapping (`auto_mapper.py`).
3. Add `POST /api/datasets/validate` endpoint.
4. Add `POST /api/datasets/confirm-import` endpoint.
5. Add `GET /api/datasets` and `GET /api/datasets/{id}` endpoints.
6. Add `DELETE /api/datasets/{id}` endpoint with ownership verification.

### Milestone 7: Sharing & Community
1. Implement `.prh` bundle export format.
2. Add `POST /api/datasets/share` endpoint (GitHub PR integration).
3. Add `POST /api/datasets/import-community` endpoint.
4. Frontend: Dataset Manager page with import/export/share controls.

### Milestone 8: API + Frontend (Sightings)
1. Add `/api/sightings` endpoint (search, filter by date/location/shape/source).
2. Add Browse "Sightings" tab.
3. Add Dashboard sighting count.
4. Import wizard UI component.
5. (Future) Map view, entity-detail sighting enrichment.

---

## Dependencies

| Package | Purpose | Already in requirements? |
|---------|---------|------------------------|
| `pandas` | CSV/JSON parsing, dedup | Yes (pandas 2.1.4 in requirements) |
| `geopy` | Distance calculations (facility proximity) | No — add when needed (Milestone 5) |
| `hashlib` | Dedup hashing, file integrity | Built-in |
| `aiofiles` | Async file I/O for uploads | No — add for Milestone 6 |
| `python-magic` | MIME type detection (optional, platform-specific) | No — optional enhancement |
| `rapidfuzz` | Fuzzy column name matching | Yes (already in requirements) |
| `requests` | Download CSVs (optional; user can download manually) | Yes |
| `pyyaml` | Manifest parsing | Yes (via config.yaml loading) |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Redistribution restrictions (MUFON, NUFORC) | Legal | Store raw files in `data/sightings/raw/` (gitignored); only distribute normalized/deduped data if license allows; add LICENSE note per dataset |
| 500K+ rows slow SQLite | Performance | Composite indexes on (date, state), (lat, lon); paginate API; lazy-load descriptions; consider FTS5 for text search |
| Dedup misses or false positives | Data quality | Conservative hash (date + rounded location + shape); quality scoring; manual review flags for edge cases; log dedup stats |
| Column format varies between sources | Parser complexity | One parser per source via registry; shared normalization functions; generic parser as fallback |
| Large CSV files (100MB+) | Memory | Streaming parsers (`csv.DictReader`); batch database inserts; quarantine with size limits |
| PII in witness descriptions | Privacy | Automated PII scanning before ingestion; scrubbing before sharing; classification labels on datasets |
| Malicious file uploads | Security | Extension whitelist; MIME validation; binary content rejection; quarantine directory; size limits; filename sanitization |
| Injection via dataset content | Security | Text sanitization on all string fields; parameterized SQL only; type coercion; HTML stripping |
| Data corruption during large loads | Reliability | Batch transactions with rollback; idempotent inserts via dedupe_hash; checkpointing for resume |
| Users sharing copyrighted data | Legal | License field on datasets; manifest declares license; disclaimer on share screen; community review via GitHub PR |

---

## Open Questions

1. **Should raw sighting CSVs be committed to the repo?** Recommendation: No (too large, redistribution issues). Users download them manually into `data/sightings/raw/` or we provide a download script.
2. **Should we store the full witness description?** Pro: enables text search. Con: large (~100 bytes average x 500K = 50MB in DB). Recommendation: Store it but make it nullable and exclude from default API responses (lazy loading).
3. **Should the sightings data be in the same SQLite DB (`prh.db`) or a separate one?** Recommendation: Same DB for simplicity; add indexes to keep queries fast. If performance becomes an issue, split later.
4. **Priority order of sources?** Recommendation: NUFORC first (cleanest, well-structured), then MUFON, UFOCAT, UPDB, Majestic.
5. **Should dataset sharing go through GitHub PRs or a separate channel?** Recommendation: Start with GitHub PRs (consistent with existing contribution system). Consider a lightweight community server later if adoption grows.
6. **Should we support datasets beyond UFO sightings?** The plugin architecture is generic enough to support any tabular data. Recommendation: Build the sightings pipeline first, then generalize the schema mapping to support entities, money flows, and other PRH data types.
7. **How should we handle dataset versioning?** When a user re-imports an updated version of their dataset, should it overwrite or create a new version? Recommendation: Create a new version with a migration path (diff the old and new, let user confirm changes).
