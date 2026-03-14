"""
Migrate top contractors from USASpending aggregation into entities_master.csv
"""
import os
import csv
import hashlib
from typing import Dict, List, Set
import argparse


def generate_entity_id(name: str) -> str:
    """Generate consistent entity ID from name"""
    return hashlib.sha256(name.lower().strip().encode()).hexdigest()


def infer_entity_type(name: str, total_amount: float) -> str:
    """
    Infer entity type from contractor name and funding level
    """
    name_lower = name.lower()
    
    # Defense contractors
    if any(term in name_lower for term in ['defense', 'aerospace', 'technologies', 'systems', 'industries', 'corporation', 'corp', 'inc', 'llc', 'ltd']):
        return "Corporation"
    
    # Government entities
    if any(term in name_lower for term in ['department of', 'agency', 'government', 'federal', 'commission']):
        return "Government Agency"
    
    # Research institutions
    if any(term in name_lower for term in ['university', 'institute', 'college', 'research', 'laboratory', 'national lab']):
        return "Research Institution"
    
    # Default for large contractors
    if total_amount > 10_000_000:  # $10M+
        return "Corporation"
    
    return "Organization"


def load_existing_entities(entities_path: str) -> tuple[Dict[str, Dict], Set[str]]:
    """
    Load existing entities from entities_master.csv
    
    Returns:
        - Dictionary mapping entity_id to entity data
        - Set of normalized names for duplicate detection
    """
    entities = {}
    normalized_names = set()
    
    if not os.path.exists(entities_path):
        print(f"Warning: {entities_path} not found, will create new file")
        return entities, normalized_names
    
    with open(entities_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity_id = row['entity_id']
            entities[entity_id] = row
            normalized_names.add(row['normalized_name'].lower())
    
    return entities, normalized_names


def migrate_contractors(
    contractors_csv: str,
    entities_path: str,
    identifiers_path: str,
    max_contractors: int = 50
):
    """
    Migrate top contractors into entities_master.csv and entity_identifiers.csv
    """
    # Load existing data
    entities, existing_names = load_existing_entities(entities_path)
    original_count = len(entities)
    print(f"Loaded {original_count} existing entities")
    
    # Load existing identifiers
    identifiers = []
    if os.path.exists(identifiers_path):
        with open(identifiers_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            identifiers = list(reader)
    print(f"Loaded {len(identifiers)} existing identifiers")
    
    # Parse contractors CSV
    new_contractors = []
    skipped = 0
    
    with open(contractors_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if len(new_contractors) >= max_contractors:
                break
            
            name = row['recipient_name'].strip()
            if not name:
                continue
            
            # Check for duplicates
            normalized_name = name.lower().strip()
            if normalized_name in existing_names:
                print(f"Skipping duplicate: {name}")
                skipped += 1
                continue
            
            # Create entity record
            entity_id = generate_entity_id(name)
            total_amount = float(row['total_amount'])
            entity_type = infer_entity_type(name, total_amount)
            
            entity = {
                'entity_id': entity_id,
                'display_name': name,
                'normalized_name': normalized_name,
                'entity_type': entity_type,
                'aliases': '',
                'website': '',
                'description': f"Defense/aerospace contractor with ${total_amount:,.0f} in awards from {row['agencies'].split(';')[0] if row['agencies'] else 'federal agencies'}",
                'country': 'USA',
                'source': 'USASpending API',
                'credibility_score': '',
                'date_added': '',
                'last_updated': '',
                'notes': f"Total awards: ${total_amount:,.0f} ({row['award_count']} contracts). Active: {row['first_seen']} to {row['last_seen']}"
            }
            
            entities[entity_id] = entity
            existing_names.add(normalized_name)
            new_contractors.append(entity)
            
            # Add identifiers if available
            if row['uei']:
                identifiers.append({
                    'entity_id': entity_id,
                    'identifier_type': 'UEI',
                    'identifier_value': row['uei'],
                    'source': 'USASpending API',
                    'verified': 'yes'
                })
            
            if row['duns']:
                identifiers.append({
                    'entity_id': entity_id,
                    'identifier_type': 'DUNS',
                    'identifier_value': row['duns'],
                    'source': 'USASpending API',
                    'verified': 'yes'
                })
    
    print(f"\nAdded {len(new_contractors)} new contractor entities")
    print(f"Skipped {skipped} duplicates")
    
    # Write updated entities_master.csv
    with open(entities_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['entity_id', 'display_name', 'normalized_name', 'entity_type', 'aliases', 
                     'website', 'description', 'country', 'source', 'credibility_score', 
                     'date_added', 'last_updated', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entity in entities.values():
            writer.writerow(entity)
    
    print(f"Wrote {len(entities)} total entities to {entities_path}")
    
    # Write updated entity_identifiers.csv
    with open(identifiers_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['entity_id', 'identifier_type', 'identifier_value', 'source', 'verified']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for identifier in identifiers:
            writer.writerow(identifier)
    
    print(f"Wrote {len(identifiers)} total identifiers to {identifiers_path}")
    
    # Print summary
    print("\n=== Entity Type Breakdown (New) ===")
    type_counts = {}
    for entity in new_contractors:
        entity_type = entity['entity_type']
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    
    for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{entity_type}: {count}")
    
    print("\n=== Sample New Entities ===")
    for entity in new_contractors[:5]:
        print(f"- {entity['display_name']} ({entity['entity_type']})")


def main():
    parser = argparse.ArgumentParser(description='Migrate contractors to entities database')
    parser.add_argument('--contractors_csv', required=True, help='Aggregated contractors CSV from aggregate_top_recipients.py')
    parser.add_argument('--entities_master', default='data/entities/entities_master.csv', help='Path to entities_master.csv')
    parser.add_argument('--identifiers', default='data/entities/entity_identifiers.csv', help='Path to entity_identifiers.csv')
    parser.add_argument('--max_contractors', type=int, default=50, help='Maximum number of contractors to add')
    
    args = parser.parse_args()
    
    # Get absolute paths relative to script location or project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Resolve paths
    contractors_csv = args.contractors_csv
    if not os.path.isabs(contractors_csv):
        contractors_csv = os.path.join(project_root, contractors_csv)
    
    entities_master = args.entities_master
    if not os.path.isabs(entities_master):
        entities_master = os.path.join(project_root, entities_master)
    
    identifiers = args.identifiers
    if not os.path.isabs(identifiers):
        identifiers = os.path.join(project_root, identifiers)
    
    print(f"Contractors CSV: {contractors_csv}")
    print(f"Entities Master: {entities_master}")
    print(f"Identifiers: {identifiers}")
    print()
    
    migrate_contractors(contractors_csv, entities_master, identifiers, args.max_contractors)
    print("\n✅ Migration complete!")


if __name__ == "__main__":
    main()

