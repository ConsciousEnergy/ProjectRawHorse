"""
Detect potential duplicate entities in the database.

This script uses fuzzy name matching and identifier matching to find
potential duplicate entities that should be merged.

Usage:
    python data/scripts/detect_entity_duplicates.py --threshold 0.85
"""

import csv
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
from difflib import SequenceMatcher
from collections import defaultdict


def normalize_name(name: str) -> str:
    """Normalize entity name for comparison."""
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove common suffixes
    suffixes = [
        ' inc.', ' inc', ' llc', ' llc.', ' corp.', ' corp', ' corporation',
        ' company', ' co.', ' co', ' ltd', ' ltd.', ' limited',
        ' the', ', inc', ', llc', ', corp', ', ltd'
    ]
    
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name


def calculate_similarity(name1: str, name2: str) -> float:
    """Calculate similarity score between two names (0.0 to 1.0)."""
    if not name1 or not name2:
        return 0.0
    
    # Normalize names
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    if norm1 == norm2:
        return 1.0
    
    # Calculate sequence similarity
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    
    # Boost score if one name contains the other
    if norm1 in norm2 or norm2 in norm1:
        similarity = max(similarity, 0.85)
    
    return similarity


def check_identifier_match(entity1: Dict, entity2: Dict) -> bool:
    """Check if entities have matching identifiers (UEI, DUNS, CAGE)."""
    # Check UEI
    if entity1.get('uei') and entity2.get('uei'):
        if entity1['uei'] == entity2['uei']:
            return True
    
    # Check DUNS
    if entity1.get('duns') and entity2.get('duns'):
        if entity1['duns'] == entity2['duns']:
            return True
    
    # Check CAGE
    if entity1.get('cage') and entity2.get('cage'):
        if entity1['cage'] == entity2['cage']:
            return True
    
    return False


def detect_duplicates(
    entities: List[Dict],
    name_threshold: float = 0.85,
    check_identifiers: bool = True
) -> List[Tuple[Dict, Dict, float, str]]:
    """
    Detect potential duplicate entities.
    
    Args:
        entities: List of entity dictionaries
        name_threshold: Minimum similarity score for name matching (0.0-1.0)
        check_identifiers: Also check for identifier matches
    
    Returns:
        List of tuples: (entity1, entity2, similarity_score, match_reason)
    """
    duplicates = []
    seen_pairs: Set[Tuple[str, str]] = set()
    
    print(f"\n🔍 Scanning {len(entities)} entities for duplicates...")
    print(f"   Name similarity threshold: {name_threshold}")
    print(f"   Identifier matching: {'enabled' if check_identifiers else 'disabled'}")
    
    for i, entity1 in enumerate(entities):
        if i % 100 == 0:
            print(f"   Progress: {i}/{len(entities)}", end='\r')
        
        for entity2 in entities[i+1:]:
            # Skip if same entity ID
            if entity1['entity_id'] == entity2['entity_id']:
                continue
            
            # Create sorted pair key to avoid duplicate pairs
            pair_key = tuple(sorted([entity1['entity_id'], entity2['entity_id']]))
            if pair_key in seen_pairs:
                continue
            
            match_reason = None
            similarity = 0.0
            
            # Check identifier match
            if check_identifiers and check_identifier_match(entity1, entity2):
                match_reason = "IDENTIFIER_MATCH"
                similarity = 1.0
            
            # Check name similarity
            if not match_reason:
                similarity = calculate_similarity(entity1['name'], entity2['name'])
                if similarity >= name_threshold:
                    match_reason = f"NAME_SIMILAR_{similarity:.2f}"
            
            if match_reason:
                duplicates.append((entity1, entity2, similarity, match_reason))
                seen_pairs.add(pair_key)
    
    print(f"\n   ✓ Found {len(duplicates)} potential duplicate pairs")
    
    return duplicates


