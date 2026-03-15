"""
Simulation timeline API routes.

Provides a unified temporal contract for events, flows, entities, and connections
with deterministic sorting, pagination, and confidence-aware filtering.
"""
import json
from collections import defaultdict
from datetime import date
from typing import Optional, List, Dict, Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from dependencies import get_db
from database import TimelineEvent, TimelineSource, MoneyFlow, Entity, Relationship, ReCrConfidence
from models.schemas import (
    SimulationTimelineResponse,
    SimulationEventItem,
    SimulationFlowItem,
    SimulationEntityItem,
    SimulationConnectionItem,
    SimulationMeta,
    TimelineSourceSchema,
)

router = APIRouter()

VALID_GROUP_BY = {"year", "decade"}
VALID_TIERS = {"confirmed", "corroborated", "contested"}


def _parse_related_entities(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
    return [x.strip() for x in raw.split(",") if x.strip()]


def _parse_evidence_refs(raw: Optional[str]) -> str:
    if not raw:
        return ""
    return raw.strip()


def _confidence_map(
    db: Session,
    confidence_min: Optional[float],
    active_on: Optional[date],
) -> Dict[Tuple[str, str], ReCrConfidence]:
    query = db.query(ReCrConfidence)
    if confidence_min is not None:
        query = query.filter(ReCrConfidence.confidence_score >= confidence_min)
    if active_on:
        query = query.filter(
            and_(
                func.coalesce(ReCrConfidence.effective_start_date, active_on) <= active_on,
                func.coalesce(ReCrConfidence.effective_end_date, active_on) >= active_on,
            )
        )
    rows = query.order_by(
        ReCrConfidence.subject_type.asc(),
        ReCrConfidence.subject_id.asc(),
        ReCrConfidence.updated_at.desc(),
    ).all()
    result: Dict[Tuple[str, str], ReCrConfidence] = {}
    for row in rows:
        key = (row.subject_type, row.subject_id)
        if key not in result:
            result[key] = row
    return result


@router.get("/timeline", response_model=SimulationTimelineResponse)
async def get_simulation_timeline(
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    category: Optional[List[str]] = Query(None),
    entity_id: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    group_by: str = Query("year", pattern="^(year|decade)$"),
    db: Session = Depends(get_db),
):
    if group_by not in VALID_GROUP_BY:
        group_by = "year"

    offset = (page - 1) * page_size
    conf = _confidence_map(db, confidence_min=confidence_min, active_on=None)

    event_query = db.query(TimelineEvent)
    if start_year:
        event_query = event_query.filter(func.extract("year", TimelineEvent.event_date) >= start_year)
    if end_year:
        event_query = event_query.filter(func.extract("year", TimelineEvent.event_date) <= end_year)
    if category:
        event_query = event_query.filter(TimelineEvent.category.in_(category))

    event_total = event_query.count()
    event_rows = event_query.order_by(TimelineEvent.event_date.asc(), TimelineEvent.event_id.asc()).offset(offset).limit(page_size).all()

    event_ids = [e.event_id for e in event_rows]
    sources_by_event: Dict[str, List[TimelineSourceSchema]] = defaultdict(list)
    if event_ids:
        source_rows = db.query(TimelineSource).filter(TimelineSource.event_id.in_(event_ids)).order_by(TimelineSource.event_id.asc(), TimelineSource.id.asc()).all()
        for s in source_rows:
            sources_by_event[s.event_id].append(
                TimelineSourceSchema(
                    source_type=s.source_type,
                    source_title=s.source_title,
                    source_url=s.source_url,
                    source_date=s.source_date,
                    notes=s.notes,
                )
            )

    events: List[SimulationEventItem] = []
    for e in event_rows:
        c = conf.get(("event", e.event_id))
        events.append(
            SimulationEventItem(
                event_id=e.event_id,
                event_date=e.event_date,
                title=e.title,
                category=e.category,
                confidence_tier=e.confidence_tier,
                simulation_confidence=c.confidence_score if c else None,
                related_entities=_parse_related_entities(e.related_entities),
                sources=sources_by_event.get(e.event_id, []),
            )
        )

    flow_query = db.query(MoneyFlow)
    if start_year:
        flow_query = flow_query.filter(func.extract("year", MoneyFlow.start_date) >= start_year)
    if end_year:
        flow_query = flow_query.filter(func.extract("year", MoneyFlow.start_date) <= end_year)
    flow_total = flow_query.count()
    flow_rows = flow_query.order_by(MoneyFlow.start_date.asc().nulls_last(), MoneyFlow.id.asc()).offset(offset).limit(page_size).all()

    money_flows: List[SimulationFlowItem] = []
    for f in flow_rows:
        subject_id = f.edge_id or str(f.id)
        c = conf.get(("money_flow", subject_id))
        if confidence_min is not None and (not c or c.confidence_score < confidence_min):
            continue
        year = f.start_date.year if f.start_date else None
        if group_by == "decade" and year is not None:
            year = (year // 10) * 10
        money_flows.append(
            SimulationFlowItem(
                edge_id=f.edge_id,
                year=year,
                source=f.source,
                target=f.target,
                relationship=f.relationship,
                amount_usd=f.amount_usd,
                source_citation=f.source_citation,
                simulation_confidence=c.confidence_score if c else None,
                confidence_tier=c.confidence_tier if c else None,
            )
        )

    entity_query = db.query(Entity)
    if entity_id:
        entity_query = entity_query.filter(Entity.entity_id.in_(entity_id))
    entity_total = entity_query.count()
    entity_rows = entity_query.order_by(Entity.display_name.asc()).offset(offset).limit(page_size).all()
    entities: List[SimulationEntityItem] = []
    selected_entity_names = set()
    for ent in entity_rows:
        c = conf.get(("entity", ent.entity_id))
        if confidence_min is not None and (not c or c.confidence_score < confidence_min):
            continue
        selected_entity_names.add(ent.display_name)
        entities.append(
            SimulationEntityItem(
                entity_id=ent.entity_id,
                display_name=ent.display_name,
                entity_type=ent.entity_type,
                simulation_confidence=c.confidence_score if c else None,
                confidence_tier=c.confidence_tier if c else None,
                effective_start_date=c.effective_start_date if c else ent.effective_start_date,
                effective_end_date=c.effective_end_date if c else ent.effective_end_date,
                evidence_refs=_parse_evidence_refs(c.evidence_refs if c else ent.evidence_refs),
            )
        )

    rel_query = db.query(Relationship)
    if selected_entity_names:
        rel_query = rel_query.filter(
            Relationship.source.in_(list(selected_entity_names)) | Relationship.target.in_(list(selected_entity_names))
        )
    rel_total = rel_query.count()
    rel_rows = rel_query.order_by(Relationship.start_date.asc().nulls_last(), Relationship.id.asc()).offset(offset).limit(page_size).all()

    connections: List[SimulationConnectionItem] = []
    for rel in rel_rows:
        rel_key = f"{rel.source}|{rel.target}|{rel.label}"
        c = conf.get(("relationship", rel_key))
        if confidence_min is not None and (not c or c.confidence_score < confidence_min):
            continue
        connections.append(
            SimulationConnectionItem(
                source=rel.source,
                target=rel.target,
                relationship_type=rel.relationship_type,
                label=rel.label,
                start_date=rel.start_date,
                end_date=rel.end_date,
                simulation_confidence=c.confidence_score if c else None,
                confidence_tier=c.confidence_tier if c else None,
                source_citation=rel.source_citation,
            )
        )

    min_date = db.query(func.min(TimelineEvent.event_date)).scalar()
    max_date = db.query(func.max(TimelineEvent.event_date)).scalar()
    meta = SimulationMeta(
        total_events=event_total,
        total_flows=flow_total,
        total_entities=entity_total,
        total_connections=rel_total,
        page=page,
        page_size=page_size,
        truncated=(event_total > offset + page_size or flow_total > offset + page_size or entity_total > offset + page_size or rel_total > offset + page_size),
        available_filters={
            "confidence_tier": sorted(list(VALID_TIERS)),
            "group_by": sorted(list(VALID_GROUP_BY)),
            "category": sorted([x[0] for x in db.query(TimelineEvent.category).filter(TimelineEvent.category.isnot(None)).distinct().all() if x[0]]),
        },
    )

    return SimulationTimelineResponse(
        time_range={"start": min_date, "end": max_date},
        events=events,
        money_flows=money_flows,
        entities=entities,
        connections=connections,
        meta=meta,
    )


@router.get("/entities")
async def get_simulation_entities(
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    active_year: Optional[int] = Query(None, ge=1900, le=2100),
    type: Optional[str] = Query(None, max_length=80),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    conf = _confidence_map(db, confidence_min=confidence_min, active_on=date(active_year, 1, 1) if active_year else None)
    query = db.query(Entity)
    if type:
        query = query.filter(Entity.entity_type == type)
    total = query.count()
    rows = query.order_by(Entity.display_name.asc()).offset(offset).limit(page_size).all()
    out = []
    for ent in rows:
        c = conf.get(("entity", ent.entity_id))
        if confidence_min is not None and (not c or c.confidence_score < confidence_min):
            continue
        out.append(
            SimulationEntityItem(
                entity_id=ent.entity_id,
                display_name=ent.display_name,
                entity_type=ent.entity_type,
                simulation_confidence=c.confidence_score if c else None,
                confidence_tier=c.confidence_tier if c else None,
                effective_start_date=c.effective_start_date if c else ent.effective_start_date,
                effective_end_date=c.effective_end_date if c else ent.effective_end_date,
                evidence_refs=_parse_evidence_refs(c.evidence_refs if c else ent.evidence_refs),
            )
        )
    return {"total": total, "page": page, "page_size": page_size, "items": out}


@router.get("/flows")
async def get_simulation_flows(
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    min_amount: Optional[float] = Query(None, ge=0.0),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    conf = _confidence_map(db, confidence_min=confidence_min, active_on=None)
    query = db.query(MoneyFlow)
    if min_amount is not None:
        query = query.filter(MoneyFlow.amount_usd >= min_amount)
    if start_year:
        query = query.filter(func.extract("year", MoneyFlow.start_date) >= start_year)
    if end_year:
        query = query.filter(func.extract("year", MoneyFlow.start_date) <= end_year)
    total = query.count()
    rows = query.order_by(MoneyFlow.start_date.asc().nulls_last(), MoneyFlow.id.asc()).offset(offset).limit(page_size).all()
    out = []
    for f in rows:
        subject_id = f.edge_id or str(f.id)
        c = conf.get(("money_flow", subject_id))
        if confidence_min is not None and (not c or c.confidence_score < confidence_min):
            continue
        out.append(
            SimulationFlowItem(
                edge_id=f.edge_id,
                year=f.start_date.year if f.start_date else None,
                source=f.source,
                target=f.target,
                relationship=f.relationship,
                amount_usd=f.amount_usd,
                source_citation=f.source_citation,
                simulation_confidence=c.confidence_score if c else None,
                confidence_tier=c.confidence_tier if c else None,
            )
        )
    return {"total": total, "page": page, "page_size": page_size, "items": out}

