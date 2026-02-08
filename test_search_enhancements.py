"""
Quick test for backend search enhancements (alias, amount, fuzzy).
Run from project root with: python test_search_enhancements.py
Requires backend on PYTHONPATH and database initialized.
"""
import sys
import os

# Ensure backend and project root are on path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))
os.chdir(PROJECT_ROOT)

import yaml
from database import init_database, get_session_maker
from routers.search import search_entities, search_money_flows

def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    db_path = os.path.join(PROJECT_ROOT, config["database"]["path"])
    engine = init_database(db_path)
    session_maker = get_session_maker(engine)
    db = session_maker()

    ok = 0
    # 1) National Geospatial -> NGA (multi-word / alias)
    r1 = search_entities(db, "National Geospatial", limit=10)
    nga = [x for x in r1 if "NGA" in x["title"] or "National Geospatial" in x["title"]]
    if nga:
        ok += 1
        print("1. National Geospatial -> NGA: PASS (found", len(nga), "NGA-related)")
    else:
        print("1. National Geospatial -> NGA: FAIL (found", len(r1), "results, none NGA)")

    # 2) 223 -> money flow ~223M (amount-aware)
    r2 = search_money_flows(db, "223", limit=10)
    big = [x for x in r2 if x.get("metadata", {}).get("amount") and x["metadata"]["amount"] > 100e6]
    if r2 and len(big) > 0:
        ok += 1
        print("2. 223 -> $223M flows: PASS (found", len(r2), "results,", len(big), "with amount > 100M)")
    else:
        print("2. 223 -> $223M flows:", "FAIL" if not r2 else "PASS (no 223M in DB)", "- found", len(r2))

    # 3) Pereton (typo) -> Peraton (fuzzy)
    r3 = search_entities(db, "Pereton", limit=10)
    peraton = [x for x in r3 if "Peraton" in x["title"]]
    if peraton:
        ok += 1
        print("3. Pereton -> Peraton: PASS (fuzzy match)")
    else:
        print("3. Pereton -> Peraton: FAIL (found", len(r3), "results)")

    db.close()
    print("\nResult:", ok, "/ 3 passed")
    return 0 if ok == 3 else 1

if __name__ == "__main__":
    sys.exit(main())
