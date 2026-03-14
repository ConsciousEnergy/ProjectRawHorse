"""
Contribution API routes — database-first public submissions with admin review queue.

Public users submit via POST /contribute/submit (no GitHub token needed).
Admins review via GET /contribute/queue and POST /contribute/{id}/review.
"""
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import (
    PendingContribution, Entity, MoneyFlow, Award, FOIATarget,
)
from dependencies import get_db
from models.schemas import (
    ContributionSubmitRequest,
    ContributionRecord,
    ContributionListResponse,
    ContributionReviewRequest,
    ContributionResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_DATA_PAYLOAD_KEYS = 30
MAX_FIELD_LENGTH = 5000


def _sanitize_payload(data: dict) -> dict:
    """Basic guard against oversized or malicious payloads."""
    if len(data) > MAX_DATA_PAYLOAD_KEYS:
        raise HTTPException(status_code=422, detail=f"Payload exceeds {MAX_DATA_PAYLOAD_KEYS} fields")
    sanitized = {}
    for k, v in data.items():
        if isinstance(v, str) and len(v) > MAX_FIELD_LENGTH:
            raise HTTPException(status_code=422, detail=f"Field '{k}' exceeds max length ({MAX_FIELD_LENGTH})")
        sanitized[str(k)] = v
    return sanitized


@router.post("/submit", response_model=ContributionResponse)
async def submit_contribution(
    body: ContributionSubmitRequest,
    db: Session = Depends(get_db),
):
    """Public endpoint — submit a data contribution for admin review.
    No GitHub token required. Data is stored as pending until reviewed."""
    sanitized = _sanitize_payload(body.data)

    record = PendingContribution(
        contribution_type=body.contribution_type,
        status="pending",
        data_json=json.dumps(sanitized, default=str),
        contributor_name=body.contributor_name,
        contributor_email=body.contributor_email,
        notes=body.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Contribution #%s (%s) submitted", record.id, body.contribution_type)

    return ContributionResponse(
        success=True,
        message=f"Contribution #{record.id} submitted for review. Thank you!",
    )


@router.get("/queue", response_model=ContributionListResponse)
async def list_contributions(
    status: str = Query("pending", pattern="^(pending|approved|rejected|all)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Admin endpoint — list contributions by status."""
    query = db.query(PendingContribution)
    if status != "all":
        query = query.filter(PendingContribution.status == status)
    total = query.count()
    rows = query.order_by(PendingContribution.submitted_at.desc()).offset(skip).limit(limit).all()

    contributions = []
    for r in rows:
        contributions.append(ContributionRecord(
            id=r.id,
            contribution_type=r.contribution_type,
            status=r.status,
            data=json.loads(r.data_json),
            contributor_name=r.contributor_name,
            notes=r.notes,
            submitted_at=r.submitted_at,
            reviewed_at=r.reviewed_at,
            reviewed_by=r.reviewed_by,
            review_notes=r.review_notes,
        ))

    return ContributionListResponse(total=total, contributions=contributions)


@router.post("/{contribution_id}/review", response_model=ContributionResponse)
async def review_contribution(
    contribution_id: int,
    body: ContributionReviewRequest,
    db: Session = Depends(get_db),
):
    """Admin endpoint — approve or reject a pending contribution.
    Approved contributions are merged into the canonical DB tables."""
    record = db.query(PendingContribution).filter(PendingContribution.id == contribution_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Contribution not found")
    if record.status != "pending":
        raise HTTPException(status_code=409, detail=f"Contribution already {record.status}")

    record.status = body.action + "d"  # "approved" or "rejected"
    record.reviewed_at = datetime.utcnow()
    record.reviewed_by = "admin"
    record.review_notes = body.review_notes

    if body.action == "approve":
        try:
            _merge_into_canonical(db, record)
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Merge failed: {exc}")

    db.commit()
    logger.info("Contribution #%s %s", contribution_id, record.status)

    return ContributionResponse(
        success=True,
        message=f"Contribution #{contribution_id} {record.status}.",
    )


def _merge_into_canonical(db: Session, record: PendingContribution):
    """Insert approved contribution data into the matching canonical table."""
    data = json.loads(record.data_json)
    ctype = record.contribution_type

    if ctype == "entity":
        entity = Entity(
            entity_id=data.get("entity_id", ""),
            display_name=data.get("display_name", ""),
            normalized_name=data.get("normalized_name", data.get("display_name", "")).lower(),
            entity_type=data.get("entity_type"),
        )
        db.add(entity)

    elif ctype == "money_flow":
        flow = MoneyFlow(
            source=data.get("source", ""),
            target=data.get("target", ""),
            relationship=data.get("relationship"),
            amount_usd=float(data["amount_usd"]) if data.get("amount_usd") else None,
            source_citation=data.get("source_citation"),
        )
        db.add(flow)

    elif ctype == "award":
        award = Award(
            piid=data.get("award_id"),
            recipient_name=data.get("recipient_name"),
            awarding_agency=data.get("awarding_agency"),
            award_amount=float(data["award_amount"]) if data.get("award_amount") else None,
            description=data.get("description"),
        )
        db.add(award)

    elif ctype == "foia_target":
        foia = FOIATarget(
            agency=data.get("agency", ""),
            record_request=data.get("topic", ""),
            relevance=data.get("priority"),
            notes=data.get("notes"),
        )
        db.add(foia)

    else:
        raise ValueError(f"Unknown contribution type: {ctype}")
