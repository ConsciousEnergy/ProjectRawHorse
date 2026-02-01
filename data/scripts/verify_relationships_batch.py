#!/usr/bin/env python3
"""
Batch verification and update of relationships based on research findings
"""
import csv
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_CSV = PROJECT_ROOT / "data" / "entities" / "uap_gerb_transcript_relationships.csv"

# Relationships to REMOVE (unverified/incorrect)
RELATIONSHIPS_TO_REMOVE = [
    # Mark Moahan - no public records found, likely incorrect or misspelled
    ("Mark Moahan", "NRO", "High Level Deputy Director"),
    ("Mark Moahan", "CIA DS&T", "Position"),
    ("Mark Moahan", "OGA", "Position"),
    ("Mark Moahan", "DDNI ATNF", "Position"),
    # Don Meyer - unverified connection
    # Note: Keeping MITRE connection but updating note to reflect uncertainty
]

# Relationships to UPDATE (corrected information)
RELATIONSHIPS_TO_UPDATE = [
    # Donald Kerr - verified positions
    {
        'old': ("Donald Kerr", "NRO", "High Level Position", "Mentioned in ATPWG notes for funding requests"),
        'new': ("Donald Kerr", "NRO", "Director", "Director of NRO (2005-2007). Verified: Wikipedia, GovInfo.gov")
    },
    {
        'old': ("Donald Kerr", "Los Alamos National Laboratory", "Director", "Director of Los Alamos"),
        'new': ("Donald Kerr", "Los Alamos National Laboratory", "Director", "Director of Los Alamos (1979-1985). Verified: Wikipedia, GovInfo.gov")
    },
    {
        'old': ("Donald Kerr", "CIA DS&T", "Deputy Director", "Deputy director of CIA DS&T"),
        'new': ("Donald Kerr", "CIA DS&T", "Deputy Director", "Deputy Director for Science and Technology at CIA (2001-2005). Verified: Wikipedia, GovInfo.gov")
    },
    {
        'old': ("Donald Kerr", "EG&G", "Director", "Director of EG&G"),
        'new': ("Donald Kerr", "EG&G", "Director", "Director of EG&G - NEEDS VERIFICATION (no public records found)")
    },
    # Add Donald Kerr -> MITRE relationship (verified)
    {
        'old': None,
        'new': ("Donald Kerr", "MITER Corporation", "Board Chairman", "Chairman of MITRE Board of Trustees (2018-2021), Trustee (2009-2018). Verified: Wikipedia, MITRE Corporation")
    },
    # Update MITRE -> DDNI ATNF relationship note
    {
        'old': ("MITER Corporation", "DDNI ATNF", "Personnel Connection", "Don Meyer was MITER and DDNI ATNF"),
        'new': ("MITER Corporation", "DDNI ATNF", "Personnel Connection", "Donald Kerr connection (was NRO Director and MITRE Chairman) - Don Meyer claim unverified")
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

def remove_relationship(relationships, source, target, label):
    """Remove a specific relationship"""
    removed = False
    filtered = []
    for rel in relationships:
        if (rel['source'] == source and 
            rel['target'] == target and 
            rel['label'] == label):
            removed = True
            print(f"  REMOVED: {source} -> {target} ({label})")
            continue
        filtered.append(rel)
    return filtered, removed

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
            print(f"    New: {new_rel[0]} -> {new_rel[1]} ({new_rel[2]})")
            break
    return relationships, updated

def add_relationship(relationships, new_rel):
    """Add a new relationship"""
    # Check if it already exists
    exists = any(
        rel['source'] == new_rel[0] and 
        rel['target'] == new_rel[1] and 
        rel['label'] == new_rel[2]
        for rel in relationships
    )
    if not exists:
        relationships.append({
            'source': new_rel[0],
            'target': new_rel[1],
            'label': new_rel[2],
            'notes': new_rel[3]
        })
        print(f"  ADDED: {new_rel[0]} -> {new_rel[1]} ({new_rel[2]})")
        return relationships, True
    else:
        print(f"  SKIPPED (exists): {new_rel[0]} -> {new_rel[1]} ({new_rel[2]})")
        return relationships, False

def main():
    """Main verification and cleanup function"""
    print("=" * 70)
    print("Batch Relationship Verification and Update")
    print("=" * 70)
    
    if not RELATIONSHIPS_CSV.exists():
        print(f"ERROR: Relationships file not found: {RELATIONSHIPS_CSV}")
        return 1
    
    # Load relationships
    print(f"\nLoading relationships from: {RELATIONSHIPS_CSV.name}")
    relationships = load_relationships(RELATIONSHIPS_CSV)
    print(f"  Loaded {len(relationships)} relationships")
    
    # Remove incorrect/unverified relationships
    print("\n" + "=" * 70)
    print("Removing Incorrect/Unverified Relationships:")
    print("=" * 70)
    
    removed_count = 0
    for source, target, label in RELATIONSHIPS_TO_REMOVE:
        relationships, removed = remove_relationship(relationships, source, target, label)
        if removed:
            removed_count += 1
    
    if removed_count == 0:
        print("  No relationships found to remove")
    
    # Update relationships
    print("\n" + "=" * 70)
    print("Updating Relationships with Verified Information:")
    print("=" * 70)
    
    updated_count = 0
    added_count = 0
    for update in RELATIONSHIPS_TO_UPDATE:
        if update['old'] is None:
            # Adding new relationship
            relationships, added = add_relationship(relationships, update['new'])
            if added:
                added_count += 1
        else:
            # Updating existing relationship
            relationships, updated = update_relationship(relationships, update['old'], update['new'])
            if updated:
                updated_count += 1
    
    if updated_count == 0 and added_count == 0:
        print("  No relationships found to update")
    
    # Save cleaned relationships
    print("\n" + "=" * 70)
    print(f"Saving updated relationships...")
    print("=" * 70)
    
    # Create backup
    backup_path = RELATIONSHIPS_CSV.with_suffix('.csv.backup2')
    if RELATIONSHIPS_CSV.exists():
        import shutil
        shutil.copy2(RELATIONSHIPS_CSV, backup_path)
        print(f"  Created backup: {backup_path.name}")
    
    save_relationships(RELATIONSHIPS_CSV, relationships)
    print(f"  Saved {len(relationships)} relationships")
    print(f"  Removed {removed_count} incorrect/unverified relationship(s)")
    print(f"  Updated {updated_count} relationship(s)")
    print(f"  Added {added_count} new relationship(s)")
    
    print("\n" + "=" * 70)
    print("[OK] Relationship verification complete!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  Total relationships: {len(relationships)}")
    print(f"  Removed: {removed_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Added: {added_count}")
    print("\nNext steps:")
    print("  1. Review the updated relationships")
    print("  2. Run load_transcript_data.py to reload relationships")
    print("  3. Restart the application to see updated graph")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
