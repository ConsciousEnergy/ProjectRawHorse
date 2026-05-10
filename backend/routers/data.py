"""
Data API routes for entities, awards, money flows, materials flows, and FOIA targets.

Endpoints:
- /entities, /entities/{entity_id}: List and get entities (with intel_stack_level filter).
- /money-flows: List money flows with search, amount, and date filters.
- /awards: List awards with search, agency, amount, date, NAICS filters.
- /materials-flows: List materials/technology flows (search, material_type, date range).
- /connections: Unified view of relationships + money flows + materials flows for one entity (by entity_id or entity_name).
- /foia-targets: List FOIA targets.
- /stats, /version, /refresh: Aggregate stats, data version, and data refresh.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database import Entity, MoneyFlow, Award, FOIATarget, DataVersion, Relationship, MaterialsFlow
from models.schemas import (
    EntityResponse, EntityQueryParams,
    MoneyFlowResponse, MoneyFlowQueryParams,
    AwardResponse, AwardQueryParams,
    FOIATargetResponse, StatsResponse,
    MaterialsFlowResponse,
)
from validation import (
    sanitize_search,
    validate_entity_id,
    validate_date,
    validate_amount,
    MAX_SEARCH_LENGTH,
    AMOUNT_MIN,
    AMOUNT_MAX,
)

# Import database dependency
from dependencies import get_db

router = APIRouter()


@router.get("/entities", response_model=List[EntityResponse])
async def get_entities(
    search: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    entity_type: str = Query(None, max_length=100),
    intel_stack_level: int = Query(None, ge=1, le=6),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get entities with optional filtering"""
    search = sanitize_search(search)
    query = db.query(Entity)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Entity.display_name.ilike(search_term),
                Entity.normalized_name.ilike(search_term),
                Entity.entity_id.ilike(search_term)
            )
        )
    
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    
    if intel_stack_level is not None:
        query = query.filter(Entity.intel_stack_level == intel_stack_level)
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    return query.order_by(Entity.display_name).offset(actual_offset).limit(limit).all()


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str, db: Session = Depends(get_db)):
    """Get a single entity by ID"""
    ok, err = validate_entity_id(entity_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    return db.query(Entity).filter(Entity.entity_id == entity_id).first()


@router.get("/money-flows", response_model=List[MoneyFlowResponse])
async def get_money_flows(
    search: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    min_amount: float = Query(None, ge=AMOUNT_MIN, le=AMOUNT_MAX),
    max_amount: float = Query(None, ge=AMOUNT_MIN, le=AMOUNT_MAX),
    start_date: str = Query(None, max_length=10),
    end_date: str = Query(None, max_length=10),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get money flows with optional filtering"""
    from datetime import datetime
    
    search = sanitize_search(search)
    ok, err = validate_date(start_date)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    ok, err = validate_date(end_date)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    ok, err = validate_amount(min_amount)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    ok, err = validate_amount(max_amount)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    
    query = db.query(MoneyFlow)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                MoneyFlow.source.ilike(search_term),
                MoneyFlow.target.ilike(search_term),
                MoneyFlow.relationship.ilike(search_term),
                MoneyFlow.source_citation.ilike(search_term)
            )
        )
    
    if min_amount is not None:
        query = query.filter(MoneyFlow.amount_usd >= min_amount)
    
    if max_amount is not None:
        query = query.filter(MoneyFlow.amount_usd <= max_amount)
    
    # Date range filtering
    if start_date:
        start = datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
        query = query.filter(MoneyFlow.start_date >= start)
    
    if end_date:
        end = datetime.strptime(end_date.strip(), "%Y-%m-%d").date()
        query = query.filter(MoneyFlow.start_date <= end)
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    return query.order_by(MoneyFlow.amount_usd.desc().nullslast()).offset(actual_offset).limit(limit).all()


@router.get("/awards", response_model=List[AwardResponse])
async def get_awards(
    search: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    agency: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    min_amount: float = Query(None, ge=AMOUNT_MIN, le=AMOUNT_MAX),
    max_amount: float = Query(None, ge=AMOUNT_MIN, le=AMOUNT_MAX),
    start_date: str = Query(None, max_length=10),
    end_date: str = Query(None, max_length=10),
    naics_code: str = Query(None, max_length=20),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get awards with optional filtering"""
    from datetime import datetime
    
    search = sanitize_search(search)
    agency = sanitize_search(agency)
    ok, err = validate_date(start_date)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    ok, err = validate_date(end_date)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    
    query = db.query(Award)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Award.recipient_name.ilike(search_term),
                Award.description.ilike(search_term),
                Award.piid.ilike(search_term),
                Award.awarding_agency.ilike(search_term)
            )
        )
    
    if agency:
        agency_term = f"%{agency}%"
        query = query.filter(
            or_(
                Award.awarding_agency.ilike(agency_term),
                Award.funding_agency.ilike(agency_term)
            )
        )
    
    if min_amount is not None:
        query = query.filter(Award.award_amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(Award.award_amount <= max_amount)
    
    # Date range filtering
    if start_date:
        start = datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
        query = query.filter(Award.action_date >= start)
    
    if end_date:
        end = datetime.strptime(end_date.strip(), "%Y-%m-%d").date()
        query = query.filter(Award.action_date <= end)
    
    if naics_code:
        query = query.filter(Award.naics_code == naics_code)
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    return query.order_by(Award.award_amount.desc().nullslast()).offset(actual_offset).limit(limit).all()


@router.get("/foia-targets", response_model=List[FOIATargetResponse])
async def get_foia_targets(
    search: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    agency: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    status: str = Query(None, max_length=30),
    overdue_only: bool = Query(False),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get FOIA targets with optional filtering"""
    search = sanitize_search(search)
    agency = sanitize_search(agency)
    query = db.query(FOIATarget)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                FOIATarget.record_request.ilike(search_term),
                FOIATarget.notes.ilike(search_term),
                FOIATarget.agency.ilike(search_term),
                FOIATarget.timeframe.ilike(search_term)
            )
        )
    
    if agency:
        query = query.filter(FOIATarget.agency.ilike(f"%{agency}%"))

    if status:
        query = query.filter(FOIATarget.status == status)

    if overdue_only:
        from datetime import date
        today = date.today()
        query = query.filter(
            or_(
                FOIATarget.is_overdue.is_(True),
                (
                    (FOIATarget.response_due_at.isnot(None)) &
                    (FOIATarget.response_due_at < today) &
                    (FOIATarget.status.notin_(["responded", "closed"]))
                )
            )
        )
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    results = query.order_by(FOIATarget.priority_score.desc().nullslast()).offset(actual_offset).limit(limit).all()

    # Backwards-compatible computed overdue flag for legacy rows.
    from datetime import date
    today = date.today()
    for row in results:
        if row.response_due_at and row.status not in ("responded", "closed"):
            row.is_overdue = bool(row.is_overdue) or row.response_due_at < today

    return results


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_entities = db.query(func.count(Entity.id)).scalar()
    total_money_flows = db.query(func.count(MoneyFlow.id)).scalar()
    total_awards = db.query(func.count(Award.id)).scalar()
    total_foia = db.query(func.count(FOIATarget.id)).scalar()
    
    total_money = db.query(func.sum(MoneyFlow.amount_usd)).scalar() or 0
    
    # Get date range from money flows and awards
    min_money_date = db.query(func.min(MoneyFlow.start_date)).scalar()
    max_money_date = db.query(func.max(MoneyFlow.start_date)).scalar()
    min_award_date = db.query(func.min(Award.action_date)).scalar()
    max_award_date = db.query(func.max(Award.action_date)).scalar()
    
    # Also parse dates from FOIA target timeframes (e.g., "1949-1951", "2003-present", "1980s-present")
    from datetime import datetime
    import re
    foia_dates = []
    foia_targets = db.query(FOIATarget.timeframe).filter(FOIATarget.timeframe.isnot(None)).all()
    for (timeframe,) in foia_targets:
        if timeframe:
            # Parse various timeframe formats
            # "1949-1951" -> extract 1949 and 1951
            # "2003-present" -> extract 2003
            # "1980s-present" -> extract 1980
            year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', timeframe)
            for year_str in year_matches:
                try:
                    year = int(year_str)
                    foia_dates.append(datetime(year, 1, 1).date())
                except (ValueError, AttributeError):
                    continue
    
    # Combine date ranges from all sources
    all_dates = [d for d in [min_money_date, max_money_date, min_award_date, max_award_date] + foia_dates if d is not None]
    min_date = min(all_dates) if all_dates else None
    max_date = max(all_dates) if all_dates else None
    
    return StatsResponse(
        total_entities=total_entities,
        total_money_flows=total_money_flows,
        total_awards=total_awards,
        total_foia_targets=total_foia,
        total_money_amount=float(total_money),
        date_range_start=min_date,
        date_range_end=max_date
    )


@router.get("/materials-flows", response_model=List[MaterialsFlowResponse])
async def get_materials_flows(
    search: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    material_type: str = Query(None, max_length=100),
    start_date: str = Query(None, max_length=10),
    end_date: str = Query(None, max_length=10),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get materials/technology flows. Filter by search (source/target/description/relationship), material_type, and date range."""
    from datetime import datetime
    search = sanitize_search(search)
    ok, err = validate_date(start_date)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    ok, err = validate_date(end_date)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    query = db.query(MaterialsFlow)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                MaterialsFlow.source.ilike(search_term),
                MaterialsFlow.target.ilike(search_term),
                MaterialsFlow.description.ilike(search_term),
                MaterialsFlow.relationship.ilike(search_term),
            )
        )
    if material_type:
        query = query.filter(MaterialsFlow.material_type.ilike(f"%{material_type}%"))
    if start_date:
        start = datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
        query = query.filter(MaterialsFlow.start_date >= start)
    if end_date:
        end = datetime.strptime(end_date.strip(), "%Y-%m-%d").date()
        query = query.filter(MaterialsFlow.start_date <= end)
    return query.order_by(MaterialsFlow.start_date.desc().nullslast()).offset(offset).limit(limit).all()


