#!/usr/bin/env python3
"""
Verify and clean up entity relationships based on research
Removes unverified or incorrect connections
"""
import csv
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_CSV = PROJECT_ROOT / "data" / "entities" / "uap_gerb_transcript_relationships.csv"

# Verified relationships to REMOVE (incorrect/unverified)
RELATIONSHIPS_TO_REMOVE = [
    # Sean Kirkpatrick - MITRE connection is unverified/incorrect
    ("Sean Kirkpatrick", "MITER Corporation", "Subcontractor"),
]

# Relationships to VERIFY (needs research)
RELATIONSHIPS_TO_VERIFY = [
    ("Sean Kirkpatrick", "Oak Ridge National Laboratory", "Intelligence Programs Director"),
    ("Mark Moahan", "NRO", "High Level Deputy Director"),
    ("Mark Moahan", "CIA DS&T", "Position"),
    ("Mark Moahan", "OGA", "Position"),
    ("Mark Moahan", "DDNI ATNF", "Position"),
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

def main():
    """Main verification and cleanup function"""
    print("=" * 70)
    print("Relationship Verification and Cleanup")
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
    
    # List relationships that need verification
    print("\n" + "=" * 70)
    print("Relationships Requiring Verification:")
    print("=" * 70)
    for source, target, label in RELATIONSHIPS_TO_VERIFY:
        # Check if relationship exists
        exists = any(
            rel['source'] == source and 
            rel['target'] == target and 
            rel['label'] == label
            for rel in relationships
        )
        if exists:
            print(f"  VERIFY: {source} -> {target} ({label})")
        else:
            print(f"  NOT FOUND: {source} -> {target} ({label})")
    
    # Save cleaned relationships
    print("\n" + "=" * 70)
    print(f"Saving cleaned relationships...")
    print("=" * 70)
    
    # Create backup
    backup_path = RELATIONSHIPS_CSV.with_suffix('.csv.backup')
    if RELATIONSHIPS_CSV.exists():
        import shutil
        shutil.copy2(RELATIONSHIPS_CSV, backup_path)
        print(f"  Created backup: {backup_path.name}")
    
    save_relationships(RELATIONSHIPS_CSV, relationships)
    print(f"  Saved {len(relationships)} relationships")
    print(f"  Removed {removed_count} incorrect/unverified relationship(s)")
    
    print("\n" + "=" * 70)
    print("[OK] Relationship verification complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review the relationships marked for verification")
    print("  2. Run combine_all_data.py to reload relationships")
    print("  3. Restart the application to see updated graph")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
