"""
Migrate FFRDC/UARC data from reference files to main entity database.

This script:
1. Parses FFRDC lookup data
2. Generates entity_id hashes for FFRDCs and their operators
3. Creates entity records with proper types
4. Generates relationship edges (operator → FFRDC, sponsor → FFRDC)
5. Outputs updated entities_master.csv and entity_relationships.csv

Usage:
    python data/scripts/migrate_ffrdc_to_entities.py
"""

import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple


def generate_entity_id(name: str) -> str:
    """Generate consistent entity_id hash from name."""
    return hashlib.md5(name.encode('utf-8')).hexdigest()[:16]


def determine_entity_type(center_name: str, sponsor_agency: str) -> str:
    """Determine entity type based on center name and sponsor."""
    center_lower = center_name.lower()
    
    if 'national laboratory' in center_lower:
        return 'National Laboratory'
    elif sponsor_agency == 'DoD':
        return 'FFRDC'
    elif sponsor_agency in ['DOE', 'NASA', 'NSF', 'NIH', 'DOC']:
        return 'FFRDC'
    else:
        return 'FFRDC'


def determine_operator_type(operator_name: str) -> str:
    """Determine operator entity type."""
    operator_lower = operator_name.lower()
    
    if 'university' in operator_lower or 'institute of technology' in operator_lower:
        return 'Academic Institution'
    elif 'corporation' in operator_lower or 'llc' in operator_lower or ', inc' in operator_lower:
        return 'Corporation'
    else:
        return 'Organization'


