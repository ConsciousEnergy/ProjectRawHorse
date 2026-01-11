"""
Analysis API routes for graph data and relationship exploration
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Entity, MoneyFlow, Relationship, Award
from models.schemas import GraphData, GraphNode, GraphEdge
from collections import defaultdict

# Import database dependency
from dependencies import get_db

router = APIRouter()


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
    limit: int = Query(500, le=1000),
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
            from data_loader import infer_entity_type
            entity_type = infer_entity_type(entity_name)
        
        # Get full name for acronyms
        from data_loader import AGENCY_ACRONYMS
        full_name = AGENCY_ACRONYMS.get(entity_name.strip().upper())
        
        nodes.append(
            GraphNode(
                id=entity_name,  # Use name as ID to match relationships
                name=entity_name,
                type=entity_type,
                value=node_value,
                full_name=full_name
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
    min_amount: float = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get money flow graph data"""
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
    """Get all relationships for a specific entity"""
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
