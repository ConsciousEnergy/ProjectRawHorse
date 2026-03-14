"""
Load CSV data into the Project RawHorse SQLite/PostgreSQL database.

Structure:
- Entity loaders: load_entities, load_entity_type_overrides, load_nro_seeds_as_entities,
  load_transcript_entities, load_intel_stack_levels (applies level after entities exist).
- Financial loaders: load_money_flows, load_awards, load_awards_usaspending,
  load_money_flows_veritas_peraton, load_federal_flows_by_recipient,
  load_advisors_fees_as_money_flows, load_solicitations_as_awards, load_materials_flows.
- Relationship loaders: load_relationships (supports enriched fields: description,
  relationship_type, source_citation, start_date, end_date).
- FOIA: load_foia_targets.

Entry point: load_all_data(db, config, project_root). Load order: overrides → entities →
money flows → awards → FOIA → relationships → NRO seeds/edges → transcript/Hidden Wing →
additional financial CSVs → materials flows → researched contracts → intel_stack_levels.
All paths are under config['data_sources'] (entities_dir, financial_dir, etc.).
"""
import os
import csv
import logging
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
from sqlalchemy.orm import Session
from database import Entity, MoneyFlow, Award, FOIATarget, Relationship, SearchLog, DataVersion, MaterialsFlow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Valid entity types for validation
VALID_ENTITY_TYPES = [
    'Corporation', 'Government Agency', 'Individual', 
    'Research Institution', 'Facility', 'Program',
    'Investment Firm', 'Organization', 'Unknown'
]

# Entity type overrides - loaded from CSV file
# Key: display_name, Value: entity_type
ENTITY_TYPE_OVERRIDES: Dict[str, str] = {}


def load_entity_type_overrides(csv_path: str = None) -> int:
    """Load explicit entity type assignments from CSV file.
    
    The CSV should have columns: display_name, entity_type, source, notes
    Lines starting with # are treated as comments.
    
    Returns:
        Number of overrides loaded
    """
    global ENTITY_TYPE_OVERRIDES
    
    if csv_path is None:
        # Default path relative to backend directory
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'entity_type_overrides.csv')
    
    if not os.path.exists(csv_path):
        logger.warning(f"Entity type overrides file not found: {csv_path}")
        return 0
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                display_name = row.get('display_name')
                entity_type = row.get('entity_type')
                
                # Skip rows with missing fields
                if display_name is None or entity_type is None:
                    continue
                
                display_name = display_name.strip()
                entity_type = entity_type.strip()
                
                # Skip comments and empty rows
                if not display_name or display_name.startswith('#'):
                    continue
                
                if not entity_type:
                    continue
                
                # Validate entity type
                if entity_type not in VALID_ENTITY_TYPES:
                    logger.warning(f"Invalid entity type '{entity_type}' for {display_name}")
                    continue
                
                ENTITY_TYPE_OVERRIDES[display_name] = entity_type
                count += 1
            except Exception as e:
                logger.error(f"Error loading override: {e}")
                continue
    
    logger.info(f"Loaded {count} entity type overrides")
    return count


def get_entity_type(name: str) -> str:
    """Get entity type - check overrides first, then infer from name.
    
    Args:
        name: Entity display name
        
    Returns:
        Entity type string
    """
    if not name:
        return "Unknown"
    
    # Check overrides first
    name_stripped = name.strip()
    if name_stripped in ENTITY_TYPE_OVERRIDES:
        return ENTITY_TYPE_OVERRIDES[name_stripped]
    
    # Fall back to inference
    return infer_entity_type(name)


