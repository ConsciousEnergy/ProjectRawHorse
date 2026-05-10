"""
Offline import service for CSV/JSON datasets.
Provides validation preview (dry run) and optional commit mode.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from database import Award, Entity, FOIATarget, Relationship

SUPPORTED_TYPES = {"entities", "relationships", "contracts", "foia"}

TEMPLATES: Dict[str, List[str]] = {
    "entities": ["entity_id", "display_name", "normalized_name", "entity_type", "intel_stack_level"],
    "relationships": ["source", "target", "label", "description", "relationship_type", "source_citation"],
    "contracts": ["piid", "recipient_name", "awarding_agency", "funding_agency", "award_amount", "action_date", "description"],
    "foia": [
        "agency",
        "record_request",
        "timeframe",
        "status",
        "submitted_at",
        "response_due_at",
        "estimated_cost",
        "reference_url",
        "archive_url",
        "notes",
    ],
}


def get_template_columns(data_type: str) -> List[str]:
    return TEMPLATES.get(data_type, [])


def parse_uploaded_rows(file_bytes: bytes, filename: str, data_type: str) -> List[Dict[str, Any]]:
    if data_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported data_type: {data_type}")

    lower_name = filename.lower()
    text = file_bytes.decode("utf-8-sig")
    if lower_name.endswith(".json"):
        payload = json.loads(text)
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        raise ValueError("JSON import requires an array of objects.")

    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def _as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_date(value: Any):
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def validate_and_import_rows(
    db: Session,
    data_type: str,
    rows: List[Dict[str, Any]],
    *,
    dry_run: bool = True,
) -> Dict[str, Any]:
    errors: List[str] = []
    valid_rows: List[Dict[str, Any]] = []
    inserted = 0
    skipped = 0

    for idx, row in enumerate(rows, start=1):
        line = f"row {idx}"
        try:
            if data_type == "entities":
                entity_id = (row.get("entity_id") or "").strip()
                display_name = (row.get("display_name") or "").strip()
                normalized_name = (row.get("normalized_name") or "").strip()
                if not entity_id or not display_name or not normalized_name:
                    errors.append(f"{line}: entities require entity_id, display_name, normalized_name")
                    continue
                payload = {
                    "entity_id": entity_id,
                    "display_name": display_name,
                    "normalized_name": normalized_name,
                    "entity_type": row.get("entity_type") or None,
                    "intel_stack_level": _as_int(row.get("intel_stack_level")),
                }
                valid_rows.append(payload)
                if dry_run:
                    continue
                exists = db.query(Entity).filter(Entity.entity_id == entity_id).first()
                if exists:
                    skipped += 1
                    continue
                db.add(Entity(**payload))
                inserted += 1
                continue

            if data_type == "relationships":
                source = (row.get("source") or "").strip()
                target = (row.get("target") or "").strip()
                label = (row.get("label") or "").strip()
                if not source or not target or not label:
                    errors.append(f"{line}: relationships require source, target, label")
                    continue
                payload = {
                    "source": source,
                    "target": target,
                    "label": label,
                    "description": row.get("description") or None,
                    "relationship_type": row.get("relationship_type") or None,
                    "source_citation": row.get("source_citation") or None,
                    "start_date": _as_date(row.get("start_date")),
                    "end_date": _as_date(row.get("end_date")),
                }
                valid_rows.append(payload)
                if dry_run:
                    continue
                exists = db.query(Relationship).filter(
                    Relationship.source == source,
                    Relationship.target == target,
                    Relationship.label == label,
                ).first()
                if exists:
                    skipped += 1
                    continue
                db.add(Relationship(**payload))
                inserted += 1
                continue

            if data_type == "contracts":
                recipient_name = (row.get("recipient_name") or "").strip()
                agency = (row.get("awarding_agency") or "").strip()
                if not recipient_name or not agency:
                    errors.append(f"{line}: contracts require recipient_name and awarding_agency")
                    continue
                payload = {
                    "piid": row.get("piid") or None,
                    "recipient_name": recipient_name,
                    "awarding_agency": agency,
                    "funding_agency": row.get("funding_agency") or None,
                    "award_amount": _as_float(row.get("award_amount")),
                    "action_date": _as_date(row.get("action_date")),
                    "description": row.get("description") or None,
                }
                valid_rows.append(payload)
                if dry_run:
                    continue
                db.add(Award(**payload))
                inserted += 1
                continue

            if data_type == "foia":
                agency = (row.get("agency") or "").strip()
                record_request = (row.get("record_request") or "").strip()
                if not agency or not record_request:
                    errors.append(f"{line}: foia requires agency and record_request")
                    continue
                payload = {
                    "agency": agency,
                    "record_request": record_request,
                    "timeframe": row.get("timeframe") or None,
                    "status": (row.get("status") or "draft").strip().lower(),
                    "submitted_at": _as_date(row.get("submitted_at")),
                    "response_due_at": _as_date(row.get("response_due_at")),
                    "responded_at": _as_date(row.get("responded_at")),
                    "estimated_cost": _as_float(row.get("estimated_cost")),
                    "actual_cost": _as_float(row.get("actual_cost")),
                    "is_overdue": str(row.get("is_overdue") or "").strip().lower() == "true",
                    "reference_url": row.get("reference_url") or None,
                    "archive_url": row.get("archive_url") or None,
                    "notes": row.get("notes") or None,
                }
                valid_rows.append(payload)
                if dry_run:
                    continue
                exists = db.query(FOIATarget).filter(
                    FOIATarget.agency == agency,
                    FOIATarget.record_request == record_request,
                ).first()
                if exists:
                    skipped += 1
                    continue
                db.add(FOIATarget(**payload))
                inserted += 1
                continue

        except Exception as exc:  # pragma: no cover - defensive guard clause
            errors.append(f"{line}: {exc}")

    if not dry_run:
        db.commit()

    return {
        "data_type": data_type,
        "total_rows": len(rows),
        "valid_rows": len(valid_rows),
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors[:200],
        "preview": valid_rows[:25],
        "dry_run": dry_run,
    }
