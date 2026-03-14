"""
CSV schema validation gate for money-flow and entity data pipelines.

Validates canonical CSVs before DB load: required columns, types, null thresholds,
row-count minimums, and duplicate key checks. Fails fast with diagnostics.

Usage:
    python validate_csv_schema.py [--data-dir ../../data]
"""
import os
import sys
import csv
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCHEMAS: Dict[str, dict] = {
    "entities_master.csv": {
        "required_columns": ["entity_id", "display_name", "entity_type"],
        "unique_key": "entity_id",
        "min_rows": 10,
        "max_null_pct": {"entity_id": 0, "display_name": 0},
    },
    "money_flows.csv": {
        "required_columns": ["source", "target"],
        "unique_key": "edge_id",
        "min_rows": 5,
        "max_null_pct": {"source": 0, "target": 0},
        "numeric_columns": ["amount_usd"],
    },
    "awards_master.csv": {
        "required_columns": ["recipient_name", "awarding_agency"],
        "unique_key": "piid",
        "min_rows": 5,
        "max_null_pct": {"recipient_name": 0.05},
        "numeric_columns": ["award_amount"],
    },
    "entity_relationships.csv": {
        "required_columns": ["source", "target", "label"],
        "min_rows": 5,
        "max_null_pct": {"source": 0, "target": 0, "label": 0},
    },
}


def validate_file(filepath: str, schema: dict) -> List[str]:
    errors: List[str] = []
    if not os.path.exists(filepath):
        errors.append(f"File not found: {filepath}")
        return errors

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        for col in schema.get("required_columns", []):
            if col not in headers:
                errors.append(f"Missing required column: {col}")

        if errors:
            return errors

        rows = list(reader)

    row_count = len(rows)
    min_rows = schema.get("min_rows", 1)
    if row_count < min_rows:
        errors.append(f"Row count {row_count} below minimum {min_rows}")

    for col, max_pct in schema.get("max_null_pct", {}).items():
        null_count = sum(1 for r in rows if not (r.get(col) or "").strip())
        pct = null_count / max(row_count, 1)
        if pct > max_pct:
            errors.append(f"Column '{col}' null rate {pct:.1%} exceeds threshold {max_pct:.0%}")

    unique_key = schema.get("unique_key")
    if unique_key and unique_key in headers:
        keys = [r.get(unique_key, "").strip() for r in rows if r.get(unique_key, "").strip()]
        dupes = len(keys) - len(set(keys))
        if dupes > 0:
            errors.append(f"Duplicate key '{unique_key}': {dupes} duplicates found")

    for col in schema.get("numeric_columns", []):
        if col not in headers:
            continue
        bad = 0
        for r in rows:
            val = (r.get(col) or "").strip()
            if val:
                try:
                    float(val.replace(",", ""))
                except ValueError:
                    bad += 1
        if bad > 0:
            errors.append(f"Column '{col}' has {bad} non-numeric values")

    return errors


def validate_all(data_dir: str) -> bool:
    all_ok = True
    entities_dir = os.path.join(data_dir, "entities")
    financial_dir = os.path.join(data_dir, "financial")

    file_map = {
        "entities_master.csv": os.path.join(entities_dir, "entities_master.csv"),
        "entity_relationships.csv": os.path.join(entities_dir, "entity_relationships.csv"),
        "money_flows.csv": os.path.join(financial_dir, "money_flows.csv"),
        "awards_master.csv": os.path.join(financial_dir, "awards_master.csv"),
    }

    for name, schema in SCHEMAS.items():
        filepath = file_map.get(name)
        if not filepath:
            continue
        errors = validate_file(filepath, schema)
        if errors:
            all_ok = False
            logger.error(f"FAIL: {name}")
            for e in errors:
                logger.error(f"  - {e}")
        else:
            logger.info(f"PASS: {name}")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Validate canonical CSV schemas before DB load")
    parser.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__), "..", "..","data"))
    args = parser.parse_args()

    data_dir = os.path.abspath(args.data_dir)
    logger.info(f"Validating CSVs in: {data_dir}")

    if validate_all(data_dir):
        logger.info("All validations passed.")
        sys.exit(0)
    else:
        logger.error("Validation failed. Fix errors before loading into DB.")
        sys.exit(1)


if __name__ == "__main__":
    main()
