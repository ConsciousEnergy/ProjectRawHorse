#!/usr/bin/env python3
"""
Reload all FOIA targets from CSV files (with duplicate checking)
"""
import os
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, FOIATarget
from data_loader import load_foia_targets

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Reloading FOIA targets into: {db_path}")
print("=" * 70)

# Initialize database connection
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)
db = session_maker()

try:
    # Get current count
    count_before = db.query(FOIATarget).count()
    print(f"\nCurrent FOIA targets in database: {count_before}")
    
    # Load original FOIA targets
    foia_path = PROJECT_ROOT / config['data_sources']['foia_dir'] / "foia_targets.csv"
    if foia_path.exists():
        print(f"\nLoading original FOIA targets from: {foia_path.name}")
        added1 = load_foia_targets(db, str(foia_path))
        print(f"  Added: {added1}")
    else:
        print(f"\nOriginal FOIA targets file not found: {foia_path}")
    
    # Load transcript FOIA targets
    transcript_foia_path = PROJECT_ROOT / config['data_sources']['foia_dir'] / "uap_gerb_transcript_foia_targets.csv"
    if transcript_foia_path.exists():
        print(f"\nLoading transcript FOIA targets from: {transcript_foia_path.name}")
        added2 = load_foia_targets(db, str(transcript_foia_path))
        print(f"  Added: {added2}")
    else:
        print(f"\nTranscript FOIA targets file not found: {transcript_foia_path}")
    
    # Get final count
    count_after = db.query(FOIATarget).count()
    
    print("\n" + "=" * 70)
    print(f"FOIA Targets: {count_before} -> {count_after} (+{count_after - count_before})")
    print("=" * 70)
    
    print("\n[OK] FOIA targets reloaded!")
    
finally:
    db.close()
