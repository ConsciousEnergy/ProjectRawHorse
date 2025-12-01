"""
Migrate NGO entity data from seeds file to main entity database.

This script:
1. Reads entities_ngo_seeds.csv
2. Validates and enriches entity data
3. Adds NGOs to entities_master.csv
4. Avoids duplicates

Usage:
    python data/scripts/migrate_ngo_to_entities.py
"""

import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Set


def generate_entity_id(name: str) -> str:
    """Generate consistent entity_id hash from name."""
    return hashlib.md5(name.encode('utf-8')).hexdigest()[:16]


def load_existing_entities(entities_file: Path) -> List[Dict]:
    """Load existing entities from CSV."""
    entities = []
    
    if entities_file.exists():
        with open(entities_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            entities = list(reader)
    
    return entities


def load_ngo_seeds(seeds_file: Path) -> List[Dict]:
    """Load NGO seed data from CSV."""
    ngos = []
    
    if not seeds_file.exists():
        print(f"Error: Seeds file not found: {seeds_file}")
        return []
    
    with open(seeds_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ngos = list(reader)
    
    return ngos


def merge_entities(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """Merge new entities with existing, avoiding duplicates by entity_id."""
    existing_ids = {e['entity_id'] for e in existing}
    existing_names = {e['name'].lower() for e in existing}
    merged = existing.copy()
    
    added_count = 0
    skipped_count = 0
    
    for entity in new:
        entity_id = entity['entity_id']
        entity_name = entity['name'].lower()
        
        # Check for duplicates by ID or name
        if entity_id in existing_ids:
            print(f"  ⚠️  Skipping duplicate ID: {entity['name']}")
            skipped_count += 1
            continue
        
        if entity_name in existing_names:
            print(f"  ⚠️  Skipping duplicate name: {entity['name']}")
            skipped_count += 1
            continue
        
        # Add new entity
        merged.append(entity)
        existing_ids.add(entity_id)
        existing_names.add(entity_name)
        added_count += 1
    
    return merged, added_count, skipped_count


def write_entities(entities: List[Dict], output_file: Path):
    """Write entities to CSV."""
    if not entities:
        return
    
    # Use standard entity fieldnames
    fieldnames = ['entity_id', 'name', 'uei', 'duns', 'cage', 'type', 
                  'country', 'state', 'city', 'url', 'source_file']
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(entities)


def main():
    """Main migration function."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    seeds_file = base_dir / 'entities' / 'entities_ngo_seeds.csv'
    entities_file = base_dir / 'entities' / 'entities_master.csv'
    
    print("🚀 NGO Entity Migration")
    print("=" * 60)
    
    # Load NGO seeds
    print(f"\n1. Loading NGO seeds from {seeds_file.name}...")
    ngo_entities = load_ngo_seeds(seeds_file)
    print(f"   ✓ Loaded {len(ngo_entities)} NGO entities")
    
    # Load existing entities
    print(f"\n2. Loading existing entities from {entities_file.name}...")
    existing_entities = load_existing_entities(entities_file)
    print(f"   ✓ Loaded {len(existing_entities)} existing entities")
    
    # Merge data
    print("\n3. Merging NGO entities...")
    merged_entities, added_count, skipped_count = merge_entities(existing_entities, ngo_entities)
    print(f"   ✓ Added {added_count} new NGO entities")
    if skipped_count > 0:
        print(f"   ⚠️  Skipped {skipped_count} duplicate entities")
    print(f"   ✓ Total entities: {len(merged_entities)}")
    
    # Write output
    print(f"\n4. Writing updated entities to {entities_file.name}...")
    write_entities(merged_entities, entities_file)
    print("   ✓ Entities written successfully")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    
    # Count by type
    print(f"\nEntity Breakdown:")
    type_counts = {}
    for entity in merged_entities:
        entity_type = entity.get('type', 'Unknown')
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    
    for entity_type, count in sorted(type_counts.items()):
        print(f"   {entity_type}: {count}")
    
    print(f"\nTotal Entities: {len(merged_entities)}")
    
    # List new NGOs added
    if added_count > 0:
        print(f"\n📋 Newly Added NGOs:")
        for entity in ngo_entities:
            if entity['entity_id'] in [e['entity_id'] for e in merged_entities[-added_count:]]:
                ngo_type = entity.get('type', 'Unknown')
                print(f"   • {entity['name']} ({ngo_type})")
    
    print("\n📋 Next Steps:")
    print("   1. Review the updated entities_master.csv")
    print("   2. Consider adding relationships to entity_relationships.csv")
    print("   3. Restart the application to see new NGOs in network graph")
    print("   4. Optionally enrich with SAM.gov data (UEI, DUNS, CAGE)")


if __name__ == '__main__':
    main()