@router.get("/connections")
async def get_connections(
    entity_id: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    entity_name: str = Query(None, max_length=MAX_SEARCH_LENGTH),
    db: Session = Depends(get_db)
):
    """Unified view of relationships, money flows, and materials flows for one entity.
    Provide entity_id or entity_name (display_name); name is matched case-insensitive partial."""
    if not entity_id and not entity_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide entity_id or entity_name"
        )
    entity_id = sanitize_search(entity_id)
    entity_name = sanitize_search(entity_name)
    name_term = f"%{entity_name}%" if entity_name else None
    entity = None
    if entity_id:
        ok, err = validate_entity_id(entity_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
        entity = db.query(Entity).filter(Entity.entity_id == entity_id).first()
        if entity:
            search_name = entity.display_name
        else:
            search_name = entity_id
    else:
        search_name = entity_name
        entity = db.query(Entity).filter(Entity.display_name.ilike(f"%{entity_name}%")).first()
        if entity:
            search_name = entity.display_name
    relationships = db.query(Relationship).filter(
        (Relationship.source.ilike(f"%{search_name}%")) |
        (Relationship.target.ilike(f"%{search_name}%"))
    ).all()
    money_flows = db.query(MoneyFlow).filter(
        (MoneyFlow.source.ilike(f"%{search_name}%")) |
        (MoneyFlow.target.ilike(f"%{search_name}%"))
    ).all()
    materials_flows = db.query(MaterialsFlow).filter(
        (MaterialsFlow.source.ilike(f"%{search_name}%")) |
        (MaterialsFlow.target.ilike(f"%{search_name}%"))
    ).all()
    entity_data = None
    if entity:
        entity_data = {
            "entity_id": entity.entity_id,
            "display_name": entity.display_name,
            "entity_type": entity.entity_type,
            "intel_stack_level": entity.intel_stack_level,
        }
    return {
        "entity": entity_data,
        "relationships": [
            {"source": r.source, "target": r.target, "label": r.label, "description": getattr(r, "description", None), "relationship_type": getattr(r, "relationship_type", None)}
            for r in relationships
        ],
        "money_flows": [
            {"source": m.source, "target": m.target, "amount_usd": m.amount_usd, "relationship": m.relationship}
            for m in money_flows
        ],
        "materials_flows": [
            {"source": m.source, "target": m.target, "material_type": m.material_type, "relationship": m.relationship}
            for m in materials_flows
        ],
    }


@router.get("/version")
async def get_data_version(db: Session = Depends(get_db)):
    """Get current data version and last update timestamp"""
    version_record = db.query(DataVersion).order_by(DataVersion.id.desc()).first()
    
    if not version_record:
        # Initialize version if it doesn't exist
        version_record = DataVersion(version=1)
        db.add(version_record)
        db.commit()
        db.refresh(version_record)
    
    return {
        "version": version_record.version,
        "last_updated": version_record.last_updated.isoformat() if version_record.last_updated else None,
        "last_modified_by": version_record.last_modified_by
    }


@router.post("/refresh")
async def refresh_data(db: Session = Depends(get_db)):
    """Trigger data reload from CSV files and increment version"""
    import os
    import yaml
    from data_loader import load_all_data
    from audit import log_audit
    
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    config_path = os.path.join(PROJECT_ROOT, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    try:
        load_all_data(db, config, PROJECT_ROOT)
    except Exception as exc:
        log_audit(db, action="data_refresh", actor="api", detail=str(exc), success=False)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Data refresh failed")
    
    version_record = db.query(DataVersion).order_by(DataVersion.id.desc()).first()
    if version_record:
        version_record.version += 1
        from datetime import datetime
        version_record.last_updated = datetime.utcnow()
        version_record.last_modified_by = "api_refresh"
    else:
        version_record = DataVersion(version=1, last_modified_by="api_refresh")
        db.add(version_record)
    
    db.commit()
    log_audit(db, action="data_refresh", actor="api", detail=f"version={version_record.version}", success=True)
    
    return {
        "success": True,
        "message": "Data refreshed successfully",
        "version": version_record.version,
        "last_updated": version_record.last_updated.isoformat() if version_record.last_updated else None
    }