def validate_entity_type(entity_type: str, entity_name: str) -> str:
    """Validate and normalize entity type.
    
    If the entity type is invalid, falls back to inference.
    
    Args:
        entity_type: The entity type to validate
        entity_name: Entity name (for logging and fallback inference)
        
    Returns:
        Valid entity type string
    """
    if not entity_type or entity_type not in VALID_ENTITY_TYPES:
        if entity_type:
            logger.warning(f"Unknown entity type '{entity_type}' for {entity_name}, inferring...")
        return get_entity_type(entity_name)
    return entity_type


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
    
    # Exact match for government acronyms (check first to avoid misclassification)
    gov_acronyms = ['NGA', 'DOD', 'NASA', 'DARPA', 'DIA', 'NSA', 'CIA', 'FBI', 
                     'DCSA', 'TSA', 'DHS', 'AARO', 'NRO', 'USSF', 'USAF', 'DOE',
                     'AFRL', 'AFMC', 'OSD', 'SAF-AQ', 'ONR', 'ODNI', 'OUSD']
    if name_stripped.upper() in gov_acronyms:
        return "Government Agency"
    
    # General government entity patterns
    if any(term in name_lower for term in ['government', 'dept', 'department', 'agency', 'administration',
                                            'air force', 'army', 'navy', 'pentagon', 'secretary',
                                            'command', 'directorate']):
        return "Government Agency"
    
    # Facilities - check BEFORE research institutions to catch Y12 Complex, etc.
    facility_terms = [
        'base', 'afb', 'facility', 'range', 'site', 'complex', 'plant',
        'area 51', 'groom lake', 'tonopah', 'dugway', 'edwards', 'nellis',
        'white sands', 'test range', 'proving ground', 'y12', 'y-12'
    ]
    if any(term in name_lower for term in facility_terms):
        return "Facility"
    
    # Known space/tech companies (explicit list for common misclassifications)
    # These are commercial companies that might have "lab" or other confusing terms
    known_corporations = [
        'planet labs', 'planet', 'umbra', 'blacksky', 'maxar', 'digitalglobe',
        'capella', 'iceye', 'hawkeye', 'spire', 'kleos', 'turion',
        'rocket lab', 'relativity', 'astra', 'firefly', 'virgin orbit',
        'spacex', 'blue origin', 'sierra nevada', 'axiom', 'voyager',
        'redwire', 'terran orbital', 'ast spacemobile', 'momentus'
    ]
    if any(corp in name_lower for corp in known_corporations):
        return "Corporation"
    
    # Investment/Capital firms (check before corporations)
    if any(term in name_lower for term in ['capital', 'partners', 'ventures', 'investment', 'equity', 'fund']):
        return "Investment Firm"
    
    # Research institutions - be more specific to avoid catching commercial "labs"
    research_terms = [
        'national laboratory', 'national laboratories', 'research institute',
        'university', 'college', 'sandia national', 'los alamos national',
        'oak ridge national', 'lawrence livermore', 'argonne national',
        'brookhaven national', 'pacific northwest national', 'idaho national',
        'battelle memorial', 'mitre corporation', 'jason advisory',
        'rand corporation', 'aerospace corporation', 'ida ', 'ffrdc'
    ]
    if any(term in name_lower for term in research_terms):
        return "Research Institution"
    
    # Corporations - expanded list to catch space/tech companies
    corporation_terms = [
        # Explicit business suffixes
        'inc.', 'inc', 'llc', 'corp', 'corporation', 'company', 'ltd', 'limited', 'co.',
        # Tech/Industry terms that indicate a company
        'technologies', 'systems', 'solutions', 'services', 'group', 'dynamics',
        'aerospace', 'defense', 'industries', 'international', 'global', 'holdings',
        # Space industry specific
        'space', 'satellite', 'orbital', 'launch', 'rocket',
        # Defense contractors
        'lockheed', 'northrop', 'raytheon', 'boeing', 'grumman', 'general dynamics',
        'bae', 'leidos', 'saic', 'peraton', 'booz allen', 'parsons', 'l3harris',
        # Other industry terms
        'analytics', 'insight', 'imaging', 'sensing', 'geospatial', 'intelligence',
        # Commercial "lab" companies (space imagery, etc.)
        'labs'
    ]
    if any(term in name_lower for term in corporation_terms):
        return "Corporation"
    
    # Programs
    if any(term in name_lower for term in ['program', 'project', 'initiative', 'operation']):
        return "Program"
    
    # Check if it's a person's name (typically First Last format, no business terms)
    # This check comes AFTER all the business checks to avoid false positives
    words = name_stripped.split()
    if 2 <= len(words) <= 3:
        # Extended list of terms that indicate it's NOT a person
        not_person_terms = [
            'inc', 'llc', 'corp', 'corporation', 'company', 'ltd', 'limited',
            'agency', 'office', 'department', 'dept', 'program', 'project',
            'laboratory', 'lab', 'labs', 'institute', 'university', 'college',
            'foundation', 'organization', 'association', 'society', 'group',
            'space', 'aerospace', 'systems', 'technologies', 'solutions',
            'defense', 'security', 'intelligence', 'analytics', 'satellite',
            'command', 'wing', 'force', 'base', 'center', 'facility', 'complex'
        ]
        if not any(term in name_lower for term in not_person_terms):
            # Check if all words are capitalized (names typically are)
            if all(word[0].isupper() if word else False for word in words):
                # Check it's not a known company pattern (single word + Space/Tech/etc)
                if len(words) == 2 and words[1].lower() in ['space', 'tech', 'labs', 'ai', 'systems', 'lab']:
                    return "Corporation"
                return "Individual"
    
    # Single word entities - likely companies or organizations, not individuals
    if len(words) == 1:
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
                if not name.strip():
                    logger.warning(f"Entity row with empty display_name skipped in {csv_path}")
                    continue
                if not entity_id or not str(entity_id).strip():
                    logger.debug(f"Entity '{name}' has no entity_id; consider adding one for traceability")
                
                # Check if entity already exists
                existing = None
                if entity_id:
                    existing = db.query(Entity).filter(Entity.entity_id == entity_id).first()
                if not existing:
                    existing = db.query(Entity).filter(Entity.display_name == name).first()
                
                if existing:
                    skipped += 1
                    continue  # Skip duplicates
                
                # If type is empty, get from overrides or infer from name
                if not entity_type or entity_type.strip() == '':
                    entity_type = get_entity_type(name)
                else:
                    # Validate the provided type
                    entity_type = validate_entity_type(entity_type, name)
                
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
                source = (row.get('source') or '').strip()
                target = (row.get('target') or '').strip()
                if not source or not target:
                    logger.warning(f"Money flow skipped: missing source or target (source={source!r}, target={target!r}) in {csv_path}")
                    continue
                
                # Check for duplicates by edge_id
                if edge_id:
                    existing = db.query(MoneyFlow).filter(MoneyFlow.edge_id == edge_id).first()
                    if existing:
                        skipped += 1
                        continue
                
                money_flow = MoneyFlow(
                    source=source,
                    target=target,
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
    
    If the CSV has an 'entity_type' column, that value is used (with validation).
    Otherwise, the type is determined from overrides or inference.
    """
    if not os.path.exists(csv_path):
        logger.warning(f"NRO seeds file not found: {csv_path}")
        return 0
    
    # Load entity type overrides if not already loaded
    if not ENTITY_TYPE_OVERRIDES:
        load_entity_type_overrides()
    
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
    updated = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entity_name = row.get('entity', '').strip()
                if not entity_name or entity_name in entities_seen:
                    continue
                
                entities_seen.add(entity_name)
                
                # Determine entity type:
                # 1. Use entity_type from CSV if present
                # 2. Otherwise check overrides
                # 3. Otherwise infer from name
                csv_type = row.get('entity_type', '').strip()
                if csv_type and csv_type in VALID_ENTITY_TYPES:
                    entity_type = csv_type
                else:
                    entity_type = get_entity_type(entity_name)
                
                # Check if entity already exists
                existing = db.query(Entity).filter(
                    Entity.display_name == entity_name
                ).first()
                
                if existing:
                    # Update type if it's different and we have a better one
                    if existing.entity_type != entity_type:
                        logger.info(f"Updating {entity_name}: {existing.entity_type} -> {entity_type}")
                        existing.entity_type = entity_type
                        updated += 1
                    continue
                
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
    logger.info(f"Loaded {count} new entities from NRO seeds, updated {updated} existing")
    return count + updated


def load_transcript_entities(db: Session, csv_path: str) -> int:
    """Load entities from UAPGerb transcript CSV file
    
    Loads entities extracted from transcript with deduplication against existing entities.
    Supports intel_stack_level field for intelligence hierarchy categorization.
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
                
                # Parse intel_stack_level if present
                intel_stack_level_str = row.get('intel_stack_level', '').strip()
                intel_stack_level = None
                if intel_stack_level_str and intel_stack_level_str.isdigit():
                    intel_stack_level = int(intel_stack_level_str)
                
                if not display_name:
                    continue
                
                # Check if entity already exists by entity_id or display_name
                existing = db.query(Entity).filter(
                    (Entity.entity_id == entity_id) |
                    (Entity.display_name == display_name)
                ).first()
                
                if existing:
                    # Update intel_stack_level if not set and we have a value
                    if intel_stack_level is not None and existing.intel_stack_level is None:
                        existing.intel_stack_level = intel_stack_level
                    skipped += 1
                    continue  # Skip duplicates
                
                # Use provided entity_type (with validation) or get from overrides/inference
                if not entity_type:
                    entity_type = get_entity_type(display_name)
                else:
                    entity_type = validate_entity_type(entity_type, display_name)
                
                # Ensure normalized_name exists
                if not normalized_name:
                    normalized_name = display_name.lower().strip()
                
                entity = Entity(
                    entity_id=entity_id,
                    display_name=display_name,
                    normalized_name=normalized_name,
                    entity_type=entity_type,
                    intel_stack_level=intel_stack_level
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


def _parse_parties_to_source_target(parties: str) -> tuple:
    """Parse 'Source ➜ Target' or 'Source -> Target' style string. Returns (source, target) or (None, None)."""
    if not parties or not parties.strip():
        return None, None
    for sep in (" ➜ ", " -> ", " → "):
        if sep in parties:
            parts = parties.split(sep, 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
    return parties.strip(), None


def load_awards_usaspending(db: Session, csv_path: str) -> int:
    """Load awards from USAspending-style CSV (recipient, uei, agency, notes, award_or_idv_url)."""
    if not os.path.exists(csv_path):
        logger.warning(f"Awards USAspending file not found: {csv_path}")
        return 0
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                recipient = (row.get("recipient") or "").strip()
                agency = (row.get("agency") or "").strip()
                if not recipient:
                    continue
                url = (row.get("award_or_idv_url") or "").strip()
                piid = None
                if url and "award/" in url:
                    piid = url.split("award/")[-1].split("_")[0] if "award/" in url else None
                award = Award(
                    piid=piid or row.get("idv_or_award"),
                    recipient_name=recipient,
                    recipient_uei=row.get("uei"),
                    recipient_duns=row.get("duns"),
                    awarding_agency=agency,
                    funding_agency=agency,
                    award_amount=None,
                    action_date=None,
                    description=row.get("notes"),
                )
                db.add(award)
                count += 1
            except Exception as e:
                logger.error(f"Error loading USAspending award: {e}")
                continue
    db.commit()
    logger.info(f"Loaded {count} awards from USAspending")
    return count


def load_money_flows_veritas_peraton(db: Session, csv_path: str) -> int:
    """Load money flows from Veritas/Peraton CSV (parties, amount_usd, date)."""
    if not os.path.exists(csv_path):
        logger.warning(f"Money flows Veritas/Peraton file not found: {csv_path}")
        return 0
    count = 0
    skipped = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                parties = row.get("parties", "")
                source, target = _parse_parties_to_source_target(parties)
                if not source:
                    continue
                if not target:
                    target = "Unknown"
                amount = parse_float(row.get("amount_usd"))
                date_val = parse_date(row.get("date"))
                edge_id = f"veritas_{source[:20]}_{target[:20]}_{row.get('date', '')}".replace(" ", "_")
                existing = db.query(MoneyFlow).filter(MoneyFlow.edge_id == edge_id).first()
                if existing:
                    skipped += 1
                    continue
                money_flow = MoneyFlow(
                    source=source,
                    target=target,
                    relationship=row.get("type") or "M&A",
                    amount_usd=amount,
                    start_date=date_val,
                    end_date=None,
                    source_citation=row.get("source"),
                    edge_id=edge_id,
                )
                db.add(money_flow)
                count += 1
            except Exception as e:
                logger.error(f"Error loading Veritas/Peraton money flow: {e}")
                continue
    db.commit()
    logger.info(f"Loaded {count} money flows from Veritas/Peraton, skipped {skipped} duplicates")
    return count


def load_federal_flows_by_recipient(db: Session, csv_path: str) -> int:
    """Load federal flows by recipient CSV (agency, recipient, total_current_usd) as MoneyFlow."""
    if not os.path.exists(csv_path):
        logger.warning(f"Federal flows by recipient file not found: {csv_path}")
        return 0
    count = 0
    skipped = 0
    seen_key: set[tuple[str, str, str]] = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            try:
                agency = (row.get("agency") or "").strip()
                recipient = (row.get("recipient") or "").strip()
                if not agency or not recipient:
                    continue
                amount = parse_float(row.get("total_current_usd"))
                fy = (row.get("fiscal_year") or "").strip()
                dedupe_key = (agency, recipient, fy)
                if dedupe_key in seen_key:
                    skipped += 1
                    continue
                seen_key.add(dedupe_key)
                edge_id = f"ffr_{idx}_{agency[:20]}_{recipient[:20]}_{fy}".replace(" ", "_").replace("/", "_")
                if len(edge_id) > 255:
                    edge_id = f"ffr_{idx}"
                money_flow = MoneyFlow(
                    source=agency,
                    target=recipient,
                    relationship="Federal Award",
                    amount_usd=amount,
                    start_date=None,
                    end_date=None,
                    source_citation="federal_flows_by_recipient",
                    edge_id=edge_id,
                )
                db.add(money_flow)
                count += 1
            except Exception as e:
                logger.error(f"Error loading federal flow: {e}")
                continue
    db.commit()
    logger.info(f"Loaded {count} federal flows by recipient, skipped {skipped} duplicates")
    return count


def load_advisors_fees_as_money_flows(db: Session, csv_path: str) -> int:
    """Load advisors_fees CSV (buyer->source, seller->target, reported_fees_usd->amount) as MoneyFlow."""
    if not os.path.exists(csv_path):
        logger.warning(f"Advisors fees file not found: {csv_path}")
        return 0
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return 0
    first = rows[0]
    if "buyer" not in first or "seller" not in first:
        logger.warning("Advisors fees CSV missing buyer/seller columns, skipping")
        return 0
    for row in rows:
        try:
            source = (row.get("buyer") or "").strip()
            target = (row.get("seller") or "").strip()
            if not source or not target:
                continue
            amount = parse_float(row.get("reported_fees_usd") or row.get("amount_usd"))
            edge_id = f"adv_{source[:15]}_{target[:15]}".replace(" ", "_")
            existing = db.query(MoneyFlow).filter(MoneyFlow.edge_id == edge_id).first()
            if existing:
                continue
            money_flow = MoneyFlow(
                source=source,
                target=target,
                relationship="Advisor Fees",
                amount_usd=amount,
                start_date=None,
                end_date=None,
                source_citation=row.get("source_citation"),
                edge_id=edge_id,
            )
            db.add(money_flow)
            count += 1
        except Exception as e:
            logger.error(f"Error loading advisor fee: {e}")
            continue
    db.commit()
    logger.info(f"Loaded {count} advisor fee money flows")
    return count


def load_solicitations_as_awards(db: Session, csv_path: str) -> int:
    """Load solicitations CSV (notice_id->piid, agency, title->description) as Award records."""
    if not os.path.exists(csv_path):
        logger.warning(f"Solicitations file not found: {csv_path}")
        return 0
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                notice_id = (row.get("notice_id") or "").strip()
                title = (row.get("title") or "").strip()
                agency = (row.get("agency") or "").strip()
                if not title and not notice_id:
                    continue
                award = Award(
                    piid=notice_id or None,
                    recipient_name=None,
                    awarding_agency=agency,
                    funding_agency=agency,
                    award_amount=None,
                    action_date=parse_date(row.get("posted_date")),
                    description=title,
                    naics_code=row.get("naics"),
                )
                db.add(award)
                count += 1
            except Exception as e:
                logger.error(f"Error loading solicitation: {e}")
                continue
    db.commit()
    logger.info(f"Loaded {count} solicitations as awards")
    return count


def load_intel_stack_levels(db: Session, csv_path: str) -> int:
    """Apply intel_stack_level to entities from CSV (display_name or entity_id, intel_stack_level)."""
    if not os.path.exists(csv_path):
        logger.warning(f"Intel stack levels file not found: {csv_path}")
        return 0
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = (row.get("display_name") or row.get("name") or row.get("entity_id") or "").strip()
                level_str = (row.get("intel_stack_level") or "").strip()
                if not name or name.startswith("#"):
                    continue
                if not level_str or not level_str.isdigit():
                    continue
                level = int(level_str)
                if level < 1 or level > 6:
                    continue
                entity = db.query(Entity).filter(
                    (Entity.display_name == name) | (Entity.entity_id == name)
                ).first()
                if entity:
                    entity.intel_stack_level = level
                    count += 1
            except Exception as e:
                logger.error(f"Error applying intel stack level: {e}")
                continue
    db.commit()
    logger.info(f"Applied intel_stack_level to {count} entities")
    return count


def load_materials_flows(db: Session, csv_path: str) -> int:
    """Load materials/technology flows from CSV. Deduplicate by edge_id."""
    if not os.path.exists(csv_path):
        logger.warning(f"Materials flows file not found: {csv_path}")
        return 0
    count = 0
    skipped = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                source = (row.get("source") or "").strip()
                target = (row.get("target") or "").strip()
                if not source or not target:
                    continue
                edge_id = (row.get("edge_id") or "").strip()
                if not edge_id:
                    edge_id = f"mf_{source[:20]}_{target[:20]}_{row.get('material_type', '')}".replace(" ", "_")
                existing = db.query(MaterialsFlow).filter(MaterialsFlow.edge_id == edge_id).first()
                if existing:
                    skipped += 1
                    continue
                mf = MaterialsFlow(
                    source=source,
                    target=target,
                    material_type=(row.get("material_type") or "").strip() or None,
                    relationship=(row.get("relationship") or "").strip() or None,
                    description=(row.get("description") or "").strip() or None,
                    start_date=parse_date(row.get("start_date")),
                    end_date=parse_date(row.get("end_date")),
                    source_citation=(row.get("source_citation") or "").strip() or None,
                    edge_id=edge_id,
                    source_norm=row.get("source_norm"),
                    target_norm=row.get("target_norm"),
                )
                db.add(mf)
                count += 1
            except Exception as e:
                logger.error(f"Error loading materials flow: {e}")
                continue
    db.commit()
    logger.info(f"Loaded {count} materials flows, skipped {skipped} duplicates")
    return count


def load_relationships(db: Session, csv_path: str) -> int:
    """Load relationships from CSV file.

    Supports:
    - Standard: source, target, label
    - NRO edges: source, target, relationship (used as label)
    - Enriched: relationship_type, description, source_citation, start_date, end_date (e.g. hidden_wing_2026_relationships)
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Relationships file not found: {csv_path}")
        return 0

    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                label = row.get("label") or row.get("relationship", "RELATED_TO")
                source = (row.get("source") or "").strip()
                target = (row.get("target") or "").strip()
                if not source or not target:
                    continue
                if source.startswith("#"):
                    continue
                description = row.get("description") or None
                if description:
                    description = description.strip() or None
                relationship_type = (row.get("relationship_type") or "").strip() or None
                source_citation = row.get("source_citation") or None
                if source_citation:
                    source_citation = source_citation.strip() or None
                start_date = parse_date(row.get("start_date"))
                end_date = parse_date(row.get("end_date"))
                relationship = Relationship(
                    source=source,
                    target=target,
                    label=label,
                    description=description,
                    relationship_type=relationship_type,
                    source_citation=source_citation,
                    start_date=start_date,
                    end_date=end_date,
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
    """Load all CSV data into database.

    Load order: entity overrides → core entities → money flows → awards → FOIA →
    relationships → NRO seeds/edges → transcript and Hidden Wing entities/relationships/FOIA →
    additional financial CSVs (USAspending, Veritas/Peraton, federal flows, advisors, solicitations) →
    materials flows → researched FFRDC/prime contracts → intel_stack_levels backfill.

    Args:
        db: Database session.
        config: Configuration dict with 'data_sources' (entities_dir, financial_dir, foia_dir, etc.).
        project_root: Absolute path to project root (used to resolve CSV paths).
    """
    logger.info("Loading data from refactored structure")
    
    # Load entity type overrides first (used by all entity loading functions)
    overrides_path = os.path.join(project_root, config['data_sources']['entities_dir'], "entity_type_overrides.csv")
    if os.path.exists(overrides_path):
        load_entity_type_overrides(overrides_path)
    else:
        # Try default path
        load_entity_type_overrides()
    
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
    hierarchy_rels_path = os.path.join(project_root, config['data_sources']['entities_dir'], "hierarchy_relationships.csv")
    if os.path.exists(hierarchy_rels_path):
        load_relationships(db, hierarchy_rels_path)
    
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
    
    # Load Hidden Wing transcript entities (US Air Force UFO Programs - 2026)
    hidden_wing_entities_path = os.path.join(project_root, config['data_sources']['entities_dir'], "hidden_wing_entities.csv")
    if os.path.exists(hidden_wing_entities_path):
        logger.info("Loading Hidden Wing transcript entities (Air Force SAF hierarchy)")
        load_transcript_entities(db, hidden_wing_entities_path)
    
    # Load Hidden Wing transcript relationships
    hidden_wing_relationships_path = os.path.join(project_root, config['data_sources']['entities_dir'], "hidden_wing_relationships.csv")
    if os.path.exists(hidden_wing_relationships_path):
        logger.info("Loading Hidden Wing transcript relationships")
        load_relationships(db, hidden_wing_relationships_path)
    
    # Load Hidden Wing 2026 expanded entities (additional entities from full transcript analysis)
    hidden_wing_2026_entities_path = os.path.join(project_root, config['data_sources']['entities_dir'], "hidden_wing_2026_entities.csv")
    if os.path.exists(hidden_wing_2026_entities_path):
        logger.info("Loading Hidden Wing 2026 expanded entities (individuals, offices, programs)")
        load_transcript_entities(db, hidden_wing_2026_entities_path)
    
    # Load Hidden Wing 2026 expanded relationships
    hidden_wing_2026_relationships_path = os.path.join(project_root, config['data_sources']['entities_dir'], "hidden_wing_2026_relationships.csv")
    if os.path.exists(hidden_wing_2026_relationships_path):
        logger.info("Loading Hidden Wing 2026 expanded relationships")
        load_relationships(db, hidden_wing_2026_relationships_path)
    
    # Load Hidden Wing FOIA targets
    hidden_wing_foia_path = os.path.join(project_root, config['data_sources']['foia_dir'], "hidden_wing_foia_targets.csv")
    if os.path.exists(hidden_wing_foia_path):
        logger.info("Loading Hidden Wing FOIA targets")
        load_foia_targets(db, hidden_wing_foia_path)
    
    # Load 2026 researched money flows (federal contracts)
    money_flows_2026_path = os.path.join(project_root, config['data_sources']['financial_dir'], "money_flows_2026_research.csv")
    if os.path.exists(money_flows_2026_path):
        logger.info("Loading 2026 researched federal contract money flows")
        load_money_flows(db, money_flows_2026_path)

    # Ingest additional financial CSVs
    awards_usaspending_path = os.path.join(project_root, config['data_sources']['financial_dir'], "awards_usaspending.csv")
    if os.path.exists(awards_usaspending_path):
        load_awards_usaspending(db, awards_usaspending_path)
    money_flows_veritas_path = os.path.join(project_root, config['data_sources']['financial_dir'], "money_flows_veritas_peraton.csv")
    if os.path.exists(money_flows_veritas_path):
        load_money_flows_veritas_peraton(db, money_flows_veritas_path)
    federal_flows_path = os.path.join(project_root, config['data_sources']['financial_dir'], "federal_flows_by_recipient.csv")
    if os.path.exists(federal_flows_path):
        load_federal_flows_by_recipient(db, federal_flows_path)
    advisors_fees_path = os.path.join(project_root, config['data_sources']['financial_dir'], "advisors_fees.csv")
    if os.path.exists(advisors_fees_path):
        load_advisors_fees_as_money_flows(db, advisors_fees_path)
    solicitations_path = os.path.join(project_root, config['data_sources']['financial_dir'], "solicitations.csv")
    if os.path.exists(solicitations_path):
        load_solicitations_as_awards(db, solicitations_path)

    # Materials flows (technology transfers, FFRDC flows, etc.)
    materials_flows_path = os.path.join(project_root, config['data_sources']['financial_dir'], "materials_flows.csv")
    if os.path.exists(materials_flows_path):
        load_materials_flows(db, materials_flows_path)

    # Researched FFRDC/prime contracts (SAIC, Aerospace Corp, RAND, IDA, Battelle, Sandia, etc.)
    researched_path = os.path.join(project_root, config['data_sources']['financial_dir'], "researched_contracts_ffrdc_primes.csv")
    if os.path.exists(researched_path):
        logger.info("Loading researched FFRDC/prime contract money flows")
        load_money_flows(db, researched_path)

    # Backfill intel_stack_level from CSV (after all entities loaded)
    intel_levels_path = os.path.join(project_root, config['data_sources']['entities_dir'], "intel_stack_levels.csv")
    if os.path.exists(intel_levels_path):
        load_intel_stack_levels(db, intel_levels_path)

    # Timeline events (historical UAP events with citations)
    timeline_events_path = os.path.join(project_root, "data", "timeline", "events.csv")
    timeline_sources_path = os.path.join(project_root, "data", "timeline", "sources.csv")
    if os.path.exists(timeline_events_path):
        load_timeline_events(db, timeline_events_path, timeline_sources_path)

    # Increment data version after loading
    increment_data_version(db, "data_loader")
    
    logger.info("Data loading complete")


def load_timeline_events(db: Session, events_path: str, sources_path: str = None):
    """Load historical timeline events and their citation sources from CSV."""
    from database import TimelineEvent, TimelineSource

    if not os.path.exists(events_path):
        logger.warning(f"Timeline events file not found: {events_path}")
        return

    existing = {e.event_id for e in db.query(TimelineEvent.event_id).all()}
    loaded = 0

    with open(events_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eid = (row.get("event_id") or "").strip()
            if not eid or eid.startswith("#") or eid in existing:
                continue
            date_str = (row.get("event_date") or "").strip()
            if not date_str:
                continue
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Bad date for {eid}: {date_str}")
                continue

            event = TimelineEvent(
                event_id=eid,
                event_date=event_date,
                date_precision=(row.get("date_precision") or "exact").strip(),
                title=(row.get("title") or "").strip(),
                summary=(row.get("summary") or "").strip(),
                category=(row.get("category") or "").strip() or None,
                region=(row.get("region") or "").strip() or None,
                confidence_tier=(row.get("confidence_tier") or "contested").strip(),
                related_entities=(row.get("related_entities") or "").strip() or None,
            )
            db.add(event)
            existing.add(eid)
            loaded += 1

    db.commit()
    logger.info(f"Loaded {loaded} timeline events")

    if sources_path and os.path.exists(sources_path):
        existing_sources = db.query(TimelineSource).count()
        src_loaded = 0
        with open(sources_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                eid = (row.get("event_id") or "").strip()
                if not eid or eid not in existing:
                    continue
                src_date = None
                ds = (row.get("source_date") or "").strip()
                if ds:
                    try:
                        src_date = datetime.strptime(ds, "%Y-%m-%d").date()
                    except ValueError:
                        pass
                source = TimelineSource(
                    event_id=eid,
                    source_type=(row.get("source_type") or "").strip() or None,
                    source_title=(row.get("source_title") or "").strip() or None,
                    source_url=(row.get("source_url") or "").strip() or None,
                    source_date=src_date,
                    notes=(row.get("notes") or "").strip() or None,
                )
                db.add(source)
                src_loaded += 1
        db.commit()
        logger.info(f"Loaded {src_loaded} timeline sources")


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
