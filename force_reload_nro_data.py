#!/usr/bin/env python3
"""
Force reload NRO data into existing database
This script adds NRO entities and relationships to an existing database
without deleting all existing data.
"""
import os
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, Relationship
from data_loader import load_nro_seeds_as_entities, load_relationships

# Get project root directory
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Database path: {db_path}")

if not db_path.exists():
    print(f"ERROR: Database not found at {db_path}")
    print("Please start the application first to create the database.")
    sys.exit(1)

# Initialize database connection
print("Connecting to database...")
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)

# Load NRO data
print("\nLoading NRO data...")
db = session_maker()
try:
    # Check current counts
    entity_count_before = db.query(Entity).count()
    relationship_count_before = db.query(Relationship).count()
    
    print(f"Current entities: {entity_count_before}")
    print(f"Current relationships: {relationship_count_before}")
    
    # Load NRO seeds as entities
    nro_seeds_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "nro_public_partners_seeds_v2.csv"
    if nro_seeds_path.exists():
        print("\nLoading NRO seeds as entities...")
        nro_entities_added = load_nro_seeds_as_entities(db, str(nro_seeds_path))
        print(f"Added {nro_entities_added} NRO entities")
    else:
        print(f"WARNING: NRO seeds file not found at {nro_seeds_path}")
    
    # Load NRO edges as relationships
    nro_edges_path = PROJECT_ROOT / config['data_sources']['visualizations_dir'] / "nro_seed_edges_v2.csv"
    if nro_edges_path.exists():
        print("\nLoading NRO seed edges as relationships...")
        # Check if NRO relationships already exist
        existing_nro_rels = db.query(Relationship).filter(
            Relationship.source == "NRO"
        ).count()
        
        if existing_nro_rels > 0:
            print(f"Found {existing_nro_rels} existing NRO relationships")
            response = input("Delete existing NRO relationships and reload? (yes/no): ")
            if response.lower() == 'yes':
                db.query(Relationship).filter(Relationship.source == "NRO").delete()
                db.commit()
                print("Deleted existing NRO relationships")
            else:
                print("Skipping NRO relationships (already exist)")
        
        if existing_nro_rels == 0 or response.lower() == 'yes':
            nro_rels_added = load_relationships(db, str(nro_edges_path))
            print(f"Added {nro_rels_added} NRO relationships")
    else:
        print(f"WARNING: NRO edges file not found at {nro_edges_path}")
    
    # Show final counts
    entity_count_after = db.query(Entity).count()
    relationship_count_after = db.query(Relationship).count()
    
    print("\n" + "="*50)
    print("Summary:")
    print(f"  Entities: {entity_count_before} -> {entity_count_after} (+{entity_count_after - entity_count_before})")
    print(f"  Relationships: {relationship_count_before} -> {relationship_count_after} (+{relationship_count_after - relationship_count_before})")
    print("="*50)
    
    # Verify NRO entity exists
    nro_entity = db.query(Entity).filter(Entity.display_name == "NRO").first()
    if nro_entity:
        print(f"\n✓ NRO entity found: {nro_entity.display_name} ({nro_entity.entity_type})")
    else:
        print("\n✗ WARNING: NRO entity not found in database")
    
    # Count NRO relationships
    nro_relationship_count = db.query(Relationship).filter(
        Relationship.source == "NRO"
    ).count()
    print(f"✓ NRO relationships: {nro_relationship_count}")
    
finally:
    db.close()

print("\nDone! Restart the application to see the updated data.")
