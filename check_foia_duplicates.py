#!/usr/bin/env python3
"""Check for duplicate FOIA targets in database"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "prh.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("FOIA Target Duplicate Check")
print("=" * 70)

# Check for exact duplicates (same agency and record_request)
cursor.execute('''
    SELECT agency, record_request, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM foia_targets 
    GROUP BY agency, record_request 
    HAVING COUNT(*) > 1
    ORDER BY count DESC
''')
duplicates = cursor.fetchall()

if duplicates:
    print(f"\nFound {len(duplicates)} sets of duplicate FOIA targets:\n")
    for agency, request, count, ids in duplicates:
        print(f"Agency: {agency}")
        print(f"  Request: {request[:80]}...")
        print(f"  Count: {count}")
        print(f"  IDs: {ids}")
        print()
else:
    print("\nNo exact duplicates found (same agency + record_request)")

# Check for similar duplicates (same agency, similar request)
cursor.execute('''
    SELECT id, agency, record_request 
    FROM foia_targets 
    ORDER BY agency, record_request
''')
all_targets = cursor.fetchall()

print("\n" + "=" * 70)
print("Similar FOIA Targets (same agency, similar requests):")
print("=" * 70)

similar_count = 0
for i, (id1, agency1, req1) in enumerate(all_targets):
    for id2, agency2, req2 in all_targets[i+1:]:
        if agency1 == agency2 and id1 != id2:
            # Check if requests are very similar (80% overlap)
            words1 = set(req1.lower().split())
            words2 = set(req2.lower().split())
            if words1 and words2:
                overlap = len(words1 & words2) / len(words1 | words2)
                if overlap > 0.8:
                    similar_count += 1
                    if similar_count <= 10:  # Show first 10
                        print(f"\nSimilar targets (overlap: {overlap:.0%}):")
                        print(f"  ID {id1}: {req1[:60]}...")
                        print(f"  ID {id2}: {req2[:60]}...")

if similar_count > 10:
    print(f"\n... and {similar_count - 10} more similar pairs")

# Total count
cursor.execute('SELECT COUNT(*) FROM foia_targets')
total = cursor.fetchone()[0]
print(f"\n" + "=" * 70)
print(f"Total FOIA Targets: {total}")
print("=" * 70)

conn.close()
