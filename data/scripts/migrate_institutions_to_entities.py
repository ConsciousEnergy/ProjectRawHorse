"""
Migrate academic institutions from NSF data into entities_master.csv
"""
import os
import csv
import hashlib
from typing import Dict, Set
import argparse


def generate_entity_id(name: str) -> str:
    """Generate consistent entity ID from name"""
    return hashlib.sha256(name.lower().strip().encode()).hexdigest()


def infer_institution_type(name: str, research_areas: str) -> str:
    """
    Infer more specific institution type based on name and research
    """
    name_lower = name.lower()
    
    # Universities
    if any(term in name_lower for term in ['university', 'college']):
        return "Academic Institution"
    
    # Research institutes
    if any(term in name_lower for term in ['institute', 'research center', 'laboratory', 'lab']):
        return "Research Institution"
    
    # Default
    return "Academic Institution"


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


def migrate_institutions(
    institutions_csv: str,
    entities_path: str,
    max_institutions: int = 30
):
    """
    Migrate academic institutions into entities_master.csv
    """
    # Load existing data
    entities, existing_names = load_existing_entities(entities_path)
    original_count = len(entities)
    print(f"Loaded {original_count} existing entities")
    
    # Parse institutions CSV
    new_institutions = []
    skipped = 0
    
    with open(institutions_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if len(new_institutions) >= max_institutions:
                break
            
            name = row['name'].strip()
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
            entity_type = infer_institution_type(name, row.get('research_areas', ''))
            
            # Build description
            city_state = f"{row['city']}, {row['state']}" if row['city'] and row['state'] else ''
            research_desc = f" Research areas: {row['research_areas']}" if row['research_areas'] else ''
            description = f"Academic institution in {city_state}.{research_desc}" if city_state else f"Academic institution.{research_desc}"
            
            # Build notes
            notes = f"NSF Awards: {row['award_count']}, Total Funding: ${float(row['total_funding']):,.0f}"
            if row.get('pi_count'):
                notes += f", Principal Investigators: {row['pi_count']}"
            if row.get('first_award') and row.get('last_award'):
                notes += f", Award Period: {row['first_award']} to {row['last_award']}"
            
            entity = {
                'entity_id': entity_id,
                'display_name': name,
                'normalized_name': normalized_name,
                'entity_type': entity_type,
                'aliases': '',
                'website': '',
                'description': description,
                'country': row.get('country', 'US'),
                'source': 'NSF Awards API',
                'credibility_score': '',
                'date_added': '',
                'last_updated': '',
                'notes': notes
            }
            
            entities[entity_id] = entity
            existing_names.add(normalized_name)
            new_institutions.append(entity)
    
    print(f"\nAdded {len(new_institutions)} new academic institutions")
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
    
    # Print summary
    print("\n=== Entity Type Breakdown (New) ===")
    type_counts = {}
    for entity in new_institutions:
        entity_type = entity['entity_type']
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    
    for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{entity_type}: {count}")
    
    print("\n=== Sample New Institutions ===")
    for entity in new_institutions[:5]:
        print(f"- {entity['display_name']} ({entity['entity_type']})")
        if entity['description']:
            print(f"  {entity['description'][:100]}")


def main():
    parser = argparse.ArgumentParser(description='Migrate academic institutions to entities database')
    parser.add_argument('--institutions_csv', required=True, help='Extracted institutions CSV from extract_institutions_from_nsf.py')
    parser.add_argument('--entities_master', default='data/entities/entities_master.csv', help='Path to entities_master.csv')
    parser.add_argument('--max_institutions', type=int, default=30, help='Maximum number of institutions to add')
    
    args = parser.parse_args()
    
    # Get absolute paths relative to script location or project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Resolve paths
    institutions_csv = args.institutions_csv
    if not os.path.isabs(institutions_csv):
        institutions_csv = os.path.join(project_root, institutions_csv)
    
    entities_master = args.entities_master
    if not os.path.isabs(entities_master):
        entities_master = os.path.join(project_root, entities_master)
    
    print(f"Institutions CSV: {institutions_csv}")
    print(f"Entities Master: {entities_master}")
    print()
    
    migrate_institutions(institutions_csv, entities_master, args.max_institutions)
    print("\n✅ Migration complete!")


if __name__ == "__main__":
    main()

