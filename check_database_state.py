#!/usr/bin/env python3
"""Check current database state"""
import sys
from pathlib import Path
import yaml

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, Relationship, MoneyFlow, Award, FOIATarget

PROJECT_ROOT = Path(__file__).parent
config = yaml.safe_load(open(PROJECT_ROOT / "config.yaml"))
engine = init_database(config['database']['path'])
db = get_session_maker(engine)()

print("Current Database State:")
print(f"  Entities: {db.query(Entity).count()}")
print(f"  Relationships: {db.query(Relationship).count()}")
print(f"  Money Flows: {db.query(MoneyFlow).count()}")
print(f"  Awards: {db.query(Award).count()}")
print(f"  FOIA Targets: {db.query(FOIATarget).count()}")

print("\nSample entities (first 15):")
for e in db.query(Entity).limit(15).all():
    marker = " [NRO]" if e.entity_id.startswith("nro_seed_") or e.display_name == "NRO" else ""
    print(f"  - {e.display_name} ({e.entity_type}){marker}")

nro_entity = db.query(Entity).filter(Entity.display_name == "NRO").first()
nro_entities = db.query(Entity).filter(Entity.entity_id.like("nro_seed_%")).count()
nro_relationships = db.query(Relationship).filter(Relationship.source == "NRO").count()

print(f"\nNRO Data:")
print(f"  NRO entity exists: {nro_entity is not None}")
print(f"  NRO seed entities: {nro_entities}")
print(f"  NRO relationships: {nro_relationships}")

db.close()
