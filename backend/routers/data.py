"""
Data API routes for entities, awards, money flows, and FOIA targets
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database import Entity, MoneyFlow, Award, FOIATarget, DataVersion
from models.schemas import (
    EntityResponse, EntityQueryParams,
    MoneyFlowResponse, MoneyFlowQueryParams,
    AwardResponse, AwardQueryParams,
    FOIATargetResponse, StatsResponse
)

# Import database dependency
from dependencies import get_db

router = APIRouter()


@router.get("/entities", response_model=List[EntityResponse])
async def get_entities(
    search: str = Query(None),
    entity_type: str = Query(None),
    intel_stack_level: int = Query(None),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get entities with optional filtering"""
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
    return db.query(Entity).filter(Entity.entity_id == entity_id).first()


@router.get("/money-flows", response_model=List[MoneyFlowResponse])
async def get_money_flows(
    search: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get money flows with optional filtering"""
    from datetime import datetime
    
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
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(MoneyFlow.start_date >= start)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(MoneyFlow.start_date <= end)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    return query.order_by(MoneyFlow.amount_usd.desc().nullslast()).offset(actual_offset).limit(limit).all()


@router.get("/awards", response_model=List[AwardResponse])
async def get_awards(
    search: str = Query(None),
    agency: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    naics_code: str = Query(None),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get awards with optional filtering"""
    from datetime import datetime
    
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
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Award.action_date >= start)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Award.action_date <= end)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    if naics_code:
        query = query.filter(Award.naics_code == naics_code)
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    return query.order_by(Award.award_amount.desc().nullslast()).offset(actual_offset).limit(limit).all()


@router.get("/foia-targets", response_model=List[FOIATargetResponse])
async def get_foia_targets(
    search: str = Query(None),
    agency: str = Query(None),
    offset: int = Query(0, ge=0),
    skip: int = Query(None, ge=0),  # Alias for offset
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get FOIA targets with optional filtering"""
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
    
    # Use skip if offset not provided (backwards compatibility)
    actual_offset = offset if offset > 0 else (skip or 0)
    
    return query.order_by(FOIATarget.priority_score.desc().nullslast()).offset(actual_offset).limit(limit).all()


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
    
    # Get project root
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load configuration
    config_path = os.path.join(PROJECT_ROOT, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Reload all data
    load_all_data(db, config, PROJECT_ROOT)
    
    # Increment version
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
    
    return {
        "success": True,
        "message": "Data refreshed successfully",
        "version": version_record.version,
        "last_updated": version_record.last_updated.isoformat() if version_record.last_updated else None
    }
