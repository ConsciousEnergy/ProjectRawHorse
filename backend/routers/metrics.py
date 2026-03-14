"""
Operational metrics endpoint for monitoring dashboards.

Provides:
- Request counts and latency summaries (from in-memory counters)
- Database table counts
- Error rate snapshots
- System resource info
"""
import time
import logging
from collections import defaultdict
from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Entity, MoneyFlow, Award, Relationship, TimelineEvent, FOIATarget, AuditLog
from dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

_request_counts: Dict[str, int] = defaultdict(int)
_error_counts: Dict[str, int] = defaultdict(int)
_latency_samples: Dict[str, list] = defaultdict(list)
_start_time = time.time()

MAX_SAMPLES = 1000


def record_request(path: str, status_code: int, duration_ms: float):
    """Called by middleware to record request metrics."""
    _request_counts[path] += 1
    if status_code >= 400:
        _error_counts[path] += 1
    samples = _latency_samples[path]
    samples.append(duration_ms)
    if len(samples) > MAX_SAMPLES:
        _latency_samples[path] = samples[-MAX_SAMPLES:]


@router.get("/summary")
async def get_metrics_summary(db: Session = Depends(get_db)):
    """Operational metrics summary for monitoring dashboards."""
    uptime_sec = round(time.time() - _start_time, 0)

    db_counts = {
        "entities": db.query(Entity).count(),
        "money_flows": db.query(MoneyFlow).count(),
        "awards": db.query(Award).count(),
        "relationships": db.query(Relationship).count(),
        "timeline_events": db.query(TimelineEvent).count(),
        "foia_targets": db.query(FOIATarget).count(),
        "audit_log_entries": db.query(AuditLog).count(),
    }

    total_requests = sum(_request_counts.values())
    total_errors = sum(_error_counts.values())
    error_rate = total_errors / max(total_requests, 1)

    all_latencies = []
    for samples in _latency_samples.values():
        all_latencies.extend(samples)
    all_latencies.sort()

    latency_stats = {}
    if all_latencies:
        latency_stats = {
            "p50_ms": all_latencies[len(all_latencies) // 2],
            "p95_ms": all_latencies[int(len(all_latencies) * 0.95)],
            "p99_ms": all_latencies[int(len(all_latencies) * 0.99)],
            "max_ms": all_latencies[-1],
        }

    top_endpoints = sorted(_request_counts.items(), key=lambda x: -x[1])[:10]
    top_errors = sorted(_error_counts.items(), key=lambda x: -x[1])[:10]

    return {
        "uptime_seconds": uptime_sec,
        "db_counts": db_counts,
        "traffic": {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 4),
        },
        "latency": latency_stats,
        "top_endpoints": [{"path": p, "count": c} for p, c in top_endpoints],
        "top_errors": [{"path": p, "count": c} for p, c in top_errors],
    }
