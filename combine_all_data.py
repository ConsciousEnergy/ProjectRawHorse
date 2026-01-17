#!/usr/bin/env python3
"""
Combine all datasets - reloads original data AND adds NRO data
This ensures all data is present without losing anything.
"""
import os
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, Relationship, MoneyFlow, Award, FOIATarget
from data_loader import (
    load_entities, load_money_flows, load_awards, 
    load_foia_targets, load_relationships,
    load_nro_seeds_as_entities, load_transcript_entities
)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Database path: {db_path}")

# Ask for confirmation (non-interactive mode for automation)
print("\nThis script will:")
print("  1. Load all original data files (entities, money flows, awards, FOIA, relationships)")
print("  2. Add NRO entities and relationships")
print("  3. Add UAPGerb transcript entities, relationships, and FOIA targets")
print("  4. Combine everything into one complete dataset")
print("\nNOTE: This will add data but won't delete existing data unless duplicates are found.")
print("\nStarting data combination...")

# Initialize database connection
print("\nConnecting to database...")
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)
db = session_maker()

try:
    # Get current counts
    print("\nCurrent database state:")
    entity_count_before = db.query(Entity).count()
    relationship_count_before = db.query(Relationship).count()
    money_flow_count_before = db.query(MoneyFlow).count()
    award_count_before = db.query(Award).count()
    foia_count_before = db.query(FOIATarget).count()
    
    print(f"  Entities: {entity_count_before}")
    print(f"  Relationships: {relationship_count_before}")
    print(f"  Money Flows: {money_flow_count_before}")
    print(f"  Awards: {award_count_before}")
    print(f"  FOIA Targets: {foia_count_before}")
    
    # Load original data files (these functions skip duplicates)
    print("\n" + "="*60)
    print("Loading original data files...")
    print("="*60)
    
    # Load entities
    entities_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "entities_master.csv"
    if entities_path.exists():
        print(f"\nLoading entities from: {entities_path.name}")
        entities_added = load_entities(db, str(entities_path))
        print(f"  Entities processed: {entities_added}")
    else:
        print(f"WARNING: Entities file not found: {entities_path}")
    
    # Load money flows
    money_flows_path = PROJECT_ROOT / config['data_sources']['financial_dir'] / "money_flows.csv"
    if money_flows_path.exists():
        print(f"\nLoading money flows from: {money_flows_path.name}")
        money_flows_added = load_money_flows(db, str(money_flows_path))
        print(f"  Money flows processed: {money_flows_added}")
    else:
        print(f"WARNING: Money flows file not found: {money_flows_path}")
    
    # Load awards
    awards_path = PROJECT_ROOT / config['data_sources']['financial_dir'] / "awards_master.csv"
    if awards_path.exists():
        print(f"\nLoading awards from: {awards_path.name}")
        awards_added = load_awards(db, str(awards_path))
        print(f"  Awards processed: {awards_added}")
    else:
        print(f"WARNING: Awards file not found: {awards_path}")
    
    # Load FOIA targets
    foia_path = PROJECT_ROOT / config['data_sources']['foia_dir'] / "foia_targets.csv"
    if foia_path.exists():
        print(f"\nLoading FOIA targets from: {foia_path.name}")
        foia_added = load_foia_targets(db, str(foia_path))
        print(f"  FOIA targets processed: {foia_added}")
    else:
        print(f"WARNING: FOIA targets file not found: {foia_path}")
    
    # Load original relationships
    relationships_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "entity_relationships.csv"
    if relationships_path.exists():
        print(f"\nLoading relationships from: {relationships_path.name}")
        relationships_added = load_relationships(db, str(relationships_path))
        print(f"  Relationships processed: {relationships_added}")
    else:
        print(f"WARNING: Relationships file not found: {relationships_path}")
    
    # Load NRO data
    print("\n" + "="*60)
    print("Loading NRO datasets...")
    print("="*60)
    
    # Load NRO seeds as entities
    nro_seeds_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "nro_public_partners_seeds_v2.csv"
    if nro_seeds_path.exists():
        print(f"\nLoading NRO seeds as entities from: {nro_seeds_path.name}")
        nro_entities_added = load_nro_seeds_as_entities(db, str(nro_seeds_path))
        print(f"  NRO entities added: {nro_entities_added}")
    else:
        print(f"WARNING: NRO seeds file not found: {nro_seeds_path}")
    
    # Load NRO seed edges as relationships
    nro_edges_path = PROJECT_ROOT / config['data_sources']['visualizations_dir'] / "nro_seed_edges_v2.csv"
    if nro_edges_path.exists():
        print(f"\nLoading NRO seed edges as relationships from: {nro_edges_path.name}")
        nro_relationships_added = load_relationships(db, str(nro_edges_path))
        print(f"  NRO relationships added: {nro_relationships_added}")
    else:
        print(f"WARNING: NRO edges file not found: {nro_edges_path}")
    
    # Load UAPGerb transcript data
    print("\n" + "="*60)
    print("Loading UAPGerb transcript datasets...")
    print("="*60)
    
    # Load transcript entities
    transcript_entities_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "uap_gerb_transcript_entities.csv"
    if transcript_entities_path.exists():
        print(f"\nLoading transcript entities from: {transcript_entities_path.name}")
        transcript_entities_added = load_transcript_entities(db, str(transcript_entities_path))
        print(f"  Transcript entities added: {transcript_entities_added}")
    else:
        print(f"WARNING: Transcript entities file not found: {transcript_entities_path}")
    
    # Load transcript relationships
    transcript_relationships_path = PROJECT_ROOT / config['data_sources']['entities_dir'] / "uap_gerb_transcript_relationships.csv"
    if transcript_relationships_path.exists():
        print(f"\nLoading transcript relationships from: {transcript_relationships_path.name}")
        transcript_relationships_added = load_relationships(db, str(transcript_relationships_path))
        print(f"  Transcript relationships added: {transcript_relationships_added}")
    else:
        print(f"WARNING: Transcript relationships file not found: {transcript_relationships_path}")
    
    # Load transcript FOIA targets
    transcript_foia_path = PROJECT_ROOT / config['data_sources']['foia_dir'] / "uap_gerb_transcript_foia_targets.csv"
    if transcript_foia_path.exists():
        print(f"\nLoading transcript FOIA targets from: {transcript_foia_path.name}")
        transcript_foia_added = load_foia_targets(db, str(transcript_foia_path))
        print(f"  Transcript FOIA targets added: {transcript_foia_added}")
    else:
        print(f"WARNING: Transcript FOIA targets file not found: {transcript_foia_path}")
    
    # Get final counts
    entity_count_after = db.query(Entity).count()
    relationship_count_after = db.query(Relationship).count()
    money_flow_count_after = db.query(MoneyFlow).count()
    award_count_after = db.query(Award).count()
    foia_count_after = db.query(FOIATarget).count()
    
    # Show summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Entities:        {entity_count_before:4d} -> {entity_count_after:4d} (+{entity_count_after - entity_count_before:3d})")
    print(f"Relationships:   {relationship_count_before:4d} -> {relationship_count_after:4d} (+{relationship_count_after - relationship_count_before:3d})")
    print(f"Money Flows:     {money_flow_count_before:4d} -> {money_flow_count_after:4d} (+{money_flow_count_after - money_flow_count_before:3d})")
    print(f"Awards:          {award_count_before:4d} -> {award_count_after:4d} (+{award_count_after - award_count_before:3d})")
    print(f"FOIA Targets:    {foia_count_before:4d} -> {foia_count_after:4d} (+{foia_count_after - foia_count_before:3d})")
    print("="*60)
    
    # Verify NRO data
    nro_entity = db.query(Entity).filter(Entity.display_name == "NRO").first()
    nro_entities = db.query(Entity).filter(Entity.entity_id.like("nro_seed_%")).count()
    nro_relationships = db.query(Relationship).filter(Relationship.source == "NRO").count()
    
    print(f"\nNRO Data Verification:")
    print(f"  NRO entity exists: {nro_entity is not None}")
    print(f"  NRO seed entities: {nro_entities}")
    print(f"  NRO relationships: {nro_relationships}")
    
    # Show sample of entities
    print(f"\nSample entities (showing mix of original and NRO):")
    all_entities = db.query(Entity).limit(15).all()
    for e in all_entities:
        marker = " [NRO]" if e.entity_id.startswith("nro_seed_") or e.display_name == "NRO" else ""
        print(f"  - {e.display_name} ({e.entity_type}){marker}")
    
    if db.query(Entity).count() > 15:
        print(f"  ... and {db.query(Entity).count() - 15} more entities")
    
finally:
    db.close()

print("\n" + "="*60)
print("Done! All data has been combined.")
print("Restart the application to see the updated dashboard and visualizations.")
print("="*60)
