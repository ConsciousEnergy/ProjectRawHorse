"""
Validate simulation confidence CSV schema and values.
"""
import csv
import os
import sys

REQUIRED_COLUMNS = [
    "subject_type",
    "subject_id",
    "confidence_score",
    "confidence_tier",
    "evidence_refs",
    "effective_start_date",
    "effective_end_date",
    "notes",
]

VALID_SUBJECT_TYPES = {"entity", "money_flow", "relationship", "event"}
VALID_TIERS = {"confirmed", "corroborated", "contested"}


def main() -> int:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(project_root, "data", "simulation", "re_cr_confidence.csv")
    if not os.path.exists(csv_path):
        print(f"ERROR: Missing simulation dataset: {csv_path}")
        return 1

    errors = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        if missing:
            errors.append(f"Missing columns: {missing}")
        for idx, row in enumerate(reader, start=2):
            st = (row.get("subject_type") or "").strip().lower()
            sid = (row.get("subject_id") or "").strip()
            tier = (row.get("confidence_tier") or "").strip().lower()
            score_raw = (row.get("confidence_score") or "").strip()
            if st not in VALID_SUBJECT_TYPES:
                errors.append(f"Line {idx}: invalid subject_type '{st}'")
            if not sid:
                errors.append(f"Line {idx}: subject_id is required")
            if tier and tier not in VALID_TIERS:
                errors.append(f"Line {idx}: invalid confidence_tier '{tier}'")
            try:
                score = float(score_raw)
                if score < 0.0 or score > 1.0:
                    errors.append(f"Line {idx}: confidence_score out of range [0,1]")
            except ValueError:
                errors.append(f"Line {idx}: confidence_score must be numeric")

    if errors:
        print("Simulation schema validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Simulation schema validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
