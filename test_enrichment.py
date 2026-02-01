#!/usr/bin/env python3
"""
Test script to run enrichment on a small subset of entities
"""
import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent / "data" / "scripts"
sys.path.insert(0, str(scripts_dir))

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity
from enrich_entity_flows import research_entity_flows, save_flows_to_csv
import yaml
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

# Load configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)
db = session_maker()

try:
    print("=" * 70)
    print("Entity Flow Enrichment - Test Run")
    print("=" * 70)
    
    # Get a small sample of entities to test (3 entities)
    # Focus on well-known entities that likely have public financial info
    test_entities = db.query(Entity).filter(
        Entity.display_name.in_([
            'Peraton',
            'Lockheed Martin',
            'Perspecta'
        ])
    ).limit(3).all()
    
    # If exact matches not found, get first 5 corporations/government agencies
    if not test_entities:
        test_entities = db.query(Entity).filter(
            Entity.entity_type.in_(['Corporation', 'Government Agency'])
        ).limit(5).all()
    
    print(f"\nTesting with {len(test_entities)} entities:")
    for entity in test_entities:
        print(f"  - {entity.display_name} ({entity.entity_type})")
    
    # Create output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = PROJECT_ROOT / "data" / "financial" / f"test_enriched_flows_{timestamp}.csv"
    
    all_flows = []
    
    # Research each entity
    for i, entity in enumerate(test_entities, 1):
        print(f"\n[{i}/{len(test_entities)}] Processing {entity.display_name}...")
        try:
            flows = research_entity_flows(entity, db)
            all_flows.extend(flows)
            
            # Save incrementally
            if flows:
                save_flows_to_csv(flows, output_file)
                print(f"  Saved {len(flows)} flows to CSV")
        
        except Exception as e:
            print(f"  [ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 70)
    print(f"Test complete!")
    print(f"Total flows discovered: {len(all_flows)}")
    print(f"Output file: {output_file}")
    print("=" * 70)
    
    # Show summary
    if all_flows:
        print("\nDiscovered flows:")
        for flow in all_flows[:10]:  # Show first 10
            amount_str = f"${flow.get('amount_usd', 0):,.0f}" if flow.get('amount_usd') else "N/A"
            print(f"  {flow['source']} -> {flow.get('target', 'Unknown')}")
            print(f"    Type: {flow['relationship']}, Amount: {amount_str}")
            if flow.get('source_citation'):
                print(f"    Source: {flow['source_citation'][:80]}...")
            print()
        
        if len(all_flows) > 10:
            print(f"  ... and {len(all_flows) - 10} more flows")
        
        print("\nSummary by relationship type:")
        from collections import Counter
        rel_counts = Counter(f['relationship'] for f in all_flows)
        for rel, count in rel_counts.most_common():
            print(f"  {rel}: {count}")
    else:
        print("\nNo flows discovered. This could mean:")
        print("  - Entities don't have public financial information")
        print("  - Search queries need adjustment")
        print("  - Network/rate limiting issues")

finally:
    db.close()
