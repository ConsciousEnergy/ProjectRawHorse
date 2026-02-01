#!/usr/bin/env python3
"""
Migration script to add quality score columns to FOIA targets table
"""
import sqlite3
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "data" / "prh.db"

if not DB_PATH.exists():
    print(f"ERROR: Database not found: {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("FOIA Targets Migration: Adding Quality Score Columns")
print("=" * 70)

# Check if columns already exist
cursor.execute("PRAGMA table_info(foia_targets)")
columns = [col[1] for col in cursor.fetchall()]

new_columns = [
    ('specificity_score', 'REAL DEFAULT 0.0'),
    ('likelihood_score', 'REAL DEFAULT 0.0'),
    ('priority_score', 'REAL DEFAULT 0.0'),
    ('quality_notes', 'TEXT')
]

added = 0
for col_name, col_type in new_columns:
    if col_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE foia_targets ADD COLUMN {col_name} {col_type}")
            print(f"  [OK] Added column: {col_name}")
            added += 1
        except sqlite3.OperationalError as e:
            print(f"  [ERROR] Error adding {col_name}: {e}")
    else:
        print(f"  [-] Column already exists: {col_name}")

if added > 0:
    conn.commit()
    print(f"\n[OK] Migration complete: Added {added} column(s)")
else:
    print("\n[OK] No migration needed: All columns already exist")

conn.close()
print("=" * 70)
