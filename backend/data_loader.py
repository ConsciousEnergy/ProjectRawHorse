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
from database import Entity, MoneyFlow, Award, FOIATarget, Relationship, SearchLog, DataVersion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Government agency acronym expansion map
AGENCY_ACRONYMS = {
    'NGA': 'National Geospatial-Intelligence Agency',
    'DOD': 'Department of Defense',
    'NASA': 'National Aeronautics and Space Administration',
    'DARPA': 'Defense Advanced Research Projects Agency',
    'DIA': 'Defense Intelligence Agency',
    'NSA': 'National Security Agency',
    'CIA': 'Central Intelligence Agency',
    'FBI': 'Federal Bureau of Investigation',
    'DCSA': 'Defense Counterintelligence and Security Agency',
    'TSA': 'Transportation Security Administration',
    'DHS': 'Department of Homeland Security',
    'AARO': 'All-domain Anomaly Resolution Office',
    'NRO': 'National Reconnaissance Office',
    'USSF': 'United States Space Force',
    'USAF': 'United States Air Force',
}


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
    name_stripped = name.strip()
    
    # Check if it's a person's name (typically First Last format, no business terms)
    # Simple heuristic: if it's 2-3 words, no business terms, and looks like a name
    words = name_stripped.split()
    if 2 <= len(words) <= 3:
        # Check if it doesn't contain business/organization terms
        business_terms = ['inc', 'llc', 'corp', 'corporation', 'company', 'ltd', 'limited', 
                         'agency', 'office', 'department', 'dept', 'program', 'project',
                         'laboratory', 'lab', 'institute', 'university', 'college',
                         'foundation', 'organization', 'association', 'society', 'group']
        if not any(term in name_lower for term in business_terms):
            # Check if it looks like a person's name (capitalized words)
            if all(word[0].isupper() if word else False for word in words):
                return "Individual"
    
    # Exact match for government acronyms (to avoid false positives like "Singa Corporation")
    gov_acronyms = ['NGA', 'DOD', 'NASA', 'DARPA', 'DIA', 'NSA', 'CIA', 'FBI', 
                     'DCSA', 'TSA', 'DHS', 'AARO', 'NRO', 'USSF', 'USAF']
    if name_stripped.upper() in gov_acronyms:
        return "Government Agency"
    
    # General government entity patterns (using word boundaries)
    if any(term in name_lower for term in ['government', 'dept', 'department', 'agency', 'administration']):
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
    """Load entities from CSV file with duplicate checking"""
    if not os.path.exists(csv_path):
        logger.warning(f"Entities file not found: {csv_path}")
        return 0
    
    count = 0
    skipped = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Map CSV columns to database fields
                # CSV has 'name' but DB expects 'display_name'
                name = row.get('name', row.get('display_name', ''))
                entity_id = row.get('entity_id', '')
                entity_type = row.get('type', row.get('entity_type'))
                
                if not name:
                    continue
                
                # Check if entity already exists
                existing = None
                if entity_id:
                    existing = db.query(Entity).filter(Entity.entity_id == entity_id).first()
                if not existing:
                    existing = db.query(Entity).filter(Entity.display_name == name).first()
                
                if existing:
                    skipped += 1
                    continue  # Skip duplicates
                
                # If type is empty, infer from name
                if not entity_type or entity_type.strip() == '':
                    entity_type = infer_entity_type(name)
                
                entity = Entity(
                    entity_id=entity_id,
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
    if skipped > 0:
        logger.info(f"Loaded {count} entities, skipped {skipped} duplicates")
    else:
        logger.info(f"Loaded {count} entities")
    return count


def load_money_flows(db: Session, csv_path: str) -> int:
    """Load money flows from CSV file"""
    if not os.path.exists(csv_path):
        logger.warning(f"Money flows file not found: {csv_path}")
        return 0
    
    count = 0
    skipped = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                edge_id = row.get('edge_id')
                
                # Check for duplicates by edge_id
                if edge_id:
                    existing = db.query(MoneyFlow).filter(MoneyFlow.edge_id == edge_id).first()
                    if existing:
                        skipped += 1
                        continue
                
                money_flow = MoneyFlow(
                    source=row.get('source', ''),
                    target=row.get('target', ''),
                    relationship=row.get('relationship'),
                    amount_usd=parse_float(row.get('amount_usd')),
                    start_date=parse_date(row.get('start_date')),
                    end_date=parse_date(row.get('end_date')),
                    source_citation=row.get('source_citation'),
                    edge_id=edge_id,
                    source_norm=row.get('source_norm'),
                    target_norm=row.get('target_norm')
                )
                db.add(money_flow)
                count += 1
            except Exception as e:
                logger.error(f"Error loading money flow: {e}")
                continue
    
    db.commit()
    if skipped > 0:
        logger.info(f"Loaded {count} money flows, skipped {skipped} duplicates")
    else:
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
    """Load FOIA targets from CSV file with duplicate checking"""
    if not os.path.exists(csv_path):
        logger.warning(f"FOIA targets file not found: {csv_path}")
        return 0
    
    count = 0
    skipped = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                agency = row.get('agency', '').strip()
                record_request = row.get('record_request', '').strip()
                
                if not agency or not record_request:
                    continue
                
                # Check if FOIA target already exists (same agency and record_request)
                existing = db.query(FOIATarget).filter(
                    FOIATarget.agency == agency,
                    FOIATarget.record_request == record_request
                ).first()
                
                if existing:
                    skipped += 1
                    continue  # Skip duplicates
                
                foia = FOIATarget(
                    agency=agency,
                    record_request=record_request,
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
    if skipped > 0:
        logger.info(f"Loaded {count} new FOIA targets, skipped {skipped} duplicates")
    else:
        logger.info(f"Loaded {count} FOIA targets")
    return count


def load_nro_seeds_as_entities(db: Session, csv_path: str) -> int:
    """Load unique entities from NRO seeds CSV file
    
    Extracts unique entity names from the NRO seeds file and adds them as entities.
    Also ensures NRO itself exists as an entity.
    """
    if not os.path.exists(csv_path):
        logger.warning(f"NRO seeds file not found: {csv_path}")
        return 0
    
    # First, ensure NRO exists as an entity
    nro_entity = db.query(Entity).filter(Entity.display_name == "NRO").first()
    if not nro_entity:
        nro_entity = Entity(
            entity_id="nro",
            display_name="NRO",
            normalized_name="nro",
            entity_type="Government Agency"
        )
        db.add(nro_entity)
        db.commit()
        logger.info("Added NRO as entity")
    
    # Extract unique entities from seeds file
    entities_seen = set()
    entities_seen.add("NRO")  # Don't duplicate NRO
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entity_name = row.get('entity', '').strip()
                if not entity_name or entity_name in entities_seen:
                    continue
                
                entities_seen.add(entity_name)
                
                # Check if entity already exists
                existing = db.query(Entity).filter(
                    Entity.display_name == entity_name
                ).first()
                
                if existing:
                    continue  # Skip if already exists
                
                # Infer entity type from name
                entity_type = infer_entity_type(entity_name)
                
                # Create normalized name for entity_id
                normalized = entity_name.lower().replace(' ', '_').replace(',', '').replace('.', '').replace('&', 'and')
                entity_id = f"nro_seed_{normalized}"
                
                entity = Entity(
                    entity_id=entity_id,
                    display_name=entity_name,
                    normalized_name=normalized,
                    entity_type=entity_type
                )
                db.add(entity)
                count += 1
            except Exception as e:
                logger.error(f"Error loading NRO seed entity: {e}")
                continue
    
    db.commit()
    logger.info(f"Loaded {count} entities from NRO seeds")
    return count


def load_transcript_entities(db: Session, csv_path: str) -> int:
    """Load entities from UAPGerb transcript CSV file
    
    Loads entities extracted from transcript with deduplication against existing entities.
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Transcript entities file not found: {csv_path}")
        return 0
    
    count = 0
    skipped = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entity_id = row.get('entity_id', '').strip()
                display_name = row.get('display_name', '').strip()
                normalized_name = row.get('normalized_name', '').strip()
                entity_type = row.get('entity_type', '').strip()
                
                if not display_name:
                    continue
                
                # Check if entity already exists by entity_id or display_name
                existing = db.query(Entity).filter(
                    (Entity.entity_id == entity_id) |
                    (Entity.display_name == display_name)
                ).first()
                
                if existing:
                    skipped += 1
                    continue  # Skip duplicates
                
                # Use provided entity_type or infer
                if not entity_type:
                    entity_type = infer_entity_type(display_name)
                
                # Ensure normalized_name exists
                if not normalized_name:
                    normalized_name = display_name.lower().strip()
                
                entity = Entity(
                    entity_id=entity_id,
                    display_name=display_name,
                    normalized_name=normalized_name,
                    entity_type=entity_type
                )
                db.add(entity)
                count += 1
            except Exception as e:
                logger.error(f"Error loading transcript entity: {e}")
                continue
    
    db.commit()
    if skipped > 0:
        logger.info(f"Loaded {count} new entities from transcript, skipped {skipped} duplicates")
    else:
        logger.info(f"Loaded {count} entities from transcript")
    return count


def load_relationships(db: Session, csv_path: str) -> int:
    """Load relationships from CSV file
    
    Supports multiple formats:
    - Standard: source, target, label
    - NRO edges: source, target, relationship (used as label)
    - Transcript: source, target, label, notes (notes field ignored but handled)
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Relationships file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Support both 'label' and 'relationship' field names
                label = row.get('label') or row.get('relationship', 'RELATED_TO')
                source = row.get('source', '').strip()
                target = row.get('target', '').strip()
                
                if not source or not target:
                    continue
                
                relationship = Relationship(
                    source=source,
                    target=target,
                    label=label
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
    
    # Load NRO seeds as entities (extract unique entities from seeds file)
    nro_seeds_path = os.path.join(project_root, config['data_sources']['entities_dir'], "nro_public_partners_seeds_v2.csv")
    if os.path.exists(nro_seeds_path):
        logger.info("Loading NRO seeds as entities")
        load_nro_seeds_as_entities(db, nro_seeds_path)
    
    # Load NRO seed edges (optional - for NRO commercial partner relationships)
    nro_edges_path = os.path.join(project_root, config['data_sources']['visualizations_dir'], "nro_seed_edges_v2.csv")
    if os.path.exists(nro_edges_path):
        logger.info("Loading NRO seed edges as relationships")
        load_relationships(db, nro_edges_path)
    
    # Load UAPGerb transcript entities and relationships
    transcript_entities_path = os.path.join(project_root, config['data_sources']['entities_dir'], "uap_gerb_transcript_entities.csv")
    if os.path.exists(transcript_entities_path):
        logger.info("Loading UAPGerb transcript entities")
        load_transcript_entities(db, transcript_entities_path)
    
    transcript_relationships_path = os.path.join(project_root, config['data_sources']['entities_dir'], "uap_gerb_transcript_relationships.csv")
    if os.path.exists(transcript_relationships_path):
        logger.info("Loading UAPGerb transcript relationships")
        load_relationships(db, transcript_relationships_path)
    
    # Load UAPGerb transcript FOIA targets
    transcript_foia_path = os.path.join(project_root, config['data_sources']['foia_dir'], "uap_gerb_transcript_foia_targets.csv")
    if os.path.exists(transcript_foia_path):
        logger.info("Loading UAPGerb transcript FOIA targets")
        load_foia_targets(db, transcript_foia_path)
    
    # Increment data version after loading
    increment_data_version(db, "data_loader")
    
    logger.info("Data loading complete")


def increment_data_version(db: Session, modified_by: str = "system") -> int:
    """Increment data version to signal data changes"""
    from datetime import datetime
    
    version_record = db.query(DataVersion).order_by(DataVersion.id.desc()).first()
    
    if version_record:
        version_record.version += 1
        version_record.last_updated = datetime.utcnow()
        version_record.last_modified_by = modified_by
    else:
        version_record = DataVersion(version=1, last_modified_by=modified_by)
        db.add(version_record)
    
    db.commit()
    db.refresh(version_record)
    
    logger.info(f"Data version incremented to {version_record.version}")
    return version_record.version


def get_current_version(db: Session) -> int:
    """Get current data version"""
    version_record = db.query(DataVersion).order_by(DataVersion.id.desc()).first()
    
    if not version_record:
        # Initialize if doesn't exist
        version_record = DataVersion(version=1)
        db.add(version_record)
        db.commit()
        db.refresh(version_record)
    
    return version_record.version


def is_database_populated(db: Session) -> bool:
    """Check if database already has data"""
    entity_count = db.query(Entity).count()
    return entity_count > 0
