# Confidence Tier Policy

## Tier Definitions

### Confirmed
Event or relationship is backed by **official government records, signed legislation, or officially released documentation**.

Minimum evidence:
- At least one primary source from a government body, official publication, or verified legal record
- Date, location, and key facts independently verifiable

Examples: Congressional hearings, signed legislation, officially released videos, FOIA documents

### Corroborated
Event is supported by **multiple independent sources** but lacks primary official documentation.

Minimum evidence:
- At least two independent sources (journalism, witness testimony, leaked documents)
- Sources must be from different organizations or individuals
- Timeline and key claims are internally consistent

Examples: Multiple investigative journalists reporting the same program, multiple witnesses with consistent accounts, documents that are not officially released but are corroborated by named officials

### Contested
Event is reported but has **significant disagreement among sources**, or evidence is limited to a single unverified account.

Minimum evidence:
- At least one published source (not anonymous social media)
- Clearly labeled as contested with reason noted

Examples: Single-witness accounts, claims disputed by official investigations, events with conflicting timelines

## Tier Governance Process

### Assignment
- Initial tier assigned by data contributor based on evidence provided
- Tier must be justified with at least one linked citation (timeline_sources)

### Upgrade (e.g., contested → corroborated)
- New evidence must be added (additional citation)
- Change must be documented in audit log
- Previous tier preserved in event history

### Downgrade (e.g., confirmed → contested)
- Requires documented reason (source retraction, contradicting evidence)
- Must be accompanied by explanatory note
- Protected against casual modification (admin-only when auth is enabled)

## Provenance Requirements

Every analytic artifact (entity placement, money flow, timeline event) must carry:
- `source_citation`: URL or document reference
- `retrieval_time`: When the data was collected (for pipeline runs: pipeline_manifest.json)
- `transform_version`: Which script version processed it (checksum in manifest)

## Reconciliation

After each data refresh cycle:
1. Generate delta report (new entities, modified flows, changed tiers)
2. Flag anomalies (>20% change in entity count, tier downgrades)
3. Pipeline manifest captures checksums for reproducibility

## RE/CR Simulation Confidence Mapping

For simulation timeline overlays (`/api/simulation/*`), confidence is represented with:

- `confidence_score` in range `[0.0, 1.0]`
- `confidence_tier` in `{confirmed, corroborated, contested}`
- `effective_start_date` and `effective_end_date` for temporal validity
- `evidence_refs` for source traceability

Recommended score-to-tier defaults:

- `>= 0.80` -> `confirmed`
- `>= 0.50 and < 0.80` -> `corroborated`
- `< 0.50` -> `contested`

Governance rules:

1. Every record used to render high-confidence simulation links must include at least one evidence reference.
2. Expired mappings (`effective_end_date` in past) should be excluded from active confidence filtering.
3. Updates must preserve historical auditability (new evidence preferred over destructive replacement).
