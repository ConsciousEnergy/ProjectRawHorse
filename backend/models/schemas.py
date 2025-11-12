"""
Pydantic models for data validation and API schemas
"""
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


# Base Models
class EntityBase(BaseModel):
    entity_id: str
    display_name: str
    normalized_name: str
    entity_type: Optional[str] = None


class EntityCreate(EntityBase):
    pass


class EntityResponse(EntityBase):
    model_config = ConfigDict(from_attributes=True)


# Money Flow Models
class MoneyFlowBase(BaseModel):
    source: str
    target: str
    relationship: Optional[str] = None
    amount_usd: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    source_citation: Optional[str] = None


class MoneyFlowCreate(MoneyFlowBase):
    pass


class MoneyFlowResponse(MoneyFlowBase):
    id: int
    edge_id: Optional[str] = None
    source_norm: Optional[str] = None
    target_norm: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# Award Models
class AwardBase(BaseModel):
    piid: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_uei: Optional[str] = None
    recipient_duns: Optional[str] = None
    awarding_agency: Optional[str] = None
    funding_agency: Optional[str] = None
    award_amount: Optional[float] = None
    action_date: Optional[date] = None
    description: Optional[str] = None
    naics_code: Optional[str] = None
    psc_code: Optional[str] = None


class AwardCreate(AwardBase):
    pass


class AwardResponse(AwardBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# FOIA Target Models
class FOIATargetBase(BaseModel):
    agency: str
    record_request: str
    timeframe: Optional[str] = None
    relevance: Optional[str] = None
    notes: Optional[str] = None


class FOIATargetCreate(FOIATargetBase):
    pass


class FOIATargetResponse(FOIATargetBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Relationship Models
class RelationshipBase(BaseModel):
    source: str
    target: str
    label: str


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipResponse(RelationshipBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Query Models
class QueryParams(BaseModel):
    search: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, le=1000)
    sort_by: Optional[str] = None
    sort_desc: bool = False


class EntityQueryParams(QueryParams):
    entity_type: Optional[str] = None


class MoneyFlowQueryParams(QueryParams):
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AwardQueryParams(QueryParams):
    agency: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    naics_code: Optional[str] = None


# Statistics Models
class StatsResponse(BaseModel):
    total_entities: int
    total_money_flows: int
    total_awards: int
    total_foia_targets: int
    total_money_amount: float
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


# Graph Models
class GraphNode(BaseModel):
    id: str
    name: str
    type: str
    value: Optional[float] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    value: Optional[float] = None
    label: Optional[str] = None


class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# Export Models
class ExportRequest(BaseModel):
    data_type: str  # entities, awards, money_flows, foia_targets
    format: str  # csv, json, pdf
    filters: Optional[dict] = None


class ContributionBase(BaseModel):
    data_type: str
    data: dict
    contributor_name: Optional[str] = None
    contributor_email: Optional[str] = None
    notes: Optional[str] = None


class ContributionResponse(BaseModel):
    success: bool
    message: str
    pr_url: Optional[str] = None
