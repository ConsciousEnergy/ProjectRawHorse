"""
Timeline API routes for historical events (1933 -> present).

Endpoints:
- /events: Paginated event list with filters (category, confidence, date range, search).
- /events/{event_id}: Single event detail with source citations.
- /buckets: Time-bucket aggregates (by decade or year) for chart rendering.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from collections import defaultdict

from database import TimelineEvent, TimelineSource
from models.schemas import (
    TimelineEventSchema, TimelineSourceSchema,
    TimelineEventListResponse, TimelineBucket,
)
from validation import sanitize_search, MAX_SEARCH_LENGTH
from dependencies import get_db

router = APIRouter()

VALID_CONFIDENCE_TIERS = {"confirmed", "corroborated", "contested"}
VALID_CATEGORIES = {
    "crash_retrieval", "legislation", "disclosure", "military",
    "scientific", "whistleblower", "organizational", "sighting",
}


def _event_with_sources(event: TimelineEvent, db: Session) -> TimelineEventSchema:
    sources = db.query(TimelineSource).filter(TimelineSource.event_id == event.event_id).all()
    return TimelineEventSchema(
        event_id=event.event_id,
        event_date=event.event_date,
        date_precision=event.date_precision or "exact",
        title=event.title,
        summary=event.summary,
        category=event.category,
        region=event.region,
        confidence_tier=event.confidence_tier,
        related_entities=event.related_entities,
        sources=[
            TimelineSourceSchema(
                source_type=s.source_type,
                source_title=s.source_title,
                source_url=s.source_url,
                source_date=s.source_date,
                notes=s.notes,
            )
            for s in sources
        ],
    )


@router.get("/events", response_model=TimelineEventListResponse)
async def list_timeline_events(
    category: Optional[str] = Query(None, max_length=50),
    confidence: Optional[str] = Query(None, max_length=20),
    search: Optional[str] = Query(None, max_length=MAX_SEARCH_LENGTH),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Paginated timeline events with optional filters."""
    query = db.query(TimelineEvent)

    if category and category in VALID_CATEGORIES:
        query = query.filter(TimelineEvent.category == category)
    if confidence and confidence in VALID_CONFIDENCE_TIERS:
        query = query.filter(TimelineEvent.confidence_tier == confidence)
    if search:
        search = sanitize_search(search)
        if search:
            term = f"%{search}%"
            query = query.filter(
                TimelineEvent.title.ilike(term) | TimelineEvent.summary.ilike(term)
            )
    if start_year:
        query = query.filter(extract("year", TimelineEvent.event_date) >= start_year)
    if end_year:
        query = query.filter(extract("year", TimelineEvent.event_date) <= end_year)

    total = query.count()
    events_raw = (
        query.order_by(TimelineEvent.event_date.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    events = [_event_with_sources(e, db) for e in events_raw]
    return TimelineEventListResponse(total=total, page=page, page_size=page_size, events=events)


@router.get("/events/{event_id}", response_model=TimelineEventSchema)
async def get_timeline_event(event_id: str, db: Session = Depends(get_db)):
    """Single event detail with all source citations."""
    event = db.query(TimelineEvent).filter(TimelineEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return _event_with_sources(event, db)


@router.get("/buckets", response_model=List[TimelineBucket])
async def get_timeline_buckets(
    bucket_size: str = Query("decade", regex="^(decade|year)$"),
    db: Session = Depends(get_db),
):
    """Aggregate event counts by time bucket for chart rendering."""
    events = db.query(TimelineEvent).all()
    buckets: dict = defaultdict(lambda: {"count": 0, "categories": defaultdict(int), "confidence": defaultdict(int)})

    for e in events:
        if not e.event_date:
            continue
        year = e.event_date.year
        if bucket_size == "decade":
            key = f"{(year // 10) * 10}s"
        else:
            key = str(year)
        buckets[key]["count"] += 1
        if e.category:
            buckets[key]["categories"][e.category] += 1
        buckets[key]["confidence"][e.confidence_tier] += 1

    result = []
    for period in sorted(buckets.keys()):
        b = buckets[period]
        result.append(TimelineBucket(
            period=period,
            count=b["count"],
            categories=dict(b["categories"]),
            confidence_breakdown=dict(b["confidence"]),
        ))
    return result
