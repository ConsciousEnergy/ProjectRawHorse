#!/usr/bin/env python3
"""
Rebuild Database Script for Project RawHorse

This script performs a clean rebuild of the database from all source files.
It drops all tables and reloads all data with correct entity types.

Usage:
    python rebuild_database.py [--dry-run] [--force]

Options:
    --dry-run   Show what would be done without making changes
    --force     Skip confirmation prompt
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, Entity, init_database, get_session_maker, get_database_url
from data_loader import (
    load_all_data, 
    load_entity_type_overrides,
    get_entity_type,
    ENTITY_TYPE_OVERRIDES,
    VALID_ENTITY_TYPES
)
import yaml
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(project_root: str) -> dict:
    """Load configuration from config.yaml"""
    config_path = os.path.join(project_root, "backend", "config.yaml")
    if not os.path.exists(config_path):
        # Try alternative location
        config_path = os.path.join(project_root, "config.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def count_entities_by_type(db) -> dict:
    """Count entities grouped by type"""
    counts = {}
    entities = db.query(Entity).all()
    for entity in entities:
        entity_type = entity.entity_type or "Unknown"
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return counts


def verify_entity_types(db) -> list:
    """Verify all entities have valid types and return any issues"""
    issues = []
    entities = db.query(Entity).all()
    for entity in entities:
        if not entity.entity_type:
            issues.append(f"Missing type: {entity.display_name}")
        elif entity.entity_type not in VALID_ENTITY_TYPES:
            issues.append(f"Invalid type '{entity.entity_type}': {entity.display_name}")
    return issues


def rebuild_database(project_root: str, dry_run: bool = False, force: bool = False):
    """Perform a clean rebuild of the database
    
    Args:
        project_root: Absolute path to project root
        dry_run: If True, only show what would be done
        force: If True, skip confirmation prompt
    """
    logger.info("=" * 60)
    logger.info("Project RawHorse Database Rebuild")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config(project_root)
    logger.info(f"Loaded configuration from {project_root}")
    
    # Load entity type overrides
    overrides_path = os.path.join(project_root, "data", "entities", "entity_type_overrides.csv")
    if os.path.exists(overrides_path):
        count = load_entity_type_overrides(overrides_path)
        logger.info(f"Loaded {count} entity type overrides")
    else:
        logger.warning(f"Overrides file not found: {overrides_path}")
    
    # Database path
    db_path = os.path.join(project_root, "data", "prh.db")
    
    if dry_run:
        logger.info("[DRY RUN] Would perform the following actions:")
        logger.info(f"  - Delete database: {db_path}")
        logger.info(f"  - Recreate all tables")
        logger.info(f"  - Load entities from {config['data_sources']['entities_dir']}")
        logger.info(f"  - Load relationships and money flows")
        logger.info(f"  - Apply {len(ENTITY_TYPE_OVERRIDES)} type overrides")
        return
    
    # Confirmation
    if not force:
        if os.path.exists(db_path):
            print(f"\nWARNING: This will delete the existing database at:\n  {db_path}")
            print("\nThis action cannot be undone.")
            response = input("Are you sure you want to continue? [y/N]: ")
            if response.lower() != 'y':
                logger.info("Rebuild cancelled by user")
                return
    
    # Delete existing database
    if os.path.exists(db_path):
        logger.info(f"Deleting existing database: {db_path}")
        os.remove(db_path)
    
    # Create data directory if needed
    data_dir = os.path.dirname(db_path)
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize fresh database
    logger.info("Initializing new database...")
    engine = init_database(db_path)
    SessionLocal = get_session_maker(engine)
    
    # Load all data
    with SessionLocal() as db:
        logger.info("Loading all data...")
        load_all_data(db, config, project_root)
        
        # Show results
        logger.info("\n" + "=" * 60)
        logger.info("DATABASE REBUILD COMPLETE")
        logger.info("=" * 60)
        
        # Count entities by type
        counts = count_entities_by_type(db)
        logger.info("\nEntity counts by type:")
        for entity_type, count in sorted(counts.items()):
            logger.info(f"  {entity_type}: {count}")
        
        total = sum(counts.values())
        logger.info(f"\nTotal entities: {total}")
        
        # Verify entity types
        issues = verify_entity_types(db)
        if issues:
            logger.warning(f"\nFound {len(issues)} entity type issues:")
            for issue in issues[:10]:  # Show first 10
                logger.warning(f"  - {issue}")
            if len(issues) > 10:
                logger.warning(f"  ... and {len(issues) - 10} more")
        else:
            logger.info("\nAll entity types are valid!")
        
        # Check specific entities mentioned in the plan
        problem_entities = [
            "Maxar Technologies",
            "Planet Labs PBC",
            "Capella Space",
            "Muon Space",
            "Turion Space",
            "Albedo Space",
            "Aurora Insight",
            "HyperSat",
            "Hydrosat",
            "Orbital Sidekick",
            "Pixxel",
            "Umbra Lab, Inc.",
            "PredaSAR (Terran Orbital)"
        ]
        
        logger.info("\nVerifying previously problematic entities:")
        for name in problem_entities:
            entity = db.query(Entity).filter(Entity.display_name == name).first()
            if entity:
                status = "OK" if entity.entity_type == "Corporation" else f"WRONG ({entity.entity_type})"
                logger.info(f"  {name}: {entity.entity_type} [{status}]")
            else:
                logger.info(f"  {name}: NOT FOUND")
    
    logger.info("\nDatabase rebuild complete!")
    logger.info(f"Database location: {db_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild Project RawHorse database from source files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="Project root directory (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Determine project root
    if args.project_root:
        project_root = os.path.abspath(args.project_root)
    else:
        # Auto-detect: go up from backend directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not os.path.exists(os.path.join(project_root, "backend")):
        logger.error(f"Invalid project root: {project_root}")
        logger.error("Cannot find 'backend' directory")
        sys.exit(1)
    
    logger.info(f"Project root: {project_root}")
    
    try:
        rebuild_database(project_root, dry_run=args.dry_run, force=args.force)
    except Exception as e:
        logger.error(f"Rebuild failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