def parse_ffrdc_data(ffrdc_file: Path) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Parse FFRDC lookup file and generate entities and relationships.
    
    Returns:
        Tuple of (ffrdc_entities, operator_entities, relationships)
    """
    ffrdc_entities = []
    operator_entities = []
    relationships = []
    
    # Track unique operators to avoid duplicates
    operators_seen: Set[str] = set()
    
    with open(ffrdc_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            center = row['Center']
            operator = row['Operator']
            sponsor_agency = row['Sponsor_Agency']
            sponsor_subagency = row['Sponsor_Subagency']
            
            # Generate entity IDs
            ffrdc_id = generate_entity_id(center)
            operator_id = generate_entity_id(operator)
            sponsor_id = generate_entity_id(sponsor_agency)
            
            # Determine entity types
            ffrdc_type = determine_entity_type(center, sponsor_agency)
            operator_type = determine_operator_type(operator)
            
            # Create FFRDC entity
            ffrdc_entity = {
                'entity_id': ffrdc_id,
                'name': center,
                'uei': '',
                'duns': '',
                'cage': '',
                'type': ffrdc_type,
                'country': 'USA',
                'state': '',
                'city': '',
                'url': '',
                'source_file': 'reference/ffrdc_lookup_master.csv'
            }
            ffrdc_entities.append(ffrdc_entity)
            
            # Create operator entity (avoid duplicates)
            if operator not in operators_seen:
                operators_seen.add(operator)
                operator_entity = {
                    'entity_id': operator_id,
                    'name': operator,
                    'uei': '',
                    'duns': '',
                    'cage': '',
                    'type': operator_type,
                    'country': 'USA',
                    'state': '',
                    'city': '',
                    'url': '',
                    'source_file': 'reference/ffrdc_lookup_master.csv'
                }
                operator_entities.append(operator_entity)
            
            # Create operator → FFRDC relationship
            operator_rel = {
                'source': operator,
                'target': center,
                'label': f'Operates {ffrdc_type}'
            }
            relationships.append(operator_rel)
            
            # Create sponsor agency → FFRDC relationship
            sponsor_label = f'Sponsors ({sponsor_subagency})' if sponsor_subagency else 'Sponsors'
            sponsor_rel = {
                'source': sponsor_agency,
                'target': center,
                'label': sponsor_label
            }
            relationships.append(sponsor_rel)
    
    return ffrdc_entities, operator_entities, relationships


def load_existing_entities(entities_file: Path) -> List[Dict]:
    """Load existing entities from CSV."""
    entities = []
    
    if entities_file.exists():
        with open(entities_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            entities = list(reader)
    
    return entities


def load_existing_relationships(relationships_file: Path) -> List[Dict]:
    """Load existing relationships from CSV."""
    relationships = []
    
    if relationships_file.exists():
        with open(relationships_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            relationships = list(reader)
    
    return relationships


def merge_entities(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """Merge new entities with existing, avoiding duplicates by entity_id."""
    existing_ids = {e['entity_id'] for e in existing}
    merged = existing.copy()
    
    for entity in new:
        if entity['entity_id'] not in existing_ids:
            merged.append(entity)
            existing_ids.add(entity['entity_id'])
    
    return merged


def merge_relationships(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """Merge new relationships with existing, avoiding duplicates."""
    # Create tuple key for uniqueness
    existing_keys = {(r['source'], r['target'], r['label']) for r in existing}
    merged = existing.copy()
    
    for rel in new:
        key = (rel['source'], rel['target'], rel['label'])
        if key not in existing_keys:
            merged.append(rel)
            existing_keys.add(key)
    
    return merged


def write_entities(entities: List[Dict], output_file: Path):
    """Write entities to CSV."""
    if not entities:
        return
    
    fieldnames = ['entity_id', 'name', 'uei', 'duns', 'cage', 'type', 
                  'country', 'state', 'city', 'url', 'source_file']
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entities)


def write_relationships(relationships: List[Dict], output_file: Path):
    """Write relationships to CSV."""
    if not relationships:
        return
    
    fieldnames = ['source', 'target', 'label']
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relationships)


def main():
    """Main migration function."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    ffrdc_file = base_dir / 'reference' / 'ffrdc_lookup_master.csv'
    entities_file = base_dir / 'entities' / 'entities_master.csv'
    relationships_file = base_dir / 'entities' / 'entity_relationships.csv'
    
    print("🚀 FFRDC/UARC Entity Migration")
    print("=" * 60)
    
    # Parse FFRDC data
    print(f"\n1. Parsing FFRDC data from {ffrdc_file.name}...")
    ffrdc_entities, operator_entities, new_relationships = parse_ffrdc_data(ffrdc_file)
    
    print(f"   ✓ Found {len(ffrdc_entities)} FFRDC/UARC entities")
    print(f"   ✓ Found {len(operator_entities)} operator entities")
    print(f"   ✓ Created {len(new_relationships)} relationships")
    
    # Load existing data
    print(f"\n2. Loading existing entities from {entities_file.name}...")
    existing_entities = load_existing_entities(entities_file)
    print(f"   ✓ Loaded {len(existing_entities)} existing entities")
    
    print(f"\n3. Loading existing relationships from {relationships_file.name}...")
    existing_relationships = load_existing_relationships(relationships_file)
    print(f"   ✓ Loaded {len(existing_relationships)} existing relationships")
    
    # Merge data
    print("\n4. Merging entities...")
    all_new_entities = ffrdc_entities + operator_entities
    merged_entities = merge_entities(existing_entities, all_new_entities)
    new_entity_count = len(merged_entities) - len(existing_entities)
    print(f"   ✓ Added {new_entity_count} new entities")
    print(f"   ✓ Total entities: {len(merged_entities)}")
    
    print("\n5. Merging relationships...")
    merged_relationships = merge_relationships(existing_relationships, new_relationships)
    new_rel_count = len(merged_relationships) - len(existing_relationships)
    print(f"   ✓ Added {new_rel_count} new relationships")
    print(f"   ✓ Total relationships: {len(merged_relationships)}")
    
    # Write output
    print(f"\n6. Writing updated entities to {entities_file.name}...")
    write_entities(merged_entities, entities_file)
    print("   ✓ Entities written successfully")
    
    print(f"\n7. Writing updated relationships to {relationships_file.name}...")
    write_relationships(merged_relationships, relationships_file)
    print("   ✓ Relationships written successfully")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print(f"\nEntity Breakdown:")
    
    # Count by type
    type_counts = {}
    for entity in merged_entities:
        entity_type = entity.get('type', 'Unknown')
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    
    for entity_type, count in sorted(type_counts.items()):
        print(f"   {entity_type}: {count}")
    
    print(f"\nTotal Entities: {len(merged_entities)}")
    print(f"Total Relationships: {len(merged_relationships)}")
    
    print("\n📋 Next Steps:")
    print("   1. Review the updated CSV files")
    print("   2. Update backend data_loader.py to handle new entity types")
    print("   3. Update frontend types for new entity type colors")
    print("   4. Restart the application to see new entities in network graph")


if __name__ == '__main__':
    main()

