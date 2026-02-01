#!/usr/bin/env python3
"""Check date ranges in database"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "prh.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("Date Range Analysis")
print("=" * 70)

# Check Money Flows
cursor.execute('''
    SELECT MIN(start_date), MAX(start_date), COUNT(*) 
    FROM money_flows 
    WHERE start_date IS NOT NULL AND start_date != ''
''')
mf = cursor.fetchone()
print(f"\nMoney Flows:")
print(f"  Min Date: {mf[0]}")
print(f"  Max Date: {mf[1]}")
print(f"  Total Records: {mf[2]}")

# Check Awards
cursor.execute('''
    SELECT MIN(action_date), MAX(action_date), COUNT(*) 
    FROM awards 
    WHERE action_date IS NOT NULL AND action_date != ''
''')
aw = cursor.fetchone()
print(f"\nAwards:")
print(f"  Min Date: {aw[0]}")
print(f"  Max Date: {aw[1]}")
print(f"  Total Records: {aw[2]}")

# Check all date fields
cursor.execute('''
    SELECT 
        MIN(CASE WHEN start_date IS NOT NULL AND start_date != '' THEN start_date END) as min_mf,
        MAX(CASE WHEN start_date IS NOT NULL AND start_date != '' THEN start_date END) as max_mf,
        MIN(CASE WHEN action_date IS NOT NULL AND action_date != '' THEN action_date END) as min_aw,
        MAX(CASE WHEN action_date IS NOT NULL AND action_date != '' THEN action_date END) as max_aw
    FROM (
        SELECT start_date, NULL as action_date FROM money_flows
        UNION ALL
        SELECT NULL as start_date, action_date FROM awards
    )
''')
combined = cursor.fetchone()
print(f"\nCombined Date Range:")
print(f"  Min: {min([d for d in [combined[0], combined[2]] if d])}")
print(f"  Max: {max([d for d in [combined[1], combined[3]] if d])}")

conn.close()
