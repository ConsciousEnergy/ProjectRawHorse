"""
Data reconciliation endpoint: compare current DB state against
the last pipeline manifest for integrity checks.

Endpoints:
- /report: Generates a reconciliation report with counts, deltas, and anomalies.
"""
import os
import json
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Entity, MoneyFlow, Award, Relationship, TimelineEvent
from dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "data", "pipeline_manifest.json")


def _load_manifest() -> dict:
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/report")
async def get_reconciliation_report(db: Session = Depends(get_db)):
    """Compare current DB state against last pipeline manifest."""
    manifest = _load_manifest()
    manifest_files = manifest.get("canonical_files", {})

    db_counts = {
        "entities": db.query(Entity).count(),
        "money_flows": db.query(MoneyFlow).count(),
        "awards": db.query(Award).count(),
        "relationships": db.query(Relationship).count(),
        "timeline_events": db.query(TimelineEvent).count(),
    }

    total_money = db.query(func.sum(MoneyFlow.amount_usd)).scalar() or 0

    confidence_breakdown = {}
    for tier in ["confirmed", "corroborated", "contested"]:
        confidence_breakdown[tier] = (
            db.query(TimelineEvent)
            .filter(TimelineEvent.confidence_tier == tier)
            .count()
        )

    anomalies = []
    for csv_name, csv_info in manifest_files.items():
        manifest_count = csv_info.get("row_count", 0)
        if "entities" in csv_name and manifest_count > 0:
            delta = abs(db_counts["entities"] - manifest_count) / max(manifest_count, 1)
            if delta > 0.2:
                anomalies.append(f"Entity count delta {delta:.0%} vs manifest ({db_counts['entities']} vs {manifest_count})")
        if "money_flows" in csv_name and manifest_count > 0:
            delta = abs(db_counts["money_flows"] - manifest_count) / max(manifest_count, 1)
            if delta > 0.2:
                anomalies.append(f"Money flow count delta {delta:.0%} vs manifest")

    return {
        "db_counts": db_counts,
        "total_money_usd": float(total_money),
        "timeline_confidence_breakdown": confidence_breakdown,
        "manifest_present": bool(manifest),
        "manifest_run": manifest.get("pipeline_run", {}),
        "anomalies": anomalies,
    }
