#!/usr/bin/env python3
"""
Convenience script to run entity flow enrichment research
"""
import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent / "data" / "scripts"
sys.path.insert(0, str(scripts_dir))

from enrich_entity_flows import main

if __name__ == "__main__":
    print("\nStarting entity flow enrichment research...")
    print("This may take a while depending on the number of entities.\n")
    main()
