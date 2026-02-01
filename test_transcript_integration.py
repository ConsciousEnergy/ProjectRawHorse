#!/usr/bin/env python3
"""
Test script to verify UAPGerb transcript data integration
"""
import os
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, Relationship, FOIATarget

# Get project root directory
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Testing database: {db_path}")
print("=" * 70)

# Initialize database connection
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)
db = session_maker()

try:
    # Check for transcript entities
    transcript_entities = db.query(Entity).filter(
        Entity.entity_id.like("uapgerb_%")
    ).all()
    
    print(f"\nTranscript Entities Found: {len(transcript_entities)}")
    
    if transcript_entities:
        print("\nSample transcript entities:")
        for entity in transcript_entities[:10]:
            print(f"  - {entity.display_name} ({entity.entity_type}) [ID: {entity.entity_id}]")
        if len(transcript_entities) > 10:
            print(f"  ... and {len(transcript_entities) - 10} more")
    else:
        print("  No transcript entities found. Run combine_all_data.py first.")
    
    # Check for transcript relationships
    # We need to check relationships that might reference transcript entities
    # Since relationships use display names, we'll check for known transcript entity names
    transcript_entity_names = {e.display_name for e in transcript_entities}
    
    transcript_relationships = []
    all_relationships = db.query(Relationship).all()
    for rel in all_relationships:
        if rel.source in transcript_entity_names or rel.target in transcript_entity_names:
            transcript_relationships.append(rel)
    
    print(f"\nTranscript Relationships Found: {len(transcript_relationships)}")
    
    if transcript_relationships:
        print("\nSample transcript relationships:")
        for rel in transcript_relationships[:10]:
            print(f"  - {rel.source} -> {rel.target} ({rel.label})")
        if len(transcript_relationships) > 10:
            print(f"  ... and {len(transcript_relationships) - 10} more")
    else:
        print("  No transcript relationships found.")
    
    # Check for transcript FOIA targets
    transcript_foia = db.query(FOIATarget).all()
    
    # Filter for transcript FOIA targets (we can identify by checking for agencies mentioned in transcript)
    transcript_agencies = {'NRO', 'CIA DS&T', 'DOE OICI', 'DOE NEST', 'DARPA SID', 
                          'MITER Corporation', 'OUSD', 'DDNI ATNF', 'Sandia National Laboratories',
                          'Edwards 412 Test Wing', 'Oak Ridge National Laboratory'}
    
    transcript_foia_targets = [
        foia for foia in transcript_foia 
        if any(agency in foia.agency for agency in transcript_agencies)
    ]
    
    print(f"\nTranscript FOIA Targets Found: {len(transcript_foia_targets)}")
    
    if transcript_foia_targets:
        print("\nSample transcript FOIA targets:")
        for foia in transcript_foia_targets[:5]:
            print(f"  - {foia.agency}: {foia.record_request[:60]}...")
        if len(transcript_foia_targets) > 5:
            print(f"  ... and {len(transcript_foia_targets) - 5} more")
    else:
        print("  No transcript FOIA targets found.")
    
    # Check for duplicates
    print("\n" + "=" * 70)
    print("Duplicate Check:")
    
    # Check for entities with same display_name but different IDs
    all_entities = db.query(Entity).all()
    name_to_ids = {}
    for entity in all_entities:
        if entity.display_name not in name_to_ids:
            name_to_ids[entity.display_name] = []
        name_to_ids[entity.display_name].append(entity.entity_id)
    
    duplicates = {name: ids for name, ids in name_to_ids.items() if len(ids) > 1}
    
    if duplicates:
        print(f"  WARNING: Found {len(duplicates)} entities with duplicate display names:")
        for name, ids in list(duplicates.items())[:5]:
            print(f"    - {name}: {ids}")
        if len(duplicates) > 5:
            print(f"    ... and {len(duplicates) - 5} more duplicates")
    else:
        print("  No duplicate entities found. [OK]")
    
    # Overall summary
    print("\n" + "=" * 70)
    print("Overall Summary:")
    print(f"  Total Entities: {db.query(Entity).count()}")
    print(f"  Total Relationships: {db.query(Relationship).count()}")
    print(f"  Total FOIA Targets: {db.query(FOIATarget).count()}")
    print(f"  Transcript Entities: {len(transcript_entities)}")
    print(f"  Transcript Relationships: {len(transcript_relationships)}")
    print(f"  Transcript FOIA Targets: {len(transcript_foia_targets)}")
    
    if len(transcript_entities) > 0:
        print("\n[OK] Transcript data integration appears successful!")
    else:
        print("\n[WARNING] No transcript entities found. Run combine_all_data.py to load data.")

finally:
    db.close()