def group_duplicates(duplicates: List[Tuple[Dict, Dict, float, str]]) -> List[List[Dict]]:
    """Group duplicate pairs into clusters of related entities."""
    # Build adjacency list
    graph = defaultdict(set)
    all_entities = {}
    
    for entity1, entity2, _, _ in duplicates:
        id1 = entity1['entity_id']
        id2 = entity2['entity_id']
        
        graph[id1].add(id2)
        graph[id2].add(id1)
        
        all_entities[id1] = entity1
        all_entities[id2] = entity2
    
    # Find connected components using DFS
    visited = set()
    clusters = []
    
    def dfs(entity_id: str, cluster: List[str]):
        visited.add(entity_id)
        cluster.append(entity_id)
        for neighbor in graph[entity_id]:
            if neighbor not in visited:
                dfs(neighbor, cluster)
    
    for entity_id in all_entities:
        if entity_id not in visited:
            cluster = []
            dfs(entity_id, cluster)
            clusters.append([all_entities[eid] for eid in cluster])
    
    return clusters


def main():
    parser = argparse.ArgumentParser(
        description='Detect potential duplicate entities'
    )
    parser.add_argument(
        '--entities_file',
        default='data/entities/entities_master.csv',
        help='Path to entities CSV file'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.85,
        help='Name similarity threshold (0.0-1.0)'
    )
    parser.add_argument(
        '--output',
        default='data/entities/entities_duplicates_detected.csv',
        help='Output CSV file for detected duplicates'
    )
    parser.add_argument(
        '--no-identifiers',
        action='store_true',
        help='Disable identifier matching (only use name similarity)'
    )
    
    args = parser.parse_args()
    
    # Load entities
    entities_path = Path(args.entities_file)
    
    if not entities_path.exists():
        print(f"Error: File not found: {entities_path}")
        return
    
    print("🔎 Entity Duplicate Detection")
    print("=" * 60)
    print(f"Input file: {entities_path}")
    
    entities = []
    with open(entities_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entities = list(reader)
    
    print(f"Loaded {len(entities)} entities")
    
    # Detect duplicates
    duplicates = detect_duplicates(
        entities,
        name_threshold=args.threshold,
        check_identifiers=not args.no_identifiers
    )
    
    if not duplicates:
        print("\n✅ No duplicates found!")
        return
    
    # Group into clusters
    print("\n📊 Grouping duplicates into clusters...")
    clusters = group_duplicates(duplicates)
    print(f"   ✓ Found {len(clusters)} clusters of duplicate entities")
    
    # Write results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Writing results to {output_path}...")
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'cluster_id', 'entity_id', 'name', 'type', 'uei', 'duns', 'cage',
            'similarity_score', 'match_reason', 'cluster_size'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for cluster_id, cluster in enumerate(clusters, 1):
            # Calculate max similarity within cluster
            max_similarity = 0.0
            match_reasons = set()
            
            for dup in duplicates:
                if dup[0] in cluster and dup[1] in cluster:
                    max_similarity = max(max_similarity, dup[2])
                    match_reasons.add(dup[3])
            
            for entity in cluster:
                writer.writerow({
                    'cluster_id': cluster_id,
                    'entity_id': entity['entity_id'],
                    'name': entity['name'],
                    'type': entity.get('type', ''),
                    'uei': entity.get('uei', ''),
                    'duns': entity.get('duns', ''),
                    'cage': entity.get('cage', ''),
                    'similarity_score': f'{max_similarity:.2f}',
                    'match_reason': ', '.join(match_reasons),
                    'cluster_size': len(cluster)
                })
    
    print("   ✓ Results written")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    print(f"Total duplicate pairs found: {len(duplicates)}")
    print(f"Duplicate clusters: {len(clusters)}")
    print(f"Total entities involved: {sum(len(c) for c in clusters)}")
    
    # Show top clusters
    print("\n🔝 Top 10 Largest Clusters:")
    sorted_clusters = sorted(clusters, key=len, reverse=True)[:10]
    for i, cluster in enumerate(sorted_clusters, 1):
        print(f"\n{i}. Cluster with {len(cluster)} entities:")
        for entity in cluster[:3]:  # Show first 3
            print(f"   - {entity['name']} ({entity.get('type', 'Unknown')})")
        if len(cluster) > 3:
            print(f"   ... and {len(cluster) - 3} more")
    
    print("\n📋 Next Steps:")
    print(f"   1. Review detected duplicates in: {output_path}")
    print("   2. Manually verify which entities should be merged")
    print("   3. Use merge_entities.py script to merge confirmed duplicates")
    print("   4. Update relationships and references")


if __name__ == '__main__':
    main()

