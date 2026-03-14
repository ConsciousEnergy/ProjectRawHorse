"""
Network Metrics Service

Calculate network centrality, betweenness, and community detection metrics
for entity relationship networks and financial flow networks.

Uses NetworkX for graph analysis algorithms.
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from database import Entity, Relationship, MoneyFlow


def build_entity_graph(db: Session, include_money_flows: bool = False) -> nx.Graph:
    """
    Build NetworkX graph from entity relationships.
    
    Args:
        db: Database session
        include_money_flows: If True, include money flows as weighted edges
    
    Returns:
        NetworkX Graph object
    """
    G = nx.Graph()
    
    # Add nodes from entities
    entities = db.query(Entity).all()
    for entity in entities:
        G.add_node(
            entity.display_name,
            entity_id=entity.entity_id,
            entity_type=entity.entity_type or 'Unknown'
        )
    
    # Add edges from relationships
    relationships = db.query(Relationship).all()
    for rel in relationships:
        if rel.source and rel.target:
            G.add_edge(
                rel.source,
                rel.target,
                relationship_type='structural',
                label=rel.label or ''
            )
    
    # Optionally add weighted edges from money flows
    if include_money_flows:
        flows = db.query(MoneyFlow).filter(MoneyFlow.amount_usd.isnot(None)).all()
        for flow in flows:
            if flow.source and flow.target and flow.amount_usd:
                # If edge already exists, add to weight; otherwise create new edge
                if G.has_edge(flow.source, flow.target):
                    G[flow.source][flow.target]['weight'] = G[flow.source][flow.target].get('weight', 0) + flow.amount_usd
                    G[flow.source][flow.target]['relationship_type'] = 'hybrid'
                else:
                    G.add_edge(
                        flow.source,
                        flow.target,
                        weight=flow.amount_usd,
                        relationship_type='financial'
                    )
    
    return G


def build_directed_flow_graph(db: Session) -> nx.DiGraph:
    """
    Build directed graph from money flows (for flow analysis).
    
    Args:
        db: Database session
    
    Returns:
        NetworkX DiGraph object
    """
    G = nx.DiGraph()
    
    # Add nodes from unique entities in flows
    flows = db.query(MoneyFlow).filter(MoneyFlow.amount_usd.isnot(None)).all()
    
    entity_names = set()
    for flow in flows:
        if flow.source:
            entity_names.add(flow.source)
        if flow.target:
            entity_names.add(flow.target)
    
    for name in entity_names:
        G.add_node(name)
    
    # Add weighted directed edges
    for flow in flows:
        if flow.source and flow.target and flow.amount_usd:
            if G.has_edge(flow.source, flow.target):
                G[flow.source][flow.target]['weight'] += flow.amount_usd
            else:
                G.add_edge(flow.source, flow.target, weight=flow.amount_usd)
    
    return G


def calculate_centrality_metrics(G: nx.Graph) -> Dict[str, Dict[str, float]]:
    """
    Calculate various centrality metrics for all nodes.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dictionary mapping node names to centrality metrics
    """
    if len(G) == 0:
        return {}
    
    metrics = {}
    
    # Degree centrality (normalized by max possible connections)
    degree_centrality = nx.degree_centrality(G)
    
    # Betweenness centrality (measures how often node appears on shortest paths)
    try:
        betweenness_centrality = nx.betweenness_centrality(G)
    except:
        betweenness_centrality = {node: 0.0 for node in G.nodes()}
    
    # Closeness centrality (inverse of average distance to all other nodes)
    try:
        closeness_centrality = nx.closeness_centrality(G)
    except:
        closeness_centrality = {node: 0.0 for node in G.nodes()}
    
    # Eigenvector centrality (considers importance of neighbors)
    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eigenvector_centrality = {node: 0.0 for node in G.nodes()}
    
    # Combine all metrics
    for node in G.nodes():
        metrics[node] = {
            'degree_centrality': degree_centrality.get(node, 0.0),
            'betweenness_centrality': betweenness_centrality.get(node, 0.0),
            'closeness_centrality': closeness_centrality.get(node, 0.0),
            'eigenvector_centrality': eigenvector_centrality.get(node, 0.0),
            'degree': G.degree(node)
        }
    
    return metrics


def calculate_weighted_centrality(G: nx.Graph) -> Dict[str, Dict[str, float]]:
    """
    Calculate centrality metrics considering edge weights (for financial flows).
    
    Args:
        G: NetworkX graph with 'weight' attributes on edges
    
    Returns:
        Dictionary mapping node names to weighted centrality metrics
    """
    if len(G) == 0:
        return {}
    
    metrics = {}
    
    # Weighted degree (sum of edge weights)
    weighted_degree = {}
    for node in G.nodes():
        total_weight = sum(G[node][neighbor].get('weight', 1.0) for neighbor in G.neighbors(node))
        weighted_degree[node] = total_weight
    
    # Betweenness centrality with weights
    try:
        betweenness = nx.betweenness_centrality(G, weight='weight')
    except:
        betweenness = {node: 0.0 for node in G.nodes()}
    
    # PageRank (considers edge weights)
    try:
        pagerank = nx.pagerank(G, weight='weight')
    except:
        pagerank = {node: 1.0 / len(G) for node in G.nodes()}
    
    for node in G.nodes():
        metrics[node] = {
            'weighted_degree': weighted_degree.get(node, 0.0),
            'weighted_betweenness': betweenness.get(node, 0.0),
            'pagerank': pagerank.get(node, 0.0)
        }
    
    return metrics


def detect_communities(G: nx.Graph) -> Dict[str, int]:
    """
    Detect communities/clusters in the network using Louvain algorithm.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dictionary mapping node names to community IDs
    """
    if len(G) == 0:
        return {}
    
    # Use Louvain method for community detection (requires python-louvain or networkx communities)
    try:
        # NetworkX's built-in greedy modularity communities
        communities = nx.community.greedy_modularity_communities(G)
        
        # Map nodes to community IDs
        node_to_community = {}
        for community_id, community in enumerate(communities):
            for node in community:
                node_to_community[node] = community_id
        
        return node_to_community
    except Exception as e:
        print(f"Community detection failed: {e}")
        # Fallback: each node in its own community
        return {node: i for i, node in enumerate(G.nodes())}


def calculate_network_stats(G: nx.Graph) -> Dict:
    """
    Calculate overall network statistics.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dictionary of network-level statistics
    """
    if len(G) == 0:
        return {
            'num_nodes': 0,
            'num_edges': 0,
            'density': 0.0,
            'avg_degree': 0.0,
            'num_components': 0,
            'largest_component_size': 0,
            'avg_clustering': 0.0,
            'transitivity': 0.0
        }
    
    # Basic stats
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)
    
    # Degree statistics
    degrees = [deg for node, deg in G.degree()]
    avg_degree = sum(degrees) / len(degrees) if degrees else 0.0
    
    # Connected components
    components = list(nx.connected_components(G))
    num_components = len(components)
    largest_component_size = len(max(components, key=len)) if components else 0
    
    # Clustering
    try:
        avg_clustering = nx.average_clustering(G)
    except:
        avg_clustering = 0.0
    
    try:
        transitivity = nx.transitivity(G)
    except:
        transitivity = 0.0
    
    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'density': density,
        'avg_degree': avg_degree,
        'num_components': num_components,
        'largest_component_size': largest_component_size,
        'largest_component_pct': (largest_component_size / num_nodes * 100) if num_nodes > 0 else 0.0,
        'avg_clustering': avg_clustering,
        'transitivity': transitivity
    }


def get_hub_nodes(centrality_metrics: Dict[str, Dict[str, float]], top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Identify hub nodes (highly connected/important nodes).
    
    Args:
        centrality_metrics: Output from calculate_centrality_metrics
        top_n: Number of top hubs to return
    
    Returns:
        List of (node_name, combined_score) tuples
    """
    if not centrality_metrics:
        return []
    
    # Combine multiple centrality measures for overall importance score
    hub_scores = {}
    for node, metrics in centrality_metrics.items():
        # Weighted combination of different centrality measures
        score = (
            metrics['degree_centrality'] * 0.3 +
            metrics['betweenness_centrality'] * 0.3 +
            metrics['eigenvector_centrality'] * 0.2 +
            metrics['closeness_centrality'] * 0.2
        )
        hub_scores[node] = score
    
    # Sort and return top N
    sorted_hubs = sorted(hub_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_hubs[:top_n]


def get_bridge_nodes(centrality_metrics: Dict[str, Dict[str, float]], top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Identify bridge nodes (nodes that connect different parts of network).
    
    Args:
        centrality_metrics: Output from calculate_centrality_metrics
        top_n: Number of top bridges to return
    
    Returns:
        List of (node_name, betweenness_score) tuples
    """
    if not centrality_metrics:
        return []
    
    # Sort by betweenness centrality (indicates bridging role)
    bridge_scores = [(node, metrics['betweenness_centrality']) 
                     for node, metrics in centrality_metrics.items()]
    
    sorted_bridges = sorted(bridge_scores, key=lambda x: x[1], reverse=True)
    return sorted_bridges[:top_n]

