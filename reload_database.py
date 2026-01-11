#!/usr/bin/env python3
"""
Reload database with all data including new NRO datasets
Run this script to refresh the database with latest data files
"""
import os
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker
from data_loader import load_all_data, is_database_populated

# Get project root directory
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Database path: {db_path}")

# Ask for confirmation
response = input("This will reload all data. Continue? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled.")
    sys.exit(0)

# Remove existing database if it exists
if db_path.exists():
    print(f"Removing existing database: {db_path}")
    db_path.unlink()

# Initialize new database
print("Initializing database...")
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)

# Load all data
print("Loading data...")
db = session_maker()
try:
    load_all_data(db, config, str(PROJECT_ROOT))
    print("Data loading complete!")
    
    # Show summary
    from database import Entity, MoneyFlow, Award, FOIATarget, Relationship
    
    entity_count = db.query(Entity).count()
    money_flow_count = db.query(MoneyFlow).count()
    award_count = db.query(Award).count()
    foia_count = db.query(FOIATarget).count()
    relationship_count = db.query(Relationship).count()
    
    print("\nDatabase Summary:")
    print(f"  Entities: {entity_count}")
    print(f"  Money Flows: {money_flow_count}")
    print(f"  Awards: {award_count}")
    print(f"  FOIA Targets: {foia_count}")
    print(f"  Relationships: {relationship_count}")
finally:
    db.close()

print("\nDone! You can now start the application.")
