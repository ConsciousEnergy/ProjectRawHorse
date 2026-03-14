"""
Merge duplicate entities identified by detect_entity_duplicates.py.

This script takes a list of entity IDs to merge and combines them into
a single entity, updating all references in related tables.

Usage:
    python data/scripts/merge_entities.py --cluster 1 --keep entity_id_to_keep
"""

import csv
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple


def load_csv(filepath: Path) -> List[Dict]:
    """Load CSV file into list of dictionaries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_csv(filepath: Path, data: List[Dict], fieldnames: List[str]):
    """Save list of dictionaries to CSV file."""
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def merge_entity_records(
    entities: List[Dict],
    entity_ids_to_merge: List[str],
    keep_id: str
) -> Tuple[List[Dict], Dict]:
    """
    Merge multiple entity records into one.
    
    Args:
        entities: List of all entities
        entity_ids_to_merge: List of entity IDs to merge
        keep_id: Entity ID to keep (others will be removed)
    
    Returns:
        Tuple of (updated_entities, kept_entity)
    """
    # Find entities to merge
    entities_to_merge = [e for e in entities if e['entity_id'] in entity_ids_to_merge]
    
    if not entities_to_merge:
        raise ValueError(f"No entities found with IDs: {entity_ids_to_merge}")
    
    # Find the entity to keep
    kept_entity = next((e for e in entities_to_merge if e['entity_id'] == keep_id), None)
    
    if not kept_entity:
        # Keep the first one if specified ID not found
        kept_entity = entities_to_merge[0]
        keep_id = kept_entity['entity_id']
        print(f"   ⚠️  Specified ID not found, keeping: {kept_entity['name']}")
    
    # Merge data from other entities (fill in missing fields)
    for entity in entities_to_merge:
        if entity['entity_id'] == keep_id:
            continue
        
        # Fill in missing identifier fields
        if not kept_entity.get('uei') and entity.get('uei'):
            kept_entity['uei'] = entity['uei']
        
        if not kept_entity.get('duns') and entity.get('duns'):
            kept_entity['duns'] = entity['duns']
        
        if not kept_entity.get('cage') and entity.get('cage'):
            kept_entity['cage'] = entity['cage']
        
        # Fill in location if missing
        if not kept_entity.get('state') and entity.get('state'):
            kept_entity['state'] = entity['state']
        
        if not kept_entity.get('city') and entity.get('city'):
            kept_entity['city'] = entity['city']
        
        if not kept_entity.get('url') and entity.get('url'):
            kept_entity['url'] = entity['url']
    
    # Remove duplicates, keep only the merged entity
    updated_entities = [e for e in entities if e['entity_id'] not in entity_ids_to_merge]
    updated_entities.append(kept_entity)
    
    return updated_entities, kept_entity


def update_relationships(
    relationships: List[Dict],
    old_ids: List[str],
    new_id: str,
    old_names: List[str],
    new_name: str
) -> List[Dict]:
    """Update relationship references to use the kept entity."""
    updated = []
    removed_count = 0
    
    for rel in relationships:
        source = rel['source']
        target = rel['target']
        
        # Update IDs
        if source in old_ids:
            source = new_id
        if target in old_ids:
            target = new_id
        
        # Update names
        if source in old_names:
            source = new_name
        if target in old_names:
            target = new_name
        
        # Skip self-references
        if source == target or source == new_id and target == new_id:
            removed_count += 1
            continue
        
        rel['source'] = source
        rel['target'] = target
        updated.append(rel)
    
    if removed_count > 0:
        print(f"   Removed {removed_count} self-referencing relationships")
    
    return updated


def update_money_flows(
    flows: List[Dict],
    old_names: List[str],
    new_name: str
) -> List[Dict]:
    """Update money flow references to use the kept entity name."""
    for flow in flows:
        if flow['source'] in old_names:
            flow['source'] = new_name
        if flow['target'] in old_names:
            flow['target'] = new_name
    return flows


def main():
    parser = argparse.ArgumentParser(
        description='Merge duplicate entities'
    )
    parser.add_argument(
        '--duplicates_file',
        default='data/entities/entities_duplicates_detected.csv',
        help='Path to detected duplicates CSV'
    )
    parser.add_argument(
        '--cluster',
        type=int,
        required=True,
        help='Cluster ID to merge'
    )
    parser.add_argument(
        '--keep',
        help='Entity ID to keep (if not specified, keeps first entity in cluster)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be merged without making changes'
    )
    
    args = parser.parse_args()
    
    print("🔗 Entity Merge Tool")
    print("=" * 60)
    
    # Setup paths
    base_dir = Path('data')
    duplicates_path = Path(args.duplicates_file)
    entities_path = base_dir / 'entities' / 'entities_master.csv'
    relationships_path = base_dir / 'entities' / 'entity_relationships.csv'
    flows_path = base_dir / 'financial' / 'money_flows.csv'
    
    # Load duplicates file
    if not duplicates_path.exists():
        print(f"Error: Duplicates file not found: {duplicates_path}")
        print("Run detect_entity_duplicates.py first!")
        return
    
    duplicates = load_csv(duplicates_path)
    
    # Filter to specified cluster
    cluster_entities = [d for d in duplicates if int(d['cluster_id']) == args.cluster]
    
    if not cluster_entities:
        print(f"Error: Cluster {args.cluster} not found in duplicates file")
        return
    
    print(f"\n📋 Cluster {args.cluster} contains {len(cluster_entities)} entities:")
    for ent in cluster_entities:
        marker = " (KEEPING)" if args.keep and ent['entity_id'] == args.keep else ""
        print(f"   - {ent['name']} [{ent['entity_id']}]{marker}")
    
    # Determine which entity to keep
    keep_id = args.keep or cluster_entities[0]['entity_id']
    entity_ids_to_merge = [e['entity_id'] for e in cluster_entities]
    entity_names = [e['name'] for e in cluster_entities]
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
        print(f"\nWould merge {len(entity_ids_to_merge)} entities into: {keep_id}")
        return
    
    print(f"\n🔄 Merging into entity: {keep_id}")
    
    # Load all data
    print("\n1. Loading data files...")
    entities = load_csv(entities_path)
    relationships = load_csv(relationships_path) if relationships_path.exists() else []
    flows = load_csv(flows_path) if flows_path.exists() else []
    
    print(f"   ✓ Loaded {len(entities)} entities")
    print(f"   ✓ Loaded {len(relationships)} relationships")
    print(f"   ✓ Loaded {len(flows)} money flows")
    
    # Merge entity records
    print("\n2. Merging entity records...")
    updated_entities, kept_entity = merge_entity_records(entities, entity_ids_to_merge, keep_id)
    print(f"   ✓ Merged into: {kept_entity['name']}")
    print(f"   ✓ Entities count: {len(entities)} → {len(updated_entities)}")
    
    # Update relationships
    print("\n3. Updating relationships...")
    old_ids = [eid for eid in entity_ids_to_merge if eid != keep_id]
    updated_relationships = update_relationships(
        relationships, old_ids, keep_id, entity_names, kept_entity['name']
    )
    print(f"   ✓ Relationships updated: {len(relationships)} → {len(updated_relationships)}")
    
    # Update money flows
    print("\n4. Updating money flows...")
    old_names = [name for name in entity_names if name != kept_entity['name']]
    updated_flows = update_money_flows(flows, old_names, kept_entity['name'])
    print(f"   ✓ Money flows updated")
    
    # Save updated data
    print("\n5. Saving updated files...")
    
    # Get fieldnames from original files
    with open(entities_path, 'r', encoding='utf-8') as f:
        entities_fieldnames = csv.DictReader(f).fieldnames
    
    save_csv(entities_path, updated_entities, entities_fieldnames)
    print(f"   ✓ Saved: {entities_path}")
    
    if relationships:
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships_fieldnames = csv.DictReader(f).fieldnames
        save_csv(relationships_path, updated_relationships, relationships_fieldnames)
        print(f"   ✓ Saved: {relationships_path}")
    
    if flows:
        with open(flows_path, 'r', encoding='utf-8') as f:
            flows_fieldnames = csv.DictReader(f).fieldnames
        save_csv(flows_path, updated_flows, flows_fieldnames)
        print(f"   ✓ Saved: {flows_path}")
    
    print("\n" + "=" * 60)
    print("✅ Merge Complete!")
    print("=" * 60)
    print(f"Merged {len(entity_ids_to_merge)} entities into: {kept_entity['name']}")
    print(f"Kept entity ID: {keep_id}")
    
    print("\n📋 Next Steps:")
    print("   1. Review the merged entity in entities_master.csv")
    print("   2. Restart application to see changes")
    print("   3. Continue merging other clusters as needed")


if __name__ == '__main__':
    main()

