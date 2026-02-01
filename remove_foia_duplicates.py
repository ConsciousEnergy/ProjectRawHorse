#!/usr/bin/env python3
"""
Remove duplicate FOIA targets from database
Keeps the first occurrence of each unique (agency, record_request) pair
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "prh.db"

if not DB_PATH.exists():
    print(f"ERROR: Database not found: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("Removing Duplicate FOIA Targets")
print("=" * 70)

# Find duplicates
cursor.execute('''
    SELECT agency, record_request, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM foia_targets 
    GROUP BY agency, record_request 
    HAVING COUNT(*) > 1
    ORDER BY count DESC
''')
duplicates = cursor.fetchall()

if not duplicates:
    print("\nNo duplicates found!")
    conn.close()
    exit(0)

print(f"\nFound {len(duplicates)} sets of duplicates:\n")

total_removed = 0
for agency, request, count, ids in duplicates:
    id_list = [int(id_str) for id_str in ids.split(',')]
    # Keep the first ID (lowest), remove the rest
    keep_id = min(id_list)
    remove_ids = [id for id in id_list if id != keep_id]
    
    print(f"Agency: {agency}")
    print(f"  Request: {request[:60]}...")
    print(f"  Keeping ID: {keep_id}")
    print(f"  Removing IDs: {remove_ids}")
    
    # Delete duplicates
    placeholders = ','.join(['?'] * len(remove_ids))
    cursor.execute(f'DELETE FROM foia_targets WHERE id IN ({placeholders})', remove_ids)
    total_removed += len(remove_ids)
    print()

conn.commit()

# Verify
cursor.execute('SELECT COUNT(*) FROM foia_targets')
remaining = cursor.fetchone()[0]

print("=" * 70)
print(f"Removed {total_removed} duplicate FOIA targets")
print(f"Remaining FOIA targets: {remaining}")
print("=" * 70)

conn.close()
