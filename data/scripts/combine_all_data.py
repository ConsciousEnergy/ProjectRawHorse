#!/usr/bin/env python3
"""
Combine and reload all data sources into the database
Ensures data consistency across all application routes

Usage:
    python combine_all_data.py              # Full reload
    python combine_all_data.py --append     # Append new data only
    python combine_all_data.py --check      # Check data integrity
"""
import os
import sys
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import (
    init_database, get_session_maker, Base,
    Entity, MoneyFlow, MaterialsFlow, Award, FOIATarget, Relationship, DataVersion
)
import yaml
from sqlalchemy import text

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

# Load configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)


def normalize_name(name: str) -> str:
    """Normalize entity name for consistent matching"""
    return name.strip().upper().replace('"', '').replace("'", "")


def generate_entity_id(name: str) -> str:
    """Generate consistent entity ID from name"""
    import hashlib
    normalized = normalize_name(name)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def load_csv_data(file_path: Path) -> List[Dict]:
    """Load data from CSV file"""
    if not file_path.exists():
        return []
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data


def count_records(db_session) -> Dict[str, int]:
    """Count records in all tables"""
    return {
        'entities': db_session.query(Entity).count(),
        'money_flows': db_session.query(MoneyFlow).count(),
        'materials_flows': db_session.query(MaterialsFlow).count(),
        'awards': db_session.query(Award).count(),
        'foia_targets': db_session.query(FOIATarget).count(),
        'relationships': db_session.query(Relationship).count(),
    }


def load_entities(db_session, data_dir: Path, append: bool = False) -> int:
    """Load entities from all entity CSV files"""
    entity_files = list(data_dir.glob('entities/**/*.csv'))
    entity_files.extend(data_dir.glob('entities/*.csv'))
    
    loaded = 0
    existing_ids = set()
    
    if append:
        existing_ids = {e.entity_id for e in db_session.query(Entity.entity_id).all()}
    
    for entity_file in entity_files:
        print(f"  Loading entities from: {entity_file.name}")
        data = load_csv_data(entity_file)
        
        for row in data:
            entity_id = row.get('entity_id') or generate_entity_id(row.get('display_name', ''))
            
            if append and entity_id in existing_ids:
                continue
            
            # Check if entity already exists
            existing = db_session.query(Entity).filter(Entity.entity_id == entity_id).first()
            
            if existing:
                # Update if needed
                if row.get('intel_stack_level') and not existing.intel_stack_level:
                    try:
                        existing.intel_stack_level = int(row['intel_stack_level'])
                    except (ValueError, TypeError):
                        pass
            else:
                # Create new entity
                entity = Entity(
                    entity_id=entity_id,
                    display_name=row.get('display_name', '').strip(),
                    normalized_name=normalize_name(row.get('normalized_name', row.get('display_name', ''))),
                    entity_type=row.get('entity_type'),
                    intel_stack_level=int(row.get('intel_stack_level')) if row.get('intel_stack_level') else None
                )
                db_session.add(entity)
                loaded += 1
                existing_ids.add(entity_id)
        
        db_session.commit()
    
    return loaded


