"""
Pydantic models for data validation and API schemas.

Sections: Entity, MoneyFlow, Award, FOIATarget, Relationship, MaterialsFlow,
query params, Stats, Graph, Sankey, DataVersion, Export, Contribution,
Pyramid/Intel Stack (PyramidEntitySummary, PyramidLevelSummary, CrossLevelFlow, PyramidDataResponse).
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
    intel_stack_level: Optional[int] = None
    evidence_refs: Optional[str] = None
    effective_start_date: Optional[date] = None
    effective_end_date: Optional[date] = None
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
    specificity_score: Optional[float] = None
    likelihood_score: Optional[float] = None
    priority_score: Optional[float] = None
    quality_notes: Optional[str] = None


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
    description: Optional[str] = None
    relationship_type: Optional[str] = None
    source_citation: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipResponse(RelationshipBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Materials Flow Models
class MaterialsFlowBase(BaseModel):
    source: str
    target: str
    material_type: Optional[str] = None
    relationship: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    source_citation: Optional[str] = None


class MaterialsFlowResponse(MaterialsFlowBase):
    id: int
    edge_id: Optional[str] = None
    source_norm: Optional[str] = None
    target_norm: Optional[str] = None
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
    full_name: Optional[str] = None  # Expanded name for acronyms
    intel_stack_level: Optional[int] = None  # Intelligence stack hierarchy level (1-6)


class GraphEdge(BaseModel):
    source: str
    target: str
    value: Optional[float] = None
    label: Optional[str] = None


class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# Sankey Diagram Models
class SankeyNode(BaseModel):
    name: str
    value: float
    category: str


class SankeyLink(BaseModel):
    source: str
    target: str
    value: float
    label: Optional[str] = None
    type: Optional[str] = None  # 'money_flow' or 'relationship'


class SankeyData(BaseModel):
    nodes: List[SankeyNode]
    links: List[SankeyLink]


# Data Version Models
class DataVersionResponse(BaseModel):
    version: int
    last_updated: Optional[datetime] = None
    last_modified_by: Optional[str] = None


class DataRefreshResponse(BaseModel):
    success: bool
    message: str
    version: int
    last_updated: Optional[datetime] = None


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


# Pyramid / Intel Stack (GET /analysis/intel-stack/pyramid and /summary)
class PyramidEntitySummary(BaseModel):
    entity_id: str
    display_name: str
    entity_type: Optional[str] = None
    description: Optional[str] = None
    relationship_count: int = 0
    money_flow_total_usd: float = 0.0
    key_connections: List[str] = []
    hierarchy_parent: Optional[str] = None
    evidence_refs: Optional[str] = None
    effective_start_date: Optional[date] = None
    effective_end_date: Optional[date] = None


class PyramidLevelSummary(BaseModel):
    level: int
    name: str
    color: str
    entity_count: int
    total_money_flow_usd: float
    entities: List[PyramidEntitySummary]


class CrossLevelFlow(BaseModel):
    from_level: int
    to_level: int
    total_usd: float
    flow_count: int


class PyramidDataResponse(BaseModel):
    """Response for GET /analysis/intel-stack/pyramid."""
    levels: List[PyramidLevelSummary]
    cross_level_flows: List[CrossLevelFlow]


# Hierarchy chain (GET /analysis/intel-stack/hierarchy)
class HierarchyNode(BaseModel):
    entity_id: str
    display_name: str
    intel_stack_level: Optional[int] = None
    entity_type: Optional[str] = None


class HierarchyChain(BaseModel):
    """Chain of command from a given entity up toward L1 and down toward L6."""
    target: HierarchyNode
    chain_up: List[HierarchyNode] = []
    chain_down: List[HierarchyNode] = []
    lateral: List[HierarchyNode] = []
