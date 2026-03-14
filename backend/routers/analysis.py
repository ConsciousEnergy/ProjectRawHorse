"""
Analysis API routes for graph data, relationship exploration, and intelligence stack.

Endpoints:
- /graph/entities, /graph/money-flows: Force-directed graph data (nodes + edges).
- /relationships/{entity_name}: Money flows and relationships for an entity by name.
- /entity/{entity_id}/flows: All flows (money, materials, relationships) for one entity by id or display_name.
- /intel-stack/summary: Entities grouped by intel_stack_level with flow totals per level.
- /intel-stack/pyramid: Full pyramid data (levels, entity counts, total money per level, cross-level flows).
- /financial/flows, /financial/totals, /timeline, /sankey: Financial summaries and Sankey diagram data.
"""
import os
import csv
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Entity, MoneyFlow, Relationship, Award, MaterialsFlow
from models.schemas import (
    GraphData, GraphNode, GraphEdge, SankeyData, SankeyNode, SankeyLink,
    PyramidDataResponse, PyramidLevelSummary, PyramidEntitySummary, CrossLevelFlow,
    HierarchyNode, HierarchyChain,
)
from collections import defaultdict
from validation import validate_amount, AMOUNT_MIN, AMOUNT_MAX

# Import database dependency
from dependencies import get_db

# Import entity type inference at module level to ensure latest version on restart
from data_loader import infer_entity_type, AGENCY_ACRONYMS

router = APIRouter()

# Hierarchy relationship types used to infer "reports to" / parent
HIERARCHY_REL_TYPES = {"reports_to", "subordinate_to", "part_of", "operates_under", "manages", "commands", "oversees"}


def _load_entity_descriptions() -> Dict[str, str]:
    """Load display_name -> description from data/entities/entity_descriptions.csv. Cached at module level."""
    if hasattr(_load_entity_descriptions, "_cache"):
        return _load_entity_descriptions._cache
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "entities", "entity_descriptions.csv")
    path = os.path.abspath(path)
    out: Dict[str, str] = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = (row.get("display_name") or "").strip()
                desc = (row.get("description") or "").strip()
                if name and not name.startswith("#"):
                    out[name] = desc
    _load_entity_descriptions._cache = out
    return out


def infer_relationships_from_awards(db: Session) -> List[GraphEdge]:
    """
    Infer relationships from Awards data to create more connections:
    1. Awarding Agency -> Recipient relationships
    2. Co-recipients (entities that received awards from same agency)
    3. Entities with same NAICS codes (same industry)
    """
    inferred_edges = []
    seen_edges = set()  # Track (source, target) pairs to avoid duplicates
    
    # Get all awards
    awards = db.query(Award).filter(
        Award.recipient_name.isnot(None),
        Award.awarding_agency.isnot(None)
    ).all()
    
    # 1. Create Awarding Agency -> Recipient relationships
    agency_recipient_map = defaultdict(set)
    for award in awards:
        if award.awarding_agency and award.recipient_name:
            agency = award.awarding_agency.strip()
            recipient = award.recipient_name.strip()
            if agency and recipient and agency != recipient:
                edge_key = (agency, recipient)
                if edge_key not in seen_edges:
                    inferred_edges.append(GraphEdge(
                        source=agency,
                        target=recipient,
                        label="Award Recipient"
                    ))
                    seen_edges.add(edge_key)
                agency_recipient_map[agency].add(recipient)
    
    # 2. Create co-recipient relationships (entities that received awards from same agency)
    # Group recipients by agency
    for agency, recipients in agency_recipient_map.items():
        recipients_list = list(recipients)
        # Create connections between all pairs of recipients from same agency
        for i in range(len(recipients_list)):
            for j in range(i + 1, len(recipients_list)):
                source = recipients_list[i]
                target = recipients_list[j]
                edge_key = tuple(sorted([source, target]))  # Undirected edge
                if edge_key not in seen_edges:
                    inferred_edges.append(GraphEdge(
                        source=source,
                        target=target,
                        label="Co-Recipient (Same Agency)"
                    ))
                    seen_edges.add(edge_key)
    
    # 3. Create relationships based on NAICS codes (same industry)
    naics_entity_map = defaultdict(set)
    for award in awards:
        if award.recipient_name and award.naics_code:
            entity = award.recipient_name.strip()
            naics = award.naics_code.strip()
            if entity and naics:
                naics_entity_map[naics].add(entity)
    
    # Connect entities with same NAICS code
    for naics, entities in naics_entity_map.items():
        if len(entities) > 1:  # Only if multiple entities share the code
            entities_list = list(entities)
            for i in range(len(entities_list)):
                for j in range(i + 1, len(entities_list)):
                    source = entities_list[i]
                    target = entities_list[j]
                    edge_key = tuple(sorted([source, target]))
                    if edge_key not in seen_edges:
                        inferred_edges.append(GraphEdge(
                            source=source,
                            target=target,
                            label=f"Same Industry (NAICS: {naics})"
                        ))
                        seen_edges.add(edge_key)
    
    return inferred_edges


