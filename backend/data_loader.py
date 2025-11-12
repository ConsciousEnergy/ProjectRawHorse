"""
Load CSV data from UAPUFOResearch directory into SQLite database
"""
import os
import csv
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from database import Entity, MoneyFlow, Award, FOIATarget, Relationship

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_str or date_str.strip() == "":
        return None
    
    # Try multiple date formats
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def parse_float(value_str: Optional[str]) -> Optional[float]:
    """Parse float string to float"""
    if not value_str or value_str.strip() == "":
        return None
    try:
        # Remove commas and convert
        return float(str(value_str).replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def infer_entity_type(name: str) -> str:
    """Infer entity type from name patterns"""
    if not name:
        return "Unknown"
    
    name_lower = name.lower()
    
    # Government entities
    if any(term in name_lower for term in ['government', 'dept', 'department', 'agency', 'administration', 'nga', 'dod', 'nasa', 'darpa']):
        return "Government Agency"
    
    # Investment/Capital firms
    if any(term in name_lower for term in ['capital', 'partners', 'ventures', 'investment', 'equity']):
        return "Investment Firm"
    
    # Research institutions
    if any(term in name_lower for term in ['laboratories', 'research', 'institute', 'university', 'lab']):
        return "Research Institution"
    
    # Corporations (default for business entities)
    if any(term in name_lower for term in ['inc.', 'inc', 'llc', 'corp', 'corporation', 'company', 'technologies', 'systems', 'solutions', 'services', 'group']):
        return "Corporation"
    
    return "Organization"


def load_entities(db: Session, csv_path: str) -> int:
    """Load entities from CSV file"""
    if not os.path.exists(csv_path):
        logger.warning(f"Entities file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Map CSV columns to database fields
                # CSV has 'name' but DB expects 'display_name'
                name = row.get('name', row.get('display_name', ''))
                entity_type = row.get('type', row.get('entity_type'))
                
                # If type is empty, infer from name
                if not entity_type or entity_type.strip() == '':
                    entity_type = infer_entity_type(name)
                
                entity = Entity(
                    entity_id=row.get('entity_id', ''),
                    display_name=name,
                    normalized_name=row.get('normalized_name', name.lower() if name else ''),
                    entity_type=entity_type
                )
                db.add(entity)
                count += 1
            except Exception as e:
                logger.error(f"Error loading entity: {e}")
                continue
    
    db.commit()
    logger.info(f"Loaded {count} entities")
    return count


def load_money_flows(db: Session, csv_path: str) -> int:
    """Load money flows from CSV file"""
    if not os.path.exists(csv_path):
        logger.warning(f"Money flows file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                money_flow = MoneyFlow(
                    source=row.get('source', ''),
                    target=row.get('target', ''),
                    relationship=row.get('relationship'),
                    amount_usd=parse_float(row.get('amount_usd')),
                    start_date=parse_date(row.get('start_date')),
                    end_date=parse_date(row.get('end_date')),
                    source_citation=row.get('source_citation'),
                    edge_id=row.get('edge_id'),
                    source_norm=row.get('source_norm'),
                    target_norm=row.get('target_norm')
                )
                db.add(money_flow)
                count += 1
            except Exception as e:
                logger.error(f"Error loading money flow: {e}")
                continue
    
    db.commit()
    logger.info(f"Loaded {count} money flows")
    return count


def load_awards(db: Session, csv_path: str) -> int:
    """Load awards from CSV file"""
    if not os.path.exists(csv_path):
        logger.warning(f"Awards file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                award = Award(
                    piid=row.get('piid'),
                    recipient_name=row.get('recipient_name'),
                    recipient_uei=row.get('recipient_uei'),
                    recipient_duns=row.get('recipient_duns'),
                    awarding_agency=row.get('awarding_agency'),
                    funding_agency=row.get('funding_agency'),
                    award_amount=parse_float(row.get('award_amount')),
                    action_date=parse_date(row.get('action_date')),
                    description=row.get('description'),
                    naics_code=row.get('naics_code'),
                    psc_code=row.get('psc_code')
                )
                db.add(award)
                count += 1
            except Exception as e:
                logger.error(f"Error loading award: {e}")
                continue
    
    db.commit()
    logger.info(f"Loaded {count} awards")
    return count


def load_foia_targets(db: Session, csv_path: str) -> int:
    """Load FOIA targets from CSV file"""
    if not os.path.exists(csv_path):
        logger.warning(f"FOIA targets file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                foia = FOIATarget(
                    agency=row.get('agency', ''),
                    record_request=row.get('record_request', ''),
                    timeframe=row.get('timeframe'),
                    relevance=row.get('relevance'),
                    notes=row.get('notes')
                )
                db.add(foia)
                count += 1
            except Exception as e:
                logger.error(f"Error loading FOIA target: {e}")
                continue
    
    db.commit()
    logger.info(f"Loaded {count} FOIA targets")
    return count


def load_relationships(db: Session, csv_path: str) -> int:
    """Load relationships from CSV file"""
    if not os.path.exists(csv_path):
        logger.warning(f"Relationships file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                relationship = Relationship(
                    source=row.get('source', ''),
                    target=row.get('target', ''),
                    label=row.get('label', 'RELATED_TO')
                )
                db.add(relationship)
                count += 1
            except Exception as e:
                logger.error(f"Error loading relationship: {e}")
                continue
    
    db.commit()
    logger.info(f"Loaded {count} relationships")
    return count


def load_all_data(db: Session, config: dict, project_root: str = "."):
    """Load all CSV data into database
    
    Args:
        db: Database session
        config: Configuration dictionary
        project_root: Absolute path to project root directory
    """
    logger.info("Loading data from refactored structure")
    
    # Load entities
    entities_path = os.path.join(project_root, config['data_sources']['entities_dir'], "entities_master.csv")
    load_entities(db, entities_path)
    
    # Load money flows
    money_flows_path = os.path.join(project_root, config['data_sources']['financial_dir'], "money_flows.csv")
    load_money_flows(db, money_flows_path)
    
    # Load awards
    awards_path = os.path.join(project_root, config['data_sources']['financial_dir'], "awards_master.csv")
    load_awards(db, awards_path)
    
    # Load FOIA targets
    foia_path = os.path.join(project_root, config['data_sources']['foia_dir'], "foia_targets.csv")
    load_foia_targets(db, foia_path)
    
    # Load relationships
    relationships_path = os.path.join(project_root, config['data_sources']['entities_dir'], "entity_relationships.csv")
    load_relationships(db, relationships_path)
    
    logger.info("Data loading complete")


def is_database_populated(db: Session) -> bool:
    """Check if database already has data"""
    entity_count = db.query(Entity).count()
    return entity_count > 0
