"""
Analysis API routes for graph data and relationship exploration
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Entity, MoneyFlow, Relationship
from models.schemas import GraphData, GraphNode, GraphEdge

# Import database dependency
from dependencies import get_db

router = APIRouter()


@router.get("/graph/entities", response_model=GraphData)
async def get_entity_graph(
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get entity relationship graph data"""
    # Get all relationships first to know which entities to include
    relationships = db.query(Relationship).limit(limit * 2).all()
    
    # Get all entities
    all_entities = db.query(Entity).all()
    
    # Create a mapping of names to entities for lookup
    entity_map = {}
    for e in all_entities:
        # Map by display name, normalized name, and id
        if e.display_name:
            entity_map[e.display_name] = e
            entity_map[e.display_name.lower()] = e
        if e.normalized_name:
            entity_map[e.normalized_name] = e
        entity_map[e.entity_id] = e
    
    # Extract all unique entity names from relationships
    entity_names_in_graph = set()
    for r in relationships:
        entity_names_in_graph.add(r.source)
        entity_names_in_graph.add(r.target)
    
    # Calculate connection counts
    connection_counts = {}
    for r in relationships:
        connection_counts[r.source] = connection_counts.get(r.source, 0) + 1
        connection_counts[r.target] = connection_counts.get(r.target, 0) + 1
    
    # Create nodes - use entity names as IDs to match relationships
    nodes = []
    seen_names = set()
    
    for entity_name in entity_names_in_graph:
        if entity_name in seen_names:
            continue
        seen_names.add(entity_name)
        
        # Try to find the entity in our database
        entity = entity_map.get(entity_name) or entity_map.get(entity_name.lower())
        
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
        
        nodes.append(
            GraphNode(
                id=entity_name,  # Use name as ID to match relationships
                name=entity_name,
                type=entity_type,
                value=node_value
            )
        )
    
    # Create edges using entity names (which now match node IDs)
    edges = [
        GraphEdge(
            source=r.source,
            target=r.target,
            label=r.label
        )
        for r in relationships
    ]
    
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
