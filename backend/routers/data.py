"""
Data API routes for entities, awards, money flows, and FOIA targets
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database import Entity, MoneyFlow, Award, FOIATarget
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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get entities with optional filtering"""
    query = db.query(Entity)
    
    if search:
        query = query.filter(
            or_(
                Entity.display_name.ilike(f"%{search}%"),
                Entity.normalized_name.ilike(f"%{search}%")
            )
        )
    
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    
    return query.offset(skip).limit(limit).all()


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str, db: Session = Depends(get_db)):
    """Get a single entity by ID"""
    return db.query(Entity).filter(Entity.entity_id == entity_id).first()


@router.get("/money-flows", response_model=List[MoneyFlowResponse])
async def get_money_flows(
    search: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get money flows with optional filtering"""
    query = db.query(MoneyFlow)
    
    if search:
        query = query.filter(
            or_(
                MoneyFlow.source.ilike(f"%{search}%"),
                MoneyFlow.target.ilike(f"%{search}%"),
                MoneyFlow.relationship.ilike(f"%{search}%")
            )
        )
    
    if min_amount is not None:
        query = query.filter(MoneyFlow.amount_usd >= min_amount)
    
    if max_amount is not None:
        query = query.filter(MoneyFlow.amount_usd <= max_amount)
    
    return query.offset(skip).limit(limit).all()


@router.get("/awards", response_model=List[AwardResponse])
async def get_awards(
    search: str = Query(None),
    agency: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    naics_code: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get awards with optional filtering"""
    query = db.query(Award)
    
    if search:
        query = query.filter(
            or_(
                Award.recipient_name.ilike(f"%{search}%"),
                Award.description.ilike(f"%{search}%")
            )
        )
    
    if agency:
        query = query.filter(
            or_(
                Award.awarding_agency.ilike(f"%{agency}%"),
                Award.funding_agency.ilike(f"%{agency}%")
            )
        )
    
    if min_amount is not None:
        query = query.filter(Award.award_amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(Award.award_amount <= max_amount)
    
    if naics_code:
        query = query.filter(Award.naics_code == naics_code)
    
    return query.offset(skip).limit(limit).all()


@router.get("/foia-targets", response_model=List[FOIATargetResponse])
async def get_foia_targets(
    search: str = Query(None),
    agency: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get FOIA targets with optional filtering"""
    query = db.query(FOIATarget)
    
    if search:
        query = query.filter(
            or_(
                FOIATarget.record_request.ilike(f"%{search}%"),
                FOIATarget.notes.ilike(f"%{search}%")
            )
        )
    
    if agency:
        query = query.filter(FOIATarget.agency.ilike(f"%{agency}%"))
    
    return query.offset(skip).limit(limit).all()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_entities = db.query(func.count(Entity.id)).scalar()
    total_money_flows = db.query(func.count(MoneyFlow.id)).scalar()
    total_awards = db.query(func.count(Award.id)).scalar()
    total_foia = db.query(func.count(FOIATarget.id)).scalar()
    
    total_money = db.query(func.sum(MoneyFlow.amount_usd)).scalar() or 0
    
    # Get date range
    min_date = db.query(func.min(MoneyFlow.start_date)).scalar()
    max_date = db.query(func.max(MoneyFlow.start_date)).scalar()
    
    return StatsResponse(
        total_entities=total_entities,
        total_money_flows=total_money_flows,
        total_awards=total_awards,
        total_foia_targets=total_foia,
        total_money_amount=float(total_money),
        date_range_start=min_date,
        date_range_end=max_date
    )
