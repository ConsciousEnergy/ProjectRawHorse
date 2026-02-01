#!/usr/bin/env python3
"""
Load UAPGerb transcript data into database
"""
import os
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, Relationship, FOIATarget
from data_loader import load_transcript_entities, load_relationships, load_foia_targets

# Get project root directory
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Loading transcript data into: {db_path}")
print("=" * 70)

# Initialize database connection
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)
db = session_maker()

try:
    # Get current counts
    print("\nCurrent database state:")
    entity_count_before = db.query(Entity).count()
    relationship_count_before = db.query(Relationship).count()
    foia_count_before = db.query(FOIATarget).count()
    
    print(f"  Entities: {entity_count_before}")
    print(f"  Relationships: {relationship_count_before}")
    print(f"  FOIA Targets: {foia_count_before}")
    
    # Load transcript entities
    transcript_entities_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "uap_gerb_transcript_entities.csv"
    if transcript_entities_path.exists():
        print(f"\nLoading transcript entities from: {transcript_entities_path.name}")
        entities_added = load_transcript_entities(db, str(transcript_entities_path))
        print(f"  Entities added: {entities_added}")
    else:
        print(f"WARNING: Transcript entities file not found: {transcript_entities_path}")
    
    # Load transcript relationships
    transcript_relationships_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "uap_gerb_transcript_relationships.csv"
    if transcript_relationships_path.exists():
        print(f"\nLoading transcript relationships from: {transcript_relationships_path.name}")
        relationships_added = load_relationships(db, str(transcript_relationships_path))
        print(f"  Relationships added: {relationships_added}")
    else:
        print(f"WARNING: Transcript relationships file not found: {transcript_relationships_path}")
    
    # Load transcript FOIA targets
    transcript_foia_path = PROJECT_ROOT / config['data_sources']['foia_dir'] / "uap_gerb_transcript_foia_targets.csv"
    if transcript_foia_path.exists():
        print(f"\nLoading transcript FOIA targets from: {transcript_foia_path.name}")
        foia_added = load_foia_targets(db, str(transcript_foia_path))
        print(f"  FOIA targets added: {foia_added}")
    else:
        print(f"WARNING: Transcript FOIA targets file not found: {transcript_foia_path}")
    
    # Get final counts
    entity_count_after = db.query(Entity).count()
    relationship_count_after = db.query(Relationship).count()
    foia_count_after = db.query(FOIATarget).count()
    
    # Show summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Entities:        {entity_count_before:4d} -> {entity_count_after:4d} (+{entity_count_after - entity_count_before:3d})")
    print(f"Relationships:   {relationship_count_before:4d} -> {relationship_count_after:4d} (+{relationship_count_after - relationship_count_before:3d})")
    print(f"FOIA Targets:    {foia_count_before:4d} -> {foia_count_after:4d} (+{foia_count_after - foia_count_before:3d})")
    print("=" * 70)
    
    # Verify transcript data
    transcript_entities = db.query(Entity).filter(Entity.entity_id.like("uapgerb_%")).count()
    print(f"\nTranscript Entities in DB: {transcript_entities}")
    
    print("\n[OK] Transcript data loading complete!")
    
finally:
    db.close()
