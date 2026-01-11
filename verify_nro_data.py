#!/usr/bin/env python3
"""Quick script to verify NRO data is in the database"""
import sys
from pathlib import Path
import yaml

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, Relationship

PROJECT_ROOT = Path(__file__).parent
config = yaml.safe_load(open(PROJECT_ROOT / "config.yaml"))
engine = init_database(config['database']['path'])
db = get_session_maker(engine)()

nro_entity = db.query(Entity).filter(Entity.display_name == "NRO").first()
nro_entities = db.query(Entity).filter(Entity.entity_id.like("nro_seed_%")).count()
nro_relationships = db.query(Relationship).filter(Relationship.source == "NRO").count()

print(f"NRO entity exists: {nro_entity is not None}")
print(f"NRO seed entities: {nro_entities}")
print(f"NRO relationships: {nro_relationships}")
print(f"Total entities: {db.query(Entity).count()}")
print(f"Total relationships: {db.query(Relationship).count()}")

db.close()
