"""
Multi-hop flow tracing service for tracking money through multiple levels
"""
from typing import List, Dict, Set, Optional, Tuple
from sqlalchemy.orm import Session
from collections import deque
import logging

from database import MoneyFlow, Relationship, Entity

logger = logging.getLogger(__name__)


class FlowPath:
    """Represents a path through the money flow network"""
    
    def __init__(self):
        self.entities: List[str] = []
        self.amounts: List[float] = []
        self.relationships: List[str] = []
        self.total_amount: float = 0.0
    
    def add_step(self, entity: str, amount: float, relationship: str = ""):
        """Add a step to the path"""
        self.entities.append(entity)
        self.amounts.append(amount)
        if relationship:
            self.relationships.append(relationship)
        self.total_amount += amount
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "path": self.entities,
            "amounts": self.amounts,
            "relationships": self.relationships,
            "total_amount": self.total_amount,
            "hops": len(self.entities) - 1
        }


def trace_money_flows_bfs(
    db: Session,
    source: str,
    target: str,
    max_hops: int = 5,
    min_amount: float = 0.0
) -> List[Dict]:
    """
    Trace all paths from source to target using breadth-first search.
    
    Args:
        db: Database session
        source: Source entity name
        target: Target entity name
        max_hops: Maximum number of hops to explore
        min_amount: Minimum amount threshold for including edges
    
    Returns:
        List of path dictionaries containing entities, amounts, and relationships
    """
    # Build adjacency list from money flows
    flows = db.query(MoneyFlow).filter(
        MoneyFlow.amount_usd.isnot(None),
        MoneyFlow.amount_usd >= min_amount
    ).all()
    
    # Create graph structure: source -> [(target, amount, relationship)]
    graph: Dict[str, List[Tuple[str, float, str]]] = {}
    for flow in flows:
        if not flow.source or not flow.target:
            continue
        
        if flow.source not in graph:
            graph[flow.source] = []
        
        graph[flow.source].append((
            flow.target,
            flow.amount_usd or 0.0,
            flow.relationship or ""
        ))
    
    # Normalize source and target names (case-insensitive)
    source_lower = source.lower().strip()
    target_lower = target.lower().strip()
    
    # Find actual keys in graph (handle case variations)
    actual_source = None
    actual_target = None
    for key in graph.keys():
        if key.lower().strip() == source_lower:
            actual_source = key
        if key.lower().strip() == target_lower:
            actual_target = key
    
    if not actual_source:
        logger.warning(f"Source entity '{source}' not found in money flow graph")
        return []
    
    # BFS to find all paths
    paths: List[FlowPath] = []
    queue = deque([(actual_source, FlowPath(), 0)])  # (current_entity, path, hop_count)
    visited_in_path: Set[str] = set()
    
    while queue:
        current, path, hops = queue.popleft()
        
        # Create new path for this branch
        new_path = FlowPath()
        new_path.entities = path.entities.copy()
        new_path.amounts = path.amounts.copy()
        new_path.relationships = path.relationships.copy()
        new_path.total_amount = path.total_amount
        
        # Add current entity if not first
        if not new_path.entities:
            new_path.entities.append(current)
        
        # Check if we've reached the target
        if current.lower().strip() == target_lower:
            if len(new_path.entities) > 1:  # Must have at least source and target
                paths.append(new_path)
            continue
        
        # Check hop limit
        if hops >= max_hops:
            continue
        
        # Explore neighbors
        if current in graph:
            for neighbor, amount, relationship in graph[current]:
                # Avoid cycles
                if neighbor in new_path.entities:
                    continue
                
                # Create path for this branch
                branch_path = FlowPath()
                branch_path.entities = new_path.entities.copy()
                branch_path.amounts = new_path.amounts.copy()
                branch_path.relationships = new_path.relationships.copy()
                branch_path.total_amount = new_path.total_amount
                
                branch_path.add_step(neighbor, amount, relationship)
                
                queue.append((neighbor, branch_path, hops + 1))
    
    # Convert paths to dictionaries and sort by total amount
    result = [p.to_dict() for p in paths]
    result.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return result


def get_critical_intermediaries(
    db: Session,
    source: str,
    target: str,
    max_hops: int = 5
) -> List[Dict]:
    """
    Find entities that are critical intermediaries between source and target.
    
    An entity is critical if it appears in multiple paths or if removing it
    would significantly reduce the number of paths.
    
    Returns:
        List of intermediary entities with their frequency and total flow
    """
    paths = trace_money_flows_bfs(db, source, target, max_hops)
    
    if not paths:
        return []
    
    # Count entity appearances (excluding source and target)
    intermediary_counts: Dict[str, Dict] = {}
    
    for path in paths:
        entities = path['path']
        amounts = path['amounts']
        
        # Skip source and target
        for i, entity in enumerate(entities[1:-1], start=1):
            if entity not in intermediary_counts:
                intermediary_counts[entity] = {
                    'entity': entity,
                    'path_count': 0,
                    'total_flow': 0.0
                }
            
            intermediary_counts[entity]['path_count'] += 1
            if i < len(amounts):
                intermediary_counts[entity]['total_flow'] += amounts[i]
    
    # Sort by path count (most critical first)
    result = list(intermediary_counts.values())
    result.sort(key=lambda x: (x['path_count'], x['total_flow']), reverse=True)
    
    return result


def detect_circular_flows(
    db: Session,
    entity: str,
    max_hops: int = 4
) -> List[Dict]:
    """
    Detect circular money flows starting and ending at the same entity.
    
    Args:
        db: Database session
        entity: Entity to check for circular flows
        max_hops: Maximum number of hops in the cycle
    
    Returns:
        List of circular paths (cycles)
    """
    # Find paths that start and end at the same entity
    cycles = trace_money_flows_bfs(db, entity, entity, max_hops)
    
    # Filter out trivial cycles (length 1)
    cycles = [c for c in cycles if len(c['path']) > 2]
    
    return cycles


def get_flow_summary(
    db: Session,
    source: str,
    target: str,
    max_hops: int = 5
) -> Dict:
    """
    Get a comprehensive summary of money flows between two entities.
    
    Returns:
        Dictionary with paths, total amounts, intermediaries, and statistics
    """
    paths = trace_money_flows_bfs(db, source, target, max_hops)
    intermediaries = get_critical_intermediaries(db, source, target, max_hops)
    
    if not paths:
        return {
            'source': source,
            'target': target,
            'paths_found': 0,
            'paths': [],
            'total_flow': 0.0,
            'intermediaries': [],
            'statistics': {}
        }
    
    # Calculate statistics
    total_flow = sum(p['total_amount'] for p in paths)
    avg_flow = total_flow / len(paths) if paths else 0.0
    max_flow = max((p['total_amount'] for p in paths), default=0.0)
    min_flow = min((p['total_amount'] for p in paths), default=0.0)
    avg_hops = sum(p['hops'] for p in paths) / len(paths) if paths else 0.0
    
    return {
        'source': source,
        'target': target,
        'paths_found': len(paths),
        'paths': paths[:20],  # Limit to top 20 paths
        'total_flow': total_flow,
        'intermediaries': intermediaries[:10],  # Top 10 intermediaries
        'statistics': {
            'avg_flow_per_path': avg_flow,
            'max_flow': max_flow,
            'min_flow': min_flow,
            'avg_hops': avg_hops
        }
    }