@router.get("/graph/entities", response_model=GraphData)
async def get_entity_graph(
    limit: int = Query(500, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get entity relationship graph data
    
    Returns all relationships AND money flows combined into one graph.
    Includes NRO commercial partner relationships and original money flows.
    """
    # Get all relationships (no limit to ensure NRO data is included)
    relationships = db.query(Relationship).all()
    
    # Also get money flows and convert them to relationship-like edges
    # This combines both datasets into one unified graph
    money_flows = db.query(MoneyFlow).all()
    
    # Get all entities
    all_entities = db.query(Entity).all()
    
    # Create a mapping of names to entities for lookup
    # Support multiple name variations for better matching
    entity_map = {}
    for e in all_entities:
        # Map by display name (exact and lowercase)
        if e.display_name:
            entity_map[e.display_name] = e
            entity_map[e.display_name.lower()] = e
            # Also map with stripped quotes and normalized
            name_clean = e.display_name.strip('"').strip()
            entity_map[name_clean] = e
            entity_map[name_clean.lower()] = e
        # Map by normalized name
        if e.normalized_name:
            entity_map[e.normalized_name] = e
            entity_map[e.normalized_name.lower()] = e
        # Map by entity_id
        entity_map[e.entity_id] = e
    
    # Infer additional relationships from Awards data
    inferred_edges = infer_relationships_from_awards(db)
    
    # Extract all unique entity names from relationships, money flows, AND inferred edges
    entity_names_in_graph = set()
    for r in relationships:
        entity_names_in_graph.add(r.source)
        entity_names_in_graph.add(r.target)
    for mf in money_flows:
        entity_names_in_graph.add(mf.source)
        entity_names_in_graph.add(mf.target)
    for ie in inferred_edges:
        entity_names_in_graph.add(ie.source)
        entity_names_in_graph.add(ie.target)
    
    # Calculate connection counts (from relationships, money flows, AND inferred edges)
    connection_counts = {}
    for r in relationships:
        connection_counts[r.source] = connection_counts.get(r.source, 0) + 1
        connection_counts[r.target] = connection_counts.get(r.target, 0) + 1
    for mf in money_flows:
        connection_counts[mf.source] = connection_counts.get(mf.source, 0) + 1
        connection_counts[mf.target] = connection_counts.get(mf.target, 0) + 1
    for ie in inferred_edges:
        connection_counts[ie.source] = connection_counts.get(ie.source, 0) + 1
        connection_counts[ie.target] = connection_counts.get(ie.target, 0) + 1
    
    # Create nodes - use entity names as IDs to match relationships
    nodes = []
    seen_names = set()
    
    for entity_name in entity_names_in_graph:
        if entity_name in seen_names:
            continue
        seen_names.add(entity_name)
        
        # Try to find the entity in our database (try multiple variations)
        entity_name_clean = entity_name.strip('"').strip()
        entity = (entity_map.get(entity_name) or 
                 entity_map.get(entity_name.lower()) or
                 entity_map.get(entity_name_clean) or
                 entity_map.get(entity_name_clean.lower()))
        
        # Get connection count
        connections = connection_counts.get(entity_name, 0)
        
        # Scale node size: base 8, +3 per connection, max 25
        node_value = min(8 + (connections * 3), 25)
        
        # Determine entity type
        if entity and entity.entity_type:
            entity_type = entity.entity_type
        else:
            # Infer from name if not in database
            entity_type = infer_entity_type(entity_name)
        
        # Get full name for acronyms
        full_name = AGENCY_ACRONYMS.get(entity_name.strip().upper())
        
        # Get intel stack level if available
        intel_stack_level = entity.intel_stack_level if entity else None
        
        nodes.append(
            GraphNode(
                id=entity_name,  # Use name as ID to match relationships
                name=entity_name,
                type=entity_type,
                value=node_value,
                full_name=full_name,
                intel_stack_level=intel_stack_level
            )
        )
    
    # Create edges from relationships
    edges = [
        GraphEdge(
            source=r.source,
            target=r.target,
            label=r.label
        )
        for r in relationships
    ]
    
    # Also add edges from money flows (combine both datasets)
    for mf in money_flows:
        # Create a label that includes amount if available
        label = mf.relationship or "Money Flow"
        if mf.amount_usd:
            # Format large amounts nicely
            if mf.amount_usd >= 1_000_000_000:
                amount_str = f"${mf.amount_usd / 1_000_000_000:.2f}B"
            elif mf.amount_usd >= 1_000_000:
                amount_str = f"${mf.amount_usd / 1_000_000:.2f}M"
            else:
                amount_str = f"${mf.amount_usd:,.0f}"
            label = f"{label} ({amount_str})"
        
        edges.append(
            GraphEdge(
                source=mf.source,
                target=mf.target,
                label=label,
                value=mf.amount_usd
            )
        )
    
    # Add inferred edges from Awards data
    edges.extend(inferred_edges)
    
    return GraphData(nodes=nodes, edges=edges)


@router.get("/graph/money-flows", response_model=GraphData)
async def get_money_flow_graph(
    min_amount: float = Query(None, ge=AMOUNT_MIN, le=AMOUNT_MAX),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get money flow graph data"""
    ok, err = validate_amount(min_amount)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    query = db.query(MoneyFlow)
    
    if min_amount:
        query = query.filter(MoneyFlow.amount_usd >= min_amount)
    
    flows = query.order_by(MoneyFlow.amount_usd.desc()).limit(limit).all()
    
    # Create nodes from unique entities
    entity_names = set()
    for flow in flows:
        entity_names.add(flow.source)
        entity_names.add(flow.target)
    
    nodes = [
        GraphNode(
            id=name,
            name=name,
            type="entity"
        )
        for name in entity_names
    ]
    
    # Create edges from money flows
    edges = [
        GraphEdge(
            source=flow.source,
            target=flow.target,
            value=flow.amount_usd,
            label=flow.relationship
        )
        for flow in flows if flow.amount_usd
    ]
    
    return GraphData(nodes=nodes, edges=edges)


@router.get("/relationships/{entity_name}")
async def get_entity_relationships(
    entity_name: str,
    db: Session = Depends(get_db)
):
    """Get all relationships for a specific entity (entity_name max 200 chars)."""
    from validation import MAX_SEARCH_LENGTH
    if len((entity_name or "")) > MAX_SEARCH_LENGTH:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="entity_name too long")
    # Money flows where entity is source or target
    money_flows = db.query(MoneyFlow).filter(
        (MoneyFlow.source.ilike(f"%{entity_name}%")) |
        (MoneyFlow.target.ilike(f"%{entity_name}%"))
    ).all()
    
    # Direct relationships
    relationships = db.query(Relationship).filter(
        (Relationship.source.ilike(f"%{entity_name}%")) |
        (Relationship.target.ilike(f"%{entity_name}%"))
    ).all()
    
    return {
        "entity": entity_name,
        "money_flows": [
            {
                "source": mf.source,
                "target": mf.target,
                "amount": mf.amount_usd,
                "date": mf.start_date,
                "relationship": mf.relationship
            }
            for mf in money_flows
        ],
        "relationships": [
            {
                "source": r.source,
                "target": r.target,
                "label": r.label
            }
            for r in relationships
        ]
    }


@router.get("/financial/flows")
async def get_financial_flows(
    db: Session = Depends(get_db)
):
    """Get financial flow summary by entity"""
    # Sum money flows by source
    outflows = db.query(
        MoneyFlow.source,
        func.sum(MoneyFlow.amount_usd).label('total')
    ).group_by(MoneyFlow.source).all()
    
    # Sum money flows by target
    inflows = db.query(
        MoneyFlow.target,
        func.sum(MoneyFlow.amount_usd).label('total')
    ).group_by(MoneyFlow.target).all()
    
    return {
        "outflows": [{"entity": o[0], "amount": o[1]} for o in outflows if o[1]],
        "inflows": [{"entity": i[0], "amount": i[1]} for i in inflows if i[1]]
    }


@router.get("/financial/totals")
async def get_financial_totals(
    db: Session = Depends(get_db)
):
    """Get total financial amounts by category"""
    total_money_flows = db.query(func.sum(MoneyFlow.amount_usd)).scalar() or 0
    total_awards = db.query(func.sum(Award.award_amount)).scalar() or 0
    
    # Get top recipients
    top_recipients = db.query(
        MoneyFlow.target,
        func.sum(MoneyFlow.amount_usd).label('total')
    ).group_by(MoneyFlow.target).order_by(func.sum(MoneyFlow.amount_usd).desc()).limit(10).all()
    
    return {
        "total_money_flows": float(total_money_flows),
        "total_awards": float(total_awards),
        "top_recipients": [
            {"entity": r[0], "amount": float(r[1])}
            for r in top_recipients if r[1]
        ]
    }


@router.get("/timeline")
async def get_timeline(
    db: Session = Depends(get_db)
):
    """Get timeline of money flows"""
    flows = db.query(
        func.strftime('%Y', MoneyFlow.start_date).label('year'),
        func.count(MoneyFlow.id).label('count'),
        func.sum(MoneyFlow.amount_usd).label('total')
    ).filter(
        MoneyFlow.start_date.isnot(None)
    ).group_by('year').order_by('year').all()
    
    return {
        "timeline": [
            {
                "year": f[0],
                "count": f[1],
                "total_amount": float(f[2]) if f[2] else 0
            }
            for f in flows
        ]
    }


@router.get("/sankey", response_model=SankeyData)
async def get_sankey_data(
    min_amount: float = Query(None, ge=AMOUNT_MIN, le=AMOUNT_MAX),
    include_relationships: bool = Query(True),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get Sankey diagram data combining money flows and relationships
    
    Returns nodes and links formatted for Sankey visualization.
    Nodes represent entities, links represent flows/relationships.
    """
    
    # Collect all unique entities
    entity_names = set()
    nodes_dict = {}  # name -> node data
    links = []
    
    # Get money flows
    money_flows_query = db.query(MoneyFlow)
    if min_amount:
        money_flows_query = money_flows_query.filter(MoneyFlow.amount_usd >= min_amount)
    money_flows = money_flows_query.order_by(MoneyFlow.amount_usd.desc()).limit(limit).all()
    
    # Process money flows
    for mf in money_flows:
        if mf.source and mf.target:
            entity_names.add(mf.source)
            entity_names.add(mf.target)
            
            # Aggregate flows between same source/target pairs
            link_key = (mf.source, mf.target)
            existing_link = next((l for l in links if l['source'] == mf.source and l['target'] == mf.target), None)
            
            if existing_link:
                existing_link['value'] = (existing_link.get('value', 0) or 0) + (mf.amount_usd or 0)
            else:
                links.append({
                    'source': mf.source,
                    'target': mf.target,
                    'value': mf.amount_usd or 0,
                    'label': mf.relationship or 'Money Flow',
                    'type': 'money_flow'
                })
    
    # Get relationships if requested
    if include_relationships:
        relationships = db.query(Relationship).limit(limit).all()
        
        for rel in relationships:
            if rel.source and rel.target:
                entity_names.add(rel.source)
                entity_names.add(rel.target)
                
                # Check if link already exists (from money flow)
                existing_link = next((l for l in links if l['source'] == rel.source and l['target'] == rel.target), None)
                
                if not existing_link:
                    links.append({
                        'source': rel.source,
                        'target': rel.target,
                        'value': 1,  # Default weight for relationships
                        'label': rel.label,
                        'type': 'relationship'
                    })
    
    # Get entity information from database
    all_entities = db.query(Entity).all()
    entity_map = {}
    for e in all_entities:
        if e.display_name:
            entity_map[e.display_name] = e
            entity_map[e.display_name.lower()] = e
        if e.normalized_name:
            entity_map[e.normalized_name] = e
            entity_map[e.normalized_name.lower()] = e
    
    # Create nodes with categories
    nodes = []
    for entity_name in entity_names:
        entity = (entity_map.get(entity_name) or 
                 entity_map.get(entity_name.lower()) or
                 entity_map.get(entity_name.strip('"').strip()) or
                 entity_map.get(entity_name.strip('"').strip().lower()))
        
        # Determine category/type
        if entity and entity.entity_type:
            category = entity.entity_type
        else:
            category = infer_entity_type(entity_name)
        
        # Calculate total flow value (sum of incoming and outgoing)
        total_value = 0
        for link in links:
            if link['source'] == entity_name or link['target'] == entity_name:
                total_value += link.get('value', 0)
        
        nodes.append(SankeyNode(
            name=entity_name,
            value=total_value,
            category=category
        ))
    
    # Filter links to only include nodes that exist
    valid_entity_names = {node.name for node in nodes}
    filtered_links = [
        SankeyLink(
            source=l['source'],
            target=l['target'],
            value=l.get('value', 0),
            label=l.get('label'),
            type=l.get('type')
        )
        for l in links 
        if l['source'] in valid_entity_names and l['target'] in valid_entity_names
    ]
    
    return SankeyData(nodes=nodes, links=filtered_links)


# Intel stack level names and colors; must match frontend IntelStackFilter.tsx
PYRAMID_LEVELS = [
    {"level": 1, "name": "Control Group", "color": "#FF1744"},
    {"level": 2, "name": "Administrators", "color": "#FF6B35"},
    {"level": 3, "name": "FFRDCs", "color": "#FF9800"},
    {"level": 4, "name": "Prime Contractors", "color": "#5B4FFF"},
    {"level": 5, "name": "Facilities", "color": "#4CAF50"},
    {"level": 6, "name": "Programs", "color": "#E91E63"},
]


@router.get("/entity/{entity_id}/flows")
async def get_entity_flows(
    entity_id: str,
    db: Session = Depends(get_db)
):
    """Return all flows (money, materials, relationships) for one entity.
    Path parameter can be entity_id or display_name; matching is by exact id or display_name."""
    from validation import MAX_SEARCH_LENGTH
    if len(entity_id) > MAX_SEARCH_LENGTH:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="entity_id too long")
    entity = db.query(Entity).filter(
        (Entity.entity_id == entity_id) | (Entity.display_name.ilike(entity_id))
    ).first()
    if not entity:
        search_name = entity_id
    else:
        search_name = entity.display_name
    money_flows = db.query(MoneyFlow).filter(
        (MoneyFlow.source == search_name) | (MoneyFlow.target == search_name)
    ).all()
    materials_flows = db.query(MaterialsFlow).filter(
        (MaterialsFlow.source == search_name) | (MaterialsFlow.target == search_name)
    ).all()
    relationships = db.query(Relationship).filter(
        (Relationship.source == search_name) | (Relationship.target == search_name)
    ).all()
    return {
        "entity_id": entity.entity_id if entity else None,
        "display_name": search_name,
        "money_flows": [
            {"source": m.source, "target": m.target, "amount_usd": m.amount_usd, "relationship": m.relationship}
            for m in money_flows
        ],
        "materials_flows": [
            {"source": m.source, "target": m.target, "material_type": m.material_type, "relationship": m.relationship}
            for m in materials_flows
        ],
        "relationships": [
            {"source": r.source, "target": r.target, "label": r.label}
            for r in relationships
        ],
    }


@router.get("/intel-stack/summary")
async def get_intel_stack_summary(db: Session = Depends(get_db)):
    """Entities grouped by intel_stack_level with flow totals per level."""
    levels = PYRAMID_LEVELS
    result = []
    for lev in levels:
        entities = db.query(Entity).filter(Entity.intel_stack_level == lev["level"]).all()
        total_money = db.query(func.sum(MoneyFlow.amount_usd)).join(
            Entity,
            (MoneyFlow.source == Entity.display_name) | (MoneyFlow.target == Entity.display_name)
        ).filter(Entity.intel_stack_level == lev["level"]).scalar() or 0
        result.append({
            "level": lev["level"],
            "name": lev["name"],
            "color": lev["color"],
            "entity_count": len(entities),
            "total_money_flow_usd": float(total_money),
            "entities": [{"entity_id": e.entity_id, "display_name": e.display_name, "entity_type": e.entity_type} for e in entities],
        })
    return {"levels": result}


@router.get("/intel-stack/pyramid", response_model=PyramidDataResponse)
async def get_pyramid_data(db: Session = Depends(get_db)):
    """Pyramid data: entities grouped by level with enriched per-entity stats; cross-level flows. O(n) money aggregation."""
    # Precompute: display_name -> intel_stack_level for all entities with level
    entities_with_level = db.query(Entity).filter(Entity.intel_stack_level.isnot(None)).all()
    name_to_level: Dict[str, int] = {e.display_name: e.intel_stack_level for e in entities_with_level}

    # One pass: money total per display_name (entity appears as source or target)
    money_per_name: Dict[str, float] = defaultdict(float)
    money_flows = db.query(MoneyFlow).filter(
        MoneyFlow.amount_usd.isnot(None),
        MoneyFlow.source.isnot(None),
        MoneyFlow.target.isnot(None),
    ).all()
    for mf in money_flows:
        amt = float(mf.amount_usd or 0)
        if mf.source:
            money_per_name[mf.source] += amt
        if mf.target:
            money_per_name[mf.target] += amt

    # Relationship count per display_name and key_connections (other names), hierarchy_parent (who this entity reports to)
    rels = db.query(Relationship).filter(
        Relationship.source.isnot(None),
        Relationship.target.isnot(None),
    ).all()
    rel_count_per_name: Dict[str, int] = defaultdict(int)
    connection_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    hierarchy_parent: Dict[str, str] = {}
    for r in rels:
        rel_count_per_name[r.source] += 1
        rel_count_per_name[r.target] += 1
        if r.source != r.target:
            connection_counts[r.source][r.target] += 1
            connection_counts[r.target][r.source] += 1
        if r.relationship_type in HIERARCHY_REL_TYPES and r.target:
            hierarchy_parent[r.target] = r.source

    for mf in money_flows:
        if mf.source and mf.target and mf.source != mf.target:
            connection_counts[mf.source][mf.target] += 1
            connection_counts[mf.target][mf.source] += 1

    descriptions = _load_entity_descriptions()

    def key_connections(name: str, top_n: int = 3) -> List[str]:
        counts = connection_counts.get(name)
        if not counts:
            return []
        sorted_conn = sorted(counts.items(), key=lambda x: -x[1])
        return [other for other, _ in sorted_conn[:top_n]]

    levels_out = []
    for lev in PYRAMID_LEVELS:
        entities = db.query(Entity).filter(Entity.intel_stack_level == lev["level"]).all()
        level_total_money = sum(money_per_name.get(e.display_name, 0.0) for e in entities)
        entity_summaries = [
            PyramidEntitySummary(
                entity_id=e.entity_id,
                display_name=e.display_name,
                entity_type=e.entity_type,
                description=descriptions.get(e.display_name),
                relationship_count=rel_count_per_name.get(e.display_name, 0),
                money_flow_total_usd=money_per_name.get(e.display_name, 0.0),
                key_connections=key_connections(e.display_name),
                hierarchy_parent=hierarchy_parent.get(e.display_name),
                evidence_refs=getattr(e, 'evidence_refs', None),
                effective_start_date=getattr(e, 'effective_start_date', None),
                effective_end_date=getattr(e, 'effective_end_date', None),
            )
            for e in entities
        ]
        levels_out.append(
            PyramidLevelSummary(
                level=lev["level"],
                name=lev["name"],
                color=lev["color"],
                entity_count=len(entities),
                total_money_flow_usd=level_total_money,
                entities=entity_summaries,
            )
        )

    # Cross-level flows (unchanged logic, already one pass)
    flow_by_pair = defaultdict(lambda: {"total": 0.0, "count": 0})
    for mf in money_flows:
        sl = name_to_level.get(mf.source)
        tl = name_to_level.get(mf.target)
        if sl is not None and tl is not None and sl != tl:
            key = (sl, tl)
            flow_by_pair[key]["total"] += float(mf.amount_usd or 0)
            flow_by_pair[key]["count"] += 1
    cross_flows = [
        CrossLevelFlow(from_level=from_l, to_level=to_l, total_usd=v["total"], flow_count=v["count"])
        for (from_l, to_l), v in flow_by_pair.items()
    ]
    return PyramidDataResponse(levels=levels_out, cross_level_flows=cross_flows)


def _entity_to_hierarchy_node(e: Entity) -> HierarchyNode:
    return HierarchyNode(
        entity_id=e.entity_id,
        display_name=e.display_name,
        intel_stack_level=e.intel_stack_level,
        entity_type=e.entity_type,
    )


@router.get("/intel-stack/hierarchy", response_model=HierarchyChain)
async def get_intel_stack_hierarchy(
    entity_id: str = Query(..., description="Entity ID or display_name"),
    db: Session = Depends(get_db),
):
    """Chain of command from the given entity up toward L1 and down toward L6 using hierarchy relationship types."""
    from validation import MAX_SEARCH_LENGTH
    if len(entity_id) > MAX_SEARCH_LENGTH:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="entity_id too long")
    entity = db.query(Entity).filter(
        (Entity.entity_id == entity_id) | (Entity.display_name.ilike(entity_id))
    ).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    name = entity.display_name
    level = entity.intel_stack_level

    # All hierarchy-type relationships
    rels = db.query(Relationship).filter(
        Relationship.relationship_type.in_(list(HIERARCHY_REL_TYPES)),
        (Relationship.source == name) | (Relationship.target == name),
    ).all()

    # Parents: rels where target=name -> source is parent
    parents_by_name: Dict[str, Entity] = {}
    children_by_name: Dict[str, Entity] = {}
    for r in rels:
        if r.target == name and r.source:
            parent = db.query(Entity).filter(Entity.display_name == r.source).first()
            if parent:
                parents_by_name[parent.display_name] = parent
        if r.source == name and r.target:
            child = db.query(Entity).filter(Entity.display_name == r.target).first()
            if child:
                children_by_name[child.display_name] = child

    # Chain up: walk parents until L1 or no parent
    chain_up: List[HierarchyNode] = []
    seen_up = {name}
    current = list(parents_by_name.values())
    while current:
        next_level = []
        for e in current:
            if e.display_name in seen_up:
                continue
            seen_up.add(e.display_name)
            chain_up.append(_entity_to_hierarchy_node(e))
            if e.intel_stack_level == 1:
                continue
            parent_rels = db.query(Relationship).filter(
                Relationship.target == e.display_name,
                Relationship.relationship_type.in_(list(HIERARCHY_REL_TYPES)),
            ).all()
            for pr in parent_rels:
                if pr.source and pr.source not in seen_up:
                    p_ent = db.query(Entity).filter(Entity.display_name == pr.source).first()
                    if p_ent:
                        next_level.append(p_ent)
        current = next_level

    # Chain down: walk children until L6 or no child
    chain_down: List[HierarchyNode] = []
    seen_down = {name}
    current = list(children_by_name.values())
    while current:
        next_level = []
        for e in current:
            if e.display_name in seen_down:
                continue
            seen_down.add(e.display_name)
            chain_down.append(_entity_to_hierarchy_node(e))
            if e.intel_stack_level == 6:
                continue
            child_rels = db.query(Relationship).filter(
                Relationship.source == e.display_name,
                Relationship.relationship_type.in_(list(HIERARCHY_REL_TYPES)),
            ).all()
            for cr in child_rels:
                if cr.target and cr.target not in seen_down:
                    c_ent = db.query(Entity).filter(Entity.display_name == cr.target).first()
                    if c_ent:
                        next_level.append(c_ent)
        current = next_level

    # Lateral: same-level entities with any relationship to this entity
    lateral_names = set()
    all_rels = db.query(Relationship).filter(
        (Relationship.source == name) | (Relationship.target == name),
    ).all()
    for r in all_rels:
        other = r.target if r.source == name else r.source
        if other and other != name:
            lateral_names.add(other)
    lateral_entities = db.query(Entity).filter(
        Entity.display_name.in_(lateral_names),
        Entity.intel_stack_level == level,
    ).all() if level is not None else []
    lateral_nodes = [_entity_to_hierarchy_node(e) for e in lateral_entities]

    return HierarchyChain(
        target=_entity_to_hierarchy_node(entity),
        chain_up=chain_up,
        chain_down=chain_down,
        lateral=lateral_nodes,
    )


@router.get("/intel-stack/entity/{entity_id}/detail")
async def get_intel_stack_entity_detail(
    entity_id: str,
    db: Session = Depends(get_db),
):
    """Full entity detail for pyramid drill-down: description, relationships by type, money and materials flows."""
    from validation import MAX_SEARCH_LENGTH
    if len(entity_id) > MAX_SEARCH_LENGTH:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="entity_id too long")
    entity = db.query(Entity).filter(
        (Entity.entity_id == entity_id) | (Entity.display_name.ilike(entity_id))
    ).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    name = entity.display_name
    descriptions = _load_entity_descriptions()
    money_flows = db.query(MoneyFlow).filter(
        (MoneyFlow.source == name) | (MoneyFlow.target == name),
    ).all()
    materials_flows = db.query(MaterialsFlow).filter(
        (MaterialsFlow.source == name) | (MaterialsFlow.target == name),
    ).all()
    relationships = db.query(Relationship).filter(
        (Relationship.source == name) | (Relationship.target == name),
    ).all()
    # Group relationships by type
    by_type: Dict[str, List[dict]] = defaultdict(list)
    for r in relationships:
        other = r.target if r.source == name else r.source
        rel_type = r.relationship_type or r.label or "related"
        by_type[rel_type].append({
            "source": r.source,
            "target": r.target,
            "description": r.description,
            "relationship_type": r.relationship_type,
        })
    return {
        "entity_id": entity.entity_id,
        "display_name": entity.display_name,
        "entity_type": entity.entity_type,
        "intel_stack_level": entity.intel_stack_level,
        "description": descriptions.get(name),
        "money_flows": [
            {"source": m.source, "target": m.target, "amount_usd": m.amount_usd, "relationship": m.relationship}
            for m in money_flows
        ],
        "materials_flows": [
            {"source": m.source, "target": m.target, "material_type": m.material_type, "relationship": m.relationship}
            for m in materials_flows
        ],
        "relationships_by_type": dict(by_type),
    }


@router.get("/intel-stack/search")
async def get_intel_stack_search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """Search entities that have intel_stack_level set. For pyramid search bar."""
    from validation import MAX_SEARCH_LENGTH
    if len(q) > MAX_SEARCH_LENGTH:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query too long")
    pattern = f"%{q.strip()}%"
    entities = db.query(Entity).filter(
        Entity.intel_stack_level.isnot(None),
        (Entity.display_name.ilike(pattern)) | (Entity.normalized_name.ilike(pattern)),
    ).limit(limit).all()
    return {
        "results": [
            {
                "entity_id": e.entity_id,
                "display_name": e.display_name,
                "entity_type": e.entity_type,
                "intel_stack_level": e.intel_stack_level,
            }
            for e in entities
        ]
    }
