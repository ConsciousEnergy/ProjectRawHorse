#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/prh.db')
cursor = conn.cursor()
cursor.execute("SELECT source, target, relationship, amount_usd, start_date FROM money_flows WHERE source LIKE '%Lockheed%' OR target LIKE '%Lockheed%'")
flows = cursor.fetchall()
print(f'Existing Lockheed Martin flows: {len(flows)}')
for f in flows:
    amount_str = f'${f[3]:,.0f}' if f[3] else 'No amount'
    date_str = f' | {f[4]}' if f[4] else ''
    print(f'  {f[0]} -> {f[1]} | {f[2]} | {amount_str}{date_str}')
conn.close()