def load_money_flows(db_session, data_dir: Path, append: bool = False) -> int:
    """Load money flows from CSV files"""
    flow_files = list(data_dir.glob('financial/**/*.csv'))
    flow_files.extend(data_dir.glob('financial/*.csv'))
    
    loaded = 0
    existing_edge_ids = set()
    
    if append:
        existing_edge_ids = {m.edge_id for m in db_session.query(MoneyFlow.edge_id).all() if m.edge_id}
    
    for flow_file in flow_files:
        print(f"  Loading money flows from: {flow_file.name}")
        data = load_csv_data(flow_file)
        
        for row in data:
            edge_id = row.get('edge_id')
            
            if not edge_id:
                import hashlib
                key = f"{row.get('source')}|{row.get('target')}|{row.get('relationship')}"
                edge_id = hashlib.md5(key.encode()).hexdigest()[:16]
            
            if append and edge_id in existing_edge_ids:
                continue
            
            existing = db_session.query(MoneyFlow).filter(MoneyFlow.edge_id == edge_id).first()
            if existing:
                continue
            
            # Parse amount
            amount = None
            if row.get('amount_usd'):
                try:
                    amount = float(str(row['amount_usd']).replace(',', '').replace('$', ''))
                except (ValueError, TypeError):
                    pass
            
            # Parse date
            start_date = None
            if row.get('start_date'):
                try:
                    from dateutil import parser
                    start_date = parser.parse(row['start_date']).date()
                except:
                    pass
            
            flow = MoneyFlow(
                source=row.get('source', '').strip(),
                target=row.get('target', '').strip(),
                relationship=row.get('relationship'),
                amount_usd=amount,
                start_date=start_date,
                source_citation=row.get('source_citation'),
                edge_id=edge_id,
                source_norm=normalize_name(row.get('source', '')),
                target_norm=normalize_name(row.get('target', ''))
            )
            db_session.add(flow)
            loaded += 1
            existing_edge_ids.add(edge_id)
        
        db_session.commit()
    
    return loaded


def load_materials_flows(db_session, data_dir: Path, append: bool = False) -> int:
    """Load materials flows from CSV files"""
    flow_files = list(data_dir.glob('materials/**/*.csv'))
    flow_files.extend(data_dir.glob('materials/*.csv'))
    
    loaded = 0
    existing_edge_ids = set()
    
    if append:
        existing_edge_ids = {m.edge_id for m in db_session.query(MaterialsFlow.edge_id).all() if m.edge_id}
    
    for flow_file in flow_files:
        print(f"  Loading materials flows from: {flow_file.name}")
        data = load_csv_data(flow_file)
        
        for row in data:
            edge_id = row.get('edge_id')
            
            if not edge_id:
                import hashlib
                key = f"MAT|{row.get('source')}|{row.get('target')}|{row.get('material_type')}"
                edge_id = hashlib.md5(key.encode()).hexdigest()[:16]
            
            if append and edge_id in existing_edge_ids:
                continue
            
            existing = db_session.query(MaterialsFlow).filter(MaterialsFlow.edge_id == edge_id).first()
            if existing:
                continue
            
            # Parse date
            start_date = None
            if row.get('start_date'):
                try:
                    from dateutil import parser
                    start_date = parser.parse(row['start_date']).date()
                except:
                    pass
            
            flow = MaterialsFlow(
                source=row.get('source', '').strip(),
                target=row.get('target', '').strip(),
                material_type=row.get('material_type'),
                relationship=row.get('relationship'),
                description=row.get('description'),
                start_date=start_date,
                source_citation=row.get('source_citation'),
                edge_id=edge_id,
                source_norm=normalize_name(row.get('source', '')),
                target_norm=normalize_name(row.get('target', ''))
            )
            db_session.add(flow)
            loaded += 1
            existing_edge_ids.add(edge_id)
        
        db_session.commit()
    
    return loaded


