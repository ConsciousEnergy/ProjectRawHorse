#!/usr/bin/env python3
"""
Phase 3: Comprehensive relationship verification and updates
"""
import csv
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_CSV = PROJECT_ROOT / "data" / "entities" / "uap_gerb_transcript_relationships.csv"

# Relationships to UPDATE (corrected information based on research)
RELATIONSHIPS_TO_UPDATE = [
    # Doug Wolfe - verified positions
    {
        'old': ("Doug Wolfe", "NRO", "Executive Assistant", "16 years in NRO, executive assistant to director"),
        'new': ("Doug Wolfe", "NRO", "Position", "NRO connection unverified - Doug Wolfe served 33 years at CIA, not NRO. Needs verification.")
    },
    {
        'old': ("Doug Wolfe", "CIA DS&T", "Deputy Director", "CIA DS&T deputy director"),
        'new': ("Doug Wolfe", "CIA DS&T", "Associate Deputy Director", "Associate Deputy Director of Science and Technology at CIA. Also served as CIO (2013-2016). Verified: TransUnion, ACG")
    },
    {
        'old': ("Doug Wolfe", "OGA", "First Director", "Started OGA in 2003"),
        'new': ("Doug Wolfe", "OGA", "Deputy Director", "Deputy Director of Office of Global Access (OGA). Verified: TransUnion, ACG")
    },
    {
        'old': ("Doug Wolfe", "DDNI ATNF", "Served As", "DDNI ATNF with oversight over NRO acquisitions"),
        'new': ("Doug Wolfe", "DDNI ATNF", "Deputy Director", "Deputy Director for Acquisition, Technology, and Facilities at ODNI (DDNI ATNF). Verified: TransUnion, ACG")
    },
    # CIA DS&T -> OGA relationship note update
    {
        'old': ("CIA DS&T", "OGA", "Created", "OGA created under DS&T in 2003, first director Doug Wolfe"),
        'new': ("CIA DS&T", "OGA", "Created", "OGA created under DS&T in 2003. Doug Wolfe served as Deputy Director (not first director - needs verification).")
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
            print(f"    New: {new_rel[0]} -> {new_rel[1]} ({new_rel[2]})")
            break
    return relationships, updated

def main():
    """Main verification and cleanup function"""
    print("=" * 70)
    print("Phase 3: Comprehensive Relationship Verification")
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
    backup_path = RELATIONSHIPS_CSV.with_suffix('.csv.backup4')
    if RELATIONSHIPS_CSV.exists():
        import shutil
        shutil.copy2(RELATIONSHIPS_CSV, backup_path)
        print(f"  Created backup: {backup_path.name}")
    
    save_relationships(RELATIONSHIPS_CSV, relationships)
    print(f"  Saved {len(relationships)} relationships")
    print(f"  Updated {updated_count} relationship(s)")
    
    print("\n" + "=" * 70)
    print("[OK] Phase 3 verification complete!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  Total relationships: {len(relationships)}")
    print(f"  Updated: {updated_count}")
    print("\nNext steps:")
    print("  1. Review the updated relationships")
    print("  2. Run load_transcript_data.py to reload relationships")
    print("  3. Continue verifying remaining relationships")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
