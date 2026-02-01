#!/usr/bin/env python3
"""Check entity types in database and identify misclassified individuals"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "prh.db"

# Known individuals from relationships
KNOWN_INDIVIDUALS = [
    "Doug Wolfe", "Glenn Gaffney", "Donald Kerr", 
    "Sean Kirkpatrick", "Paul Kaminsky", "Mark Moahan"
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("Entity Type Distribution:")
print("=" * 70)
cursor.execute('SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type ORDER BY COUNT(*) DESC')
for row in cursor.fetchall():
    print(f"  {row[0] or 'NULL'}: {row[1]}")

print("\n" + "=" * 70)
print("Checking Known Individuals:")
print("=" * 70)
for name in KNOWN_INDIVIDUALS:
    cursor.execute('SELECT display_name, entity_type FROM entities WHERE display_name = ?', (name,))
    row = cursor.fetchone()
    if row:
        status = "✓" if row[1] == "Individual" else "✗ MISCLASSIFIED"
        print(f"  {status} {row[0]}: {row[1]}")
    else:
        print(f"  ? {name}: NOT FOUND IN DATABASE")

print("\n" + "=" * 70)
print("Entities with 'Individual' type:")
print("=" * 70)
cursor.execute('SELECT display_name, entity_type FROM entities WHERE entity_type = "Individual"')
individuals = cursor.fetchall()
if individuals:
    for row in individuals:
        print(f"  {row[0]}")
else:
    print("  No entities found with type 'Individual'")

print("\n" + "=" * 70)
print("Entities that might be individuals (name patterns):")
print("=" * 70)
cursor.execute('''
    SELECT display_name, entity_type 
    FROM entities 
    WHERE entity_type != "Individual" 
    AND (
        display_name LIKE "% %" 
        AND display_name NOT LIKE "%Corporation%"
        AND display_name NOT LIKE "%Inc%"
        AND display_name NOT LIKE "%LLC%"
        AND display_name NOT LIKE "%Ltd%"
        AND display_name NOT LIKE "%Company%"
        AND display_name NOT LIKE "%Laboratory%"
        AND display_name NOT LIKE "%Institute%"
        AND display_name NOT LIKE "%Agency%"
        AND display_name NOT LIKE "%Office%"
        AND display_name NOT LIKE "%Program%"
        AND display_name NOT LIKE "%Project%"
    )
    ORDER BY display_name
    LIMIT 20
''')
potential_individuals = cursor.fetchall()
if potential_individuals:
    for row in potential_individuals:
        print(f"  {row[0]}: {row[1]}")

print("\n" + "=" * 70)
print("Total entities in database:")
print("=" * 70)
cursor.execute('SELECT COUNT(*) FROM entities')
total = cursor.fetchone()[0]
print(f"  {total} entities")

conn.close()