def load_foia_targets(db_session, data_dir: Path, append: bool = False) -> int:
    """Load FOIA targets from CSV files"""
    foia_files = list(data_dir.glob('foia/**/*.csv'))
    foia_files.extend(data_dir.glob('foia/*.csv'))
    
    loaded = 0
    existing_requests = set()
    
    if append:
        existing_requests = {
            (f.agency, f.record_request[:100])
            for f in db_session.query(FOIATarget.agency, FOIATarget.record_request).all()
        }
    
    for foia_file in foia_files:
        print(f"  Loading FOIA targets from: {foia_file.name}")
        data = load_csv_data(foia_file)
        
        for row in data:
            agency = row.get('agency', '').strip()
            request = row.get('record_request', '').strip()
            
            if not agency or not request:
                continue
            
            key = (agency, request[:100])
            if append and key in existing_requests:
                continue
            
            # Check for duplicates
            existing = db_session.query(FOIATarget).filter(
                FOIATarget.agency == agency,
                FOIATarget.record_request == request
            ).first()
            
            if existing:
                continue
            
            # Parse quality scores
            specificity = 0.0
            likelihood = 0.0
            priority = 0.0
            
            try:
                specificity = float(row.get('specificity_score', 0))
            except (ValueError, TypeError):
                pass
            try:
                likelihood = float(row.get('likelihood_score', 0))
            except (ValueError, TypeError):
                pass
            try:
                priority = float(row.get('priority_score', 0))
            except (ValueError, TypeError):
                pass
            
            target = FOIATarget(
                agency=agency,
                record_request=request,
                timeframe=row.get('timeframe'),
                relevance=row.get('relevance'),
                notes=row.get('notes'),
                specificity_score=specificity,
                likelihood_score=likelihood,
                priority_score=priority,
                quality_notes=row.get('quality_notes')
            )
            db_session.add(target)
            loaded += 1
            existing_requests.add(key)
        
        db_session.commit()
    
    return loaded


def load_relationships(db_session, data_dir: Path, append: bool = False) -> int:
    """Load relationships from CSV files"""
    rel_files = list(data_dir.glob('entities/**/*relationships*.csv'))
    rel_files.extend(data_dir.glob('relationships/*.csv'))
    
    loaded = 0
    existing_rels = set()
    
    if append:
        existing_rels = {
            (r.source, r.target, r.label)
            for r in db_session.query(Relationship.source, Relationship.target, Relationship.label).all()
        }
    
    for rel_file in rel_files:
        print(f"  Loading relationships from: {rel_file.name}")
        data = load_csv_data(rel_file)
        
        for row in data:
            source = row.get('source', '').strip()
            target = row.get('target', '').strip()
            label = row.get('label', '').strip()
            
            if not source or not target or not label:
                continue
            
            key = (source, target, label)
            if append and key in existing_rels:
                continue
            
            existing = db_session.query(Relationship).filter(
                Relationship.source == source,
                Relationship.target == target,
                Relationship.label == label
            ).first()
            
            if existing:
                continue
            
            rel = Relationship(
                source=source,
                target=target,
                label=label
            )
            db_session.add(rel)
            loaded += 1
            existing_rels.add(key)
        
        db_session.commit()
    
    return loaded


def update_data_version(db_session):
    """Update data version for cache invalidation"""
    version = db_session.query(DataVersion).first()
    
    if version:
        version.version += 1
        version.last_updated = datetime.utcnow()
        version.last_modified_by = 'combine_all_data.py'
    else:
        version = DataVersion(
            version=1,
            last_updated=datetime.utcnow(),
            last_modified_by='combine_all_data.py'
        )
        db_session.add(version)
    
    db_session.commit()
    return version.version


def check_data_integrity(db_session) -> Dict:
    """Check data integrity and return report"""
    issues = []
    
    # Check for entities with missing required fields
    empty_names = db_session.query(Entity).filter(
        (Entity.display_name == '') | (Entity.display_name == None)
    ).count()
    if empty_names:
        issues.append(f"{empty_names} entities with empty display names")
    
    # Check for money flows with unknown targets
    unknown_targets = db_session.query(MoneyFlow).filter(
        MoneyFlow.target == 'Unknown'
    ).count()
    if unknown_targets:
        issues.append(f"{unknown_targets} money flows with unknown targets")
    
    # Check for orphaned relationships (entities not in database)
    relationships = db_session.query(Relationship).all()
    entity_names = {e.display_name for e in db_session.query(Entity).all()}
    orphaned = 0
    for rel in relationships:
        if rel.source not in entity_names or rel.target not in entity_names:
            orphaned += 1
    if orphaned:
        issues.append(f"{orphaned} relationships reference non-existent entities")
    
    # Check for duplicate FOIA targets
    from sqlalchemy import func
    duplicates = db_session.query(
        FOIATarget.agency,
        FOIATarget.record_request,
        func.count(FOIATarget.id).label('count')
    ).group_by(
        FOIATarget.agency,
        FOIATarget.record_request
    ).having(func.count(FOIATarget.id) > 1).all()
    
    if duplicates:
        issues.append(f"{len(duplicates)} duplicate FOIA target entries")
    
    return {
        'status': 'ok' if not issues else 'issues_found',
        'issues': issues,
        'counts': count_records(db_session)
    }


