#!/usr/bin/env python3
"""
Run enrichment on a sample of entities for testing
"""
import os
import sys
from pathlib import Path

# Add backend and scripts to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(scripts_dir))

import yaml
from database import init_database, get_session_maker, Entity

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Import enrichment function
from enrich_entity_flows import research_entity_flows, save_flows_to_csv

OUTPUT_DIR = PROJECT_ROOT / "data" / "financial"
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    print("=" * 60)
    print("Project RawHorse - Sample Entity Enrichment")
    print("=" * 60)
    
    db_path = PROJECT_ROOT / config['database']['path']
    engine = init_database(str(db_path))
    session_maker = get_session_maker(engine)
    db = session_maker()
    
    try:
        # Get a sample of key entities to test
        sample_entities = db.query(Entity).filter(
            Entity.display_name.in_([
                'MITRE Corporation',
                'Lockheed Martin',
                'Boeing',
                'Department of Defense'
            ])
        ).all()
        
        if not sample_entities:
            # Fallback to first 3 corporations
            sample_entities = db.query(Entity).filter(
                Entity.entity_type == 'Corporation'
            ).limit(3).all()
        
        print(f"\nTesting enrichment on {len(sample_entities)} entities:")
        for e in sample_entities:
            print(f"  - {e.display_name} ({e.entity_type})")
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"sample_flows_{timestamp}.csv"
        
        all_flows = []
        
        for i, entity in enumerate(sample_entities, 1):
            print(f"\n[{i}/{len(sample_entities)}] Processing {entity.display_name}...")
            try:
                flows = research_entity_flows(entity, db)
                all_flows.extend(flows)
                
                if flows:
                    save_flows_to_csv(flows, output_file)
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
                continue
        
        print("\n" + "=" * 60)
        print(f"Sample enrichment complete!")
        print(f"Total flows discovered: {len(all_flows)}")
        if all_flows:
            print(f"Output file: {output_file}")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
