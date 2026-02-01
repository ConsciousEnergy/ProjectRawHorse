#!/usr/bin/env python3
"""
Phase 4: Verify facility and organizational relationships
"""
import csv
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_CSV = PROJECT_ROOT / "data" / "entities" / "uap_gerb_transcript_relationships.csv"

# Relationships to UPDATE based on research
RELATIONSHIPS_TO_UPDATE = [
    # Update Doug Wolfe NRO relationship - verified he served 16 years with CIA component in NRO
    {
        'old': ("Doug Wolfe", "NRO", "Position", "Served 16 years with CIA component in NRO, contributing to launch and operations of multiple satellite systems. Later served as Associate Deputy Director of Science and Technology at CIA. Verified: PSCouncil.org"),
        'new': ("Doug Wolfe", "NRO", "CIA Component Service", "Served 16 years with CIA component in NRO (1984-2000), contributing to launch and operations of multiple satellite systems. Later served as Associate Deputy Director of Science and Technology at CIA. Total 33 years at CIA. Verified: PSCouncil.org, Potomac Institute")
    },
]

def load_relationships(csv_path):
    """Load relationships from CSV"""
    relationships = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            relationships.append({
                'source': row.get('source', '').strip(),
                'target': row.get('target', '').strip(),
                'label': row.get('label', '').strip(),
                'notes': row.get('notes', '').strip()
            })
    return relationships

def save_relationships(csv_path, relationships):
    """Save relationships to CSV"""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['source', 'target', 'label', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relationships)

def update_relationship(relationships, old_rel, new_rel):
    """Update a relationship"""
    updated = False
    for i, rel in enumerate(relationships):
        if (rel['source'] == old_rel[0] and 
            rel['target'] == old_rel[1] and 
            rel['label'] == old_rel[2] and
            rel['notes'] == old_rel[3]):
            relationships[i] = {
                'source': new_rel[0],
                'target': new_rel[1],
                'label': new_rel[2],
                'notes': new_rel[3]
            }
            updated = True
            print(f"  UPDATED: {old_rel[0]} -> {old_rel[1]} ({old_rel[2]})")
            break
    return relationships, updated

def main():
    """Main verification and cleanup function"""
    print("=" * 70)
    print("Phase 4: Facility and Organizational Relationship Verification")
    print("=" * 70)
    
    if not RELATIONSHIPS_CSV.exists():
        print(f"ERROR: Relationships file not found: {RELATIONSHIPS_CSV}")
        return 1
    
    # Load relationships
    print(f"\nLoading relationships from: {RELATIONSHIPS_CSV.name}")
    relationships = load_relationships(RELATIONSHIPS_CSV)
    print(f"  Loaded {len(relationships)} relationships")
    
    # Update relationships
    print("\n" + "=" * 70)
    print("Updating Relationships with Verified Information:")
    print("=" * 70)
    
    updated_count = 0
    for update in RELATIONSHIPS_TO_UPDATE:
        relationships, updated = update_relationship(relationships, update['old'], update['new'])
        if updated:
            updated_count += 1
    
    if updated_count == 0:
        print("  No relationships found to update")
    
    # Save updated relationships
    print("\n" + "=" * 70)
    print(f"Saving updated relationships...")
    print("=" * 70)
    
    # Create backup
    backup_path = RELATIONSHIPS_CSV.with_suffix('.csv.backup5')
    if RELATIONSHIPS_CSV.exists():
        import shutil
        shutil.copy2(RELATIONSHIPS_CSV, backup_path)
        print(f"  Created backup: {backup_path.name}")
    
    save_relationships(RELATIONSHIPS_CSV, relationships)
    print(f"  Saved {len(relationships)} relationships")
    print(f"  Updated {updated_count} relationship(s)")
    
    print("\n" + "=" * 70)
    print("[OK] Phase 4 verification complete!")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