def main():
    """Main data combination function"""
    parser = argparse.ArgumentParser(description='Combine and reload all data sources')
    parser.add_argument('--append', action='store_true', help='Append new data only (skip existing)')
    parser.add_argument('--check', action='store_true', help='Check data integrity only')
    parser.add_argument('--no-update-version', action='store_true', help='Skip version update')
    args = parser.parse_args()
    
    print("=" * 70)
    print("Project RawHorse - Data Combination Tool")
    print("=" * 70)
    
    data_dir = PROJECT_ROOT / "data"
    db_path = PROJECT_ROOT / config['database']['path']
    
    print(f"\nData directory: {data_dir}")
    print(f"Database: {db_path}")
    
    engine = init_database(str(db_path))
    session_maker = get_session_maker(engine)
    db = session_maker()
    
    try:
        # Check data integrity only
        if args.check:
            print("\n[CHECK] Running data integrity check...")
            report = check_data_integrity(db)
            
            print(f"\nData Integrity Report:")
            print(f"  Status: {report['status']}")
            print(f"\nRecord Counts:")
            for table, count in report['counts'].items():
                print(f"  {table}: {count}")
            
            if report['issues']:
                print(f"\nIssues Found:")
                for issue in report['issues']:
                    print(f"  - {issue}")
            else:
                print("\nNo issues found.")
            
            return
        
        # Record initial counts
        print("\nInitial record counts:")
        initial_counts = count_records(db)
        for table, count in initial_counts.items():
            print(f"  {table}: {count}")
        
        mode = "APPEND" if args.append else "FULL LOAD"
        print(f"\nMode: {mode}")
        
        # Load all data
        print("\n[1/5] Loading entities...")
        entities_loaded = load_entities(db, data_dir, args.append)
        print(f"  Loaded {entities_loaded} new entities")
        
        print("\n[2/5] Loading money flows...")
        money_loaded = load_money_flows(db, data_dir, args.append)
        print(f"  Loaded {money_loaded} new money flows")
        
        print("\n[3/5] Loading materials flows...")
        materials_loaded = load_materials_flows(db, data_dir, args.append)
        print(f"  Loaded {materials_loaded} new materials flows")
        
        print("\n[4/5] Loading FOIA targets...")
        foia_loaded = load_foia_targets(db, data_dir, args.append)
        print(f"  Loaded {foia_loaded} new FOIA targets")
        
        print("\n[5/5] Loading relationships...")
        rels_loaded = load_relationships(db, data_dir, args.append)
        print(f"  Loaded {rels_loaded} new relationships")
        
        # Update data version
        if not args.no_update_version:
            new_version = update_data_version(db)
            print(f"\n[VERSION] Data version updated to: {new_version}")
        
        # Final counts
        print("\nFinal record counts:")
        final_counts = count_records(db)
        for table, count in final_counts.items():
            diff = count - initial_counts[table]
            diff_str = f" (+{diff})" if diff > 0 else ""
            print(f"  {table}: {count}{diff_str}")
        
        # Run integrity check
        print("\n[CHECK] Running data integrity check...")
        report = check_data_integrity(db)
        if report['issues']:
            print("Issues found:")
            for issue in report['issues']:
                print(f"  - {issue}")
        else:
            print("No issues found.")
        
        print("\n" + "=" * 70)
        print("Data combination complete!")
        print("=" * 70)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
