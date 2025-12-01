"""
Analysis API routes for graph data and relationship exploration
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Entity, MoneyFlow, Relationship, Award
from models.schemas import GraphData, GraphNode, GraphEdge

# Import database dependency
from dependencies import get_db

# Import network metrics service
from services import network_metrics

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
    """Get money flow graph data (individual flows, not aggregated)"""
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


@router.get("/money-flow-graph", response_model=GraphData)
async def get_weighted_money_flow_graph(
    min_amount: float = Query(None, description="Minimum total amount to include edge"),
    db: Session = Depends(get_db)
):
    """
    Get weighted money flow graph with aggregated edges.
    
    Aggregates all money flows by source-target pair and returns:
    - Nodes with entity information and types
    - Weighted edges with total amounts per source-target pair
    """
    # Get all money flows
    query = db.query(MoneyFlow).filter(MoneyFlow.amount_usd.isnot(None))
    flows = query.all()
    
    # Aggregate flows by source-target pair
    flow_aggregates: Dict[tuple, Dict] = {}
    entity_totals: Dict[str, float] = {}  # Track total flow per entity
    
    for flow in flows:
        if not flow.source or not flow.target or not flow.amount_usd:
            continue
        
        key = (flow.source, flow.target)
        
        if key not in flow_aggregates:
            flow_aggregates[key] = {
                'source': flow.source,
                'target': flow.target,
                'total_amount': 0.0,
                'flow_count': 0,
                'relationships': set()
            }
        
        flow_aggregates[key]['total_amount'] += flow.amount_usd
        flow_aggregates[key]['flow_count'] += 1
        if flow.relationship:
            flow_aggregates[key]['relationships'].add(flow.relationship)
        
        # Track entity totals for node sizing
        entity_totals[flow.source] = entity_totals.get(flow.source, 0.0) + flow.amount_usd
        entity_totals[flow.target] = entity_totals.get(flow.target, 0.0) + flow.amount_usd
    
    # Filter by minimum amount if specified
    if min_amount:
        flow_aggregates = {
            k: v for k, v in flow_aggregates.items()
            if v['total_amount'] >= min_amount
        }
    
    # Get all entities from database for type information
    all_entities = db.query(Entity).all()
    entity_map = {}
    for e in all_entities:
        if e.display_name:
            entity_map[e.display_name] = e
            entity_map[e.display_name.lower()] = e
        if e.normalized_name:
            entity_map[e.normalized_name] = e
    
    # Create nodes from unique entities involved in flows
    entity_names = set()
    for key in flow_aggregates.keys():
        entity_names.add(key[0])  # source
        entity_names.add(key[1])  # target
    
    nodes = []
    for name in entity_names:
        entity = entity_map.get(name) or entity_map.get(name.lower())
        
        # Determine entity type
        if entity and entity.entity_type:
            entity_type = entity.entity_type
        else:
            from data_loader import infer_entity_type
            entity_type = infer_entity_type(name)
        
        # Size node by total money flow (log scale)
        import math
        total_flow = entity_totals.get(name, 0.0)
        node_value = 8 + (math.log10(max(total_flow, 1)) * 2)  # Log scale sizing
        node_value = min(max(node_value, 8), 30)  # Clamp between 8 and 30
        
        # Get full name for acronyms
        from data_loader import AGENCY_ACRONYMS
        full_name = AGENCY_ACRONYMS.get(name.strip().upper())
        
        nodes.append(
            GraphNode(
                id=name,
                name=name,
                type=entity_type,
                value=node_value,
                full_name=full_name
            )
        )
    
    # Create weighted edges
    edges = []
    for agg in flow_aggregates.values():
        # Create label from relationships
        label = ", ".join(sorted(agg['relationships'])) if agg['relationships'] else "Money Flow"
        if agg['flow_count'] > 1:
            label += f" ({agg['flow_count']} flows)"
        
        edges.append(
            GraphEdge(
                source=agg['source'],
                target=agg['target'],
                value=agg['total_amount'],
                label=label
            )
        )
    
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


@router.get("/top-recipients")
async def get_top_recipients(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get top recipients by total amount from both awards and money flows."""
    # Aggregate from money flows
    flow_recipients = db.query(
        MoneyFlow.target.label('entity'),
        func.sum(MoneyFlow.amount_usd).label('total')
    ).filter(
        MoneyFlow.amount_usd.isnot(None)
    ).group_by(MoneyFlow.target).all()
    
    # Aggregate from awards
    award_recipients = db.query(
        Award.recipient_name.label('entity'),
        func.sum(Award.award_amount).label('total')
    ).filter(
        Award.award_amount.isnot(None)
    ).group_by(Award.recipient_name).all()
    
    # Combine and sum by entity
    entity_totals = {}
    for entity, total in flow_recipients:
        if entity:
            entity_totals[entity] = entity_totals.get(entity, 0) + (total or 0)
    
    for entity, total in award_recipients:
        if entity:
            entity_totals[entity] = entity_totals.get(entity, 0) + (total or 0)
    
    # Sort and limit
    sorted_recipients = sorted(entity_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return {
        "recipients": [
            {"entity": entity, "amount": float(amount)}
            for entity, amount in sorted_recipients
        ]
    }


@router.get("/agency-breakdown")
async def get_agency_breakdown(
    db: Session = Depends(get_db)
):
    """Get spending breakdown by agency."""
    # From money flows (source = agency)
    flow_agencies = db.query(
        MoneyFlow.source.label('agency'),
        func.sum(MoneyFlow.amount_usd).label('total')
    ).filter(
        MoneyFlow.amount_usd.isnot(None)
    ).group_by(MoneyFlow.source).all()
    
    # From awards
    award_agencies = db.query(
        Award.awarding_agency.label('agency'),
        func.sum(Award.award_amount).label('total')
    ).filter(
        Award.award_amount.isnot(None)
    ).group_by(Award.awarding_agency).all()
    
    # Combine
    agency_totals = {}
    for agency, total in flow_agencies:
        if agency:
            agency_totals[agency] = agency_totals.get(agency, 0) + (total or 0)
    
    for agency, total in award_agencies:
        if agency:
            agency_totals[agency] = agency_totals.get(agency, 0) + (total or 0)
    
    # Sort by amount
    sorted_agencies = sorted(agency_totals.items(), key=lambda x: x[1], reverse=True)
    
    total_spending = sum(amount for _, amount in sorted_agencies)
    
    return {
        "agencies": [
            {
                "agency": agency,
                "amount": float(amount),
                "percentage": (float(amount) / total_spending * 100) if total_spending > 0 else 0
            }
            for agency, amount in sorted_agencies
        ],
        "total": float(total_spending)
    }


@router.get("/flow-distribution")
async def get_flow_distribution(
    db: Session = Depends(get_db)
):
    """Get distribution statistics for money flows and awards."""
    import statistics
    
    # Get all amounts
    flow_amounts = [f.amount_usd for f in db.query(MoneyFlow.amount_usd).filter(MoneyFlow.amount_usd.isnot(None)).all()]
    award_amounts = [a.award_amount for a in db.query(Award.award_amount).filter(Award.award_amount.isnot(None)).all()]
    
    all_amounts = flow_amounts + award_amounts
    
    if not all_amounts:
        return {
            "count": 0,
            "total": 0,
            "mean": 0,
            "median": 0,
            "min": 0,
            "max": 0,
            "std_dev": 0,
            "distribution_bins": []
        }
    
    # Calculate statistics
    total = sum(all_amounts)
    mean = statistics.mean(all_amounts)
    median = statistics.median(all_amounts)
    min_amount = min(all_amounts)
    max_amount = max(all_amounts)
    std_dev = statistics.stdev(all_amounts) if len(all_amounts) > 1 else 0
    
    # Create distribution bins (log scale for better visualization)
    import math
    bins = [0, 1000, 10000, 100000, 1000000, 10000000, 100000000, float('inf')]
    bin_labels = ['<$1K', '$1K-$10K', '$10K-$100K', '$100K-$1M', '$1M-$10M', '$10M-$100M', '>$100M']
    
    distribution = [0] * len(bin_labels)
    for amount in all_amounts:
        for i, upper_bound in enumerate(bins[1:]):
            if bins[i] <= amount < upper_bound:
                distribution[i] += 1
                break
    
    return {
        "count": len(all_amounts),
        "total": float(total),
        "mean": float(mean),
        "median": float(median),
        "min": float(min_amount),
        "max": float(max_amount),
        "std_dev": float(std_dev),
        "distribution_bins": [
            {"label": label, "count": count}
            for label, count in zip(bin_labels, distribution)
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


@router.get("/spending-timeline")
async def get_spending_timeline(
    group_by: str = Query('year', regex='^(year|month|quarter)$'),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive spending timeline from both awards and money flows.
    
    Args:
        group_by: Time period grouping - 'year', 'month', or 'quarter'
    
    Returns:
        Timeline data with spending by period and agency
    """
    # Query awards data
    if group_by == 'year':
        time_format = '%Y'
    elif group_by == 'month':
        time_format = '%Y-%m'
    else:  # quarter
        time_format = '%Y-Q'
    
    # Awards timeline
    awards_timeline = db.query(
        func.strftime(time_format, Award.action_date).label('period'),
        Award.awarding_agency.label('agency'),
        func.count(Award.id).label('count'),
        func.sum(Award.award_amount).label('total')
    ).filter(
        Award.action_date.isnot(None),
        Award.award_amount.isnot(None)
    ).group_by('period', 'agency').order_by('period').all()
    
    # Money flows timeline
    flows_timeline = db.query(
        func.strftime(time_format, MoneyFlow.start_date).label('period'),
        MoneyFlow.source.label('agency'),
        func.count(MoneyFlow.id).label('count'),
        func.sum(MoneyFlow.amount_usd).label('total')
    ).filter(
        MoneyFlow.start_date.isnot(None),
        MoneyFlow.amount_usd.isnot(None)
    ).group_by('period', 'agency').order_by('period').all()
    
    # Combine and aggregate by period
    period_data = {}
    agency_totals = {}
    
    for row in awards_timeline:
        period, agency, count, total = row
        if not period:
            continue
        
        if period not in period_data:
            period_data[period] = {'period': period, 'total': 0, 'agencies': {}}
        
        agency_name = agency or 'Unknown'
        period_data[period]['agencies'][agency_name] = period_data[period]['agencies'].get(agency_name, 0) + (total or 0)
        period_data[period]['total'] += (total or 0)
        agency_totals[agency_name] = agency_totals.get(agency_name, 0) + (total or 0)
    
    for row in flows_timeline:
        period, source, count, total = row
        if not period:
            continue
        
        if period not in period_data:
            period_data[period] = {'period': period, 'total': 0, 'agencies': {}}
        
        source_name = source or 'Unknown'
        period_data[period]['agencies'][source_name] = period_data[period]['agencies'].get(source_name, 0) + (total or 0)
        period_data[period]['total'] += (total or 0)
        agency_totals[source_name] = agency_totals.get(source_name, 0) + (total or 0)
    
    # Sort by period and format for frontend
    timeline = []
    for period in sorted(period_data.keys()):
        data = period_data[period]
        timeline_entry = {
            'period': period,
            'total': float(data['total']),
        }
        # Add each agency as a separate field for stacked charts
        for agency, amount in data['agencies'].items():
            timeline_entry[agency] = float(amount)
        timeline.append(timeline_entry)
    
    # Get top agencies for legend
    top_agencies = sorted(agency_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "timeline": timeline,
        "top_agencies": [{"name": name, "total": float(total)} for name, total in top_agencies],
        "group_by": group_by
    }


@router.get("/network-metrics")
async def get_network_metrics(
    include_financial: bool = Query(False, description="Include money flows as weighted edges"),
    db: Session = Depends(get_db)
):
    """
    Calculate network centrality and community detection metrics.
    
    Args:
        include_financial: If True, includes money flows as weighted edges
    
    Returns:
        Network metrics including centrality, communities, and network statistics
    """
    # Build graph
    G = network_metrics.build_entity_graph(db, include_money_flows=include_financial)
    
    if len(G) == 0:
        return {
            "error": "No network data available",
            "num_nodes": 0,
            "num_edges": 0
        }
    
    # Calculate centrality metrics
    centrality = network_metrics.calculate_centrality_metrics(G)
    
    # Detect communities
    communities = network_metrics.detect_communities(G)
    
    # Calculate network statistics
    stats = network_metrics.calculate_network_stats(G)
    
    # Identify hub and bridge nodes
    hubs = network_metrics.get_hub_nodes(centrality, top_n=10)
    bridges = network_metrics.get_bridge_nodes(centrality, top_n=10)
    
    # Count nodes per community
    community_sizes = {}
    for node, community_id in communities.items():
        community_sizes[community_id] = community_sizes.get(community_id, 0) + 1
    
    return {
        "network_stats": stats,
        "top_hubs": [{"entity": name, "score": float(score)} for name, score in hubs],
        "top_bridges": [{"entity": name, "betweenness": float(score)} for name, score in bridges],
        "num_communities": len(set(communities.values())),
        "community_sizes": community_sizes,
        "centrality_available": True
    }


@router.get("/network-metrics/centrality/{entity_name}")
async def get_entity_centrality(
    entity_name: str,
    db: Session = Depends(get_db)
):
    """
    Get centrality metrics for a specific entity.
    
    Args:
        entity_name: Name of the entity
    
    Returns:
        Centrality metrics for the specified entity
    """
    # Build graph
    G = network_metrics.build_entity_graph(db, include_money_flows=True)
    
    if entity_name not in G.nodes():
        return {"error": f"Entity '{entity_name}' not found in network"}
    
    # Calculate centrality
    centrality = network_metrics.calculate_centrality_metrics(G)
    
    # Get community
    communities = network_metrics.detect_communities(G)
    
    # Get neighbors
    neighbors = list(G.neighbors(entity_name))
    
    return {
        "entity": entity_name,
        "metrics": centrality.get(entity_name, {}),
        "community_id": communities.get(entity_name),
        "neighbors": neighbors,
        "num_neighbors": len(neighbors)
    }


@router.get("/network-metrics/weighted")
async def get_weighted_network_metrics(
    db: Session = Depends(get_db)
):
    """
    Calculate weighted network metrics based on financial flows.
    
    Returns:
        Weighted centrality metrics considering transaction amounts
    """
    # Build financial flow graph with weights
    G = network_metrics.build_entity_graph(db, include_money_flows=True)
    
    if len(G) == 0:
        return {
            "error": "No financial flow data available",
            "num_nodes": 0
        }
    
    # Calculate weighted centrality
    weighted_centrality = network_metrics.calculate_weighted_centrality(G)
    
    # Sort by PageRank (financial importance)
    sorted_by_pagerank = sorted(
        weighted_centrality.items(),
        key=lambda x: x[1]['pagerank'],
        reverse=True
    )[:20]
    
    # Sort by weighted degree (total flow amount)
    sorted_by_flow = sorted(
        weighted_centrality.items(),
        key=lambda x: x[1]['weighted_degree'],
        reverse=True
    )[:20]
    
    return {
        "top_by_pagerank": [
            {"entity": name, "pagerank": float(metrics['pagerank']), 
             "weighted_degree": float(metrics['weighted_degree'])}
            for name, metrics in sorted_by_pagerank
        ],
        "top_by_flow_amount": [
            {"entity": name, "total_flow": float(metrics['weighted_degree']),
             "pagerank": float(metrics['pagerank'])}
            for name, metrics in sorted_by_flow
        ]
    }


@router.get("/network-metrics/communities")
async def get_network_communities(
    db: Session = Depends(get_db)
):
    """
    Get detailed community detection results.
    
    Returns:
        Communities with member lists and statistics
    """
    # Build graph
    G = network_metrics.build_entity_graph(db, include_money_flows=True)
    
    if len(G) == 0:
        return {"error": "No network data available"}
    
    # Detect communities
    communities = network_metrics.detect_communities(G)
    
    # Group nodes by community
    community_members = {}
    for node, community_id in communities.items():
        if community_id not in community_members:
            community_members[community_id] = []
        community_members[community_id].append(node)
    
    # Calculate metrics per community
    community_info = []
    for community_id, members in community_members.items():
        # Get subgraph for this community
        subgraph = G.subgraph(members)
        
        community_info.append({
            "community_id": community_id,
            "size": len(members),
            "members": members[:10],  # Show first 10
            "num_internal_edges": subgraph.number_of_edges(),
            "density": network_metrics.calculate_network_stats(subgraph)['density']
        })
    
    # Sort by size
    community_info.sort(key=lambda x: x['size'], reverse=True)
    
    return {
        "num_communities": len(community_members),
        "communities": community_info
    }


# Flow Tracing Endpoints

@router.get("/flow-trace")
async def trace_flows(
    source: str = Query(..., description="Source entity name"),
    target: str = Query(..., description="Target entity name"),
    max_hops: int = Query(5, ge=1, le=10, description="Maximum number of hops"),
    min_amount: float = Query(0, ge=0, description="Minimum flow amount"),
    db: Session = Depends(get_db)
):
    """
    Trace all paths between two entities through money flows.
    
    Returns all paths found, their amounts, and intermediary entities.
    """
    from services import flow_tracer
    
    summary = flow_tracer.get_flow_summary(db, source, target, max_hops)
    
    return summary


@router.get("/flow-trace/intermediaries")
async def get_intermediaries(
    source: str = Query(..., description="Source entity name"),
    target: str = Query(..., description="Target entity name"),
    max_hops: int = Query(5, ge=1, le=10, description="Maximum number of hops"),
    db: Session = Depends(get_db)
):
    """
    Find critical intermediary entities between source and target.
    
    Returns entities that appear in multiple paths or control significant flows.
    """
    from services import flow_tracer
    
    intermediaries = flow_tracer.get_critical_intermediaries(db, source, target, max_hops)
    
    return {
        "source": source,
        "target": target,
        "intermediaries": intermediaries
    }


@router.get("/flow-trace/circular")
async def detect_circular(
    entity: str = Query(..., description="Entity to check for circular flows"),
    max_hops: int = Query(4, ge=2, le=8, description="Maximum cycle length"),
    db: Session = Depends(get_db)
):
    """
    Detect circular money flows (cycles) involving the specified entity.
    
    Returns paths that start and end at the same entity.
    """
    from services import flow_tracer
    
    cycles = flow_tracer.detect_circular_flows(db, entity, max_hops)
    
    return {
        "entity": entity,
        "cycles_found": len(cycles),
        "cycles": cycles
    }


# Pattern Detection Endpoints

@router.get("/patterns/spikes")
async def detect_spikes(
    entity: str = Query(None, description="Optional entity to filter by"),
    threshold: float = Query(2.0, ge=1.0, le=5.0, description="Standard deviations for anomaly threshold"),
    db: Session = Depends(get_db)
):
    """
    Detect anomalous spending spikes using statistical analysis.
    
    Returns money flows that are significantly higher than the mean.
    """
    from services import pattern_detector
    
    spikes = pattern_detector.detect_spending_spikes(db, entity, threshold)
    
    return {
        "entity": entity,
        "threshold_std_devs": threshold,
        "spikes_detected": len(spikes),
        "spikes": spikes[:20]  # Limit to top 20
    }


@router.get("/patterns/clusters")
async def detect_clusters(
    recipient: str = Query(None, description="Optional recipient to filter by"),
    window_days: int = Query(30, ge=7, le=180, description="Time window for clustering"),
    db: Session = Depends(get_db)
):
    """
    Detect temporal clustering of awards (multiple awards in short time period).
    
    Identifies periods where an entity received multiple awards rapidly.
    """
    from services import pattern_detector
    
    clusters = pattern_detector.detect_award_clustering(db, recipient, window_days)
    
    return {
        "recipient": recipient,
        "window_days": window_days,
        "clusters_detected": len(clusters),
        "clusters": clusters[:20]  # Limit to top 20
    }


@router.get("/patterns/gaps")
async def detect_gaps(
    entity: str = Query(..., description="Entity to analyze for funding gaps"),
    min_gap_days: int = Query(180, ge=30, le=730, description="Minimum gap in days"),
    db: Session = Depends(get_db)
):
    """
    Detect significant gaps in funding activity for an entity.
    
    Identifies periods where an entity had no financial activity.
    """
    from services import pattern_detector
    
    gaps = pattern_detector.detect_funding_gaps(db, entity, min_gap_days)
    
    return {
        "entity": entity,
        "min_gap_days": min_gap_days,
        "gaps_detected": len(gaps),
        "gaps": gaps
    }


@router.get("/patterns/periodic")
async def detect_periodic(
    entity: str = Query(None, description="Optional entity to filter by"),
    min_occurrences: int = Query(3, ge=2, le=10, description="Minimum occurrences for pattern"),
    db: Session = Depends(get_db)
):
    """
    Detect periodic/recurring patterns in awards or flows.
    
    Identifies entities receiving awards at regular intervals.
    """
    from services import pattern_detector
    
    patterns = pattern_detector.detect_periodic_patterns(db, entity, min_occurrences)
    
    return {
        "entity": entity,
        "min_occurrences": min_occurrences,
        "patterns_detected": len(patterns),
        "patterns": patterns[:20]  # Limit to top 20
    }


@router.get("/patterns/comprehensive")
async def comprehensive_patterns(
    entity: str = Query(None, description="Optional entity for focused analysis"),
    db: Session = Depends(get_db)
):
    """
    Run comprehensive pattern detection analysis.
    
    Returns all detected patterns and anomalies in one call.
    """
    from services import pattern_detector
    
    analysis = pattern_detector.get_comprehensive_pattern_analysis(db, entity)
    
    return analysis
