#!/usr/bin/env python3
"""
Extract materials and technology transfer flows from web searches
Phase 7 of the Enrichment Improvement Plan
"""
import os
import sys
import csv
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, MaterialsFlow
import yaml

# Import extraction modules
from entity_recognition import extract_target_entity
from date_extraction import extract_date
from validate_flows import calculate_specificity_score, get_source_credibility_score
from compliance_filter import compliance_check, validate_record_for_storage

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "materials"
CACHE_DIR = PROJECT_ROOT / "data" / "scripts" / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Load configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Web search configuration
SEARCH_DELAY = 2  # Seconds between searches
MAX_RESULTS_PER_ENTITY = 5

# Materials transfer keywords organized by type
MATERIALS_KEYWORDS = {
    'technology_transfer': [
        'technology transfer', 'tech transfer', 'T2', 
        'technology sharing', 'technology license', 'tech license'
    ],
    'material_supply': [
        'material transfer', 'supply agreement', 'supply contract',
        'materials supply', 'raw materials', 'component supply'
    ],
    'equipment': [
        'equipment transfer', 'equipment procurement', 'equipment lease',
        'hardware transfer', 'machinery', 'equipment contract'
    ],
    'ip_licensing': [
        'patent license', 'intellectual property', 'IP license', 'IP transfer',
        'patent assignment', 'technology licensing', 'proprietary'
    ],
    'prototype': [
        'prototype', 'prototype development', 'proof of concept',
        'demonstration', 'test article', 'engineering model'
    ],
    'subcontract': [
        'subcontract', 'subcontractor', 'sub-contractor',
        'teaming agreement', 'subcontracting'
    ],
    'software': [
        'software license', 'software transfer', 'source code',
        'software agreement', 'software development', 'software contract'
    ]
}


def generate_edge_id(source: str, target: str, material_type: str, relationship: str) -> str:
    """Generate unique edge ID for materials flow"""
    key = f"MAT|{source}|{target}|{material_type}|{relationship}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def normalize_name(name: str) -> str:
    """Normalize entity name for matching"""
    return name.strip().upper().replace('"', '').replace("'", "")


def search_web(query: str, max_results: int = 5) -> List[Dict]:
    """Perform web search using duckduckgo-search library"""
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            search_results = ddgs.text(
                keywords=query,
                max_results=max_results,
                region='us-en',
                safesearch='moderate'
            )
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', '')
                })
        
        return results
    except ImportError:
        print("[WARNING] duckduckgo-search not installed")
        return []
    except Exception as e:
        return []


def identify_material_type(text: str) -> Optional[str]:
    """Identify the type of material transfer from text"""
    text_lower = text.lower()
    
    for material_type, keywords in MATERIALS_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return material_type
    
    return None


def identify_relationship(text: str, material_type: Optional[str]) -> str:
    """Identify the relationship type from text and material type"""
    text_lower = text.lower()
    
    relationship_map = {
        'technology_transfer': 'Technology Transfer',
        'material_supply': 'Material Supply',
        'equipment': 'Equipment Procurement',
        'ip_licensing': 'IP Licensing',
        'prototype': 'Prototype Development',
        'subcontract': 'Subcontract',
        'software': 'Software License'
    }
    
    if material_type and material_type in relationship_map:
        return relationship_map[material_type]
    
    # Fallback detection
    if 'agreement' in text_lower or 'contract' in text_lower:
        return 'Contract Agreement'
    if 'partner' in text_lower or 'collaboration' in text_lower:
        return 'Partnership'
    if 'transfer' in text_lower:
        return 'Transfer'
    
    return 'Materials Flow'


def extract_materials_info(entity_name: str, search_results: List[Dict], 
                          database_entities: Dict[str, Entity]) -> List[Dict]:
    """Extract materials and technology flow information from search results"""
    flows = []
    
    # Flatten all keywords for quick detection
    all_keywords = []
    for keywords in MATERIALS_KEYWORDS.values():
        all_keywords.extend(keywords)
    
    for result in search_results:
        # Check specificity score
        specificity_score = calculate_specificity_score(result)
        if specificity_score < -1:  # Allow slightly negative for materials (less common)
            continue
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        text_lower = text.lower()
        
        # Check if any materials keywords match
        if any(keyword.lower() in text_lower for keyword in all_keywords):
            # Identify material type
            material_type = identify_material_type(text)
            
            # Extract date
            start_date = extract_date(text)
            
            # Identify relationship type
            relationship = identify_relationship(text, material_type)
            
            # Extract target entity
            target = extract_target_entity(text, entity_name, database_entities)
            
            if material_type or target:
                source_credibility = get_source_credibility_score(result.get('url', ''))
                
                flow_data = {
                    'source': entity_name,
                    'target': target or 'Unknown',
                    'material_type': material_type or 'unknown',
                    'relationship': relationship,
                    'description': result.get('snippet', '')[:300],
                    'start_date': start_date.isoformat() if start_date else None,
                    'source_citation': result.get('url', ''),
                    'specificity_score': specificity_score,
                    'source_credibility': source_credibility
                }
                flows.append(flow_data)
                
                print(f"    [MATERIALS] Type: {material_type}")
                if target:
                    print(f"    [MATERIALS] Target: {target}")
    
    return flows


def validate_materials_flow(flow: Dict) -> Dict:
    """Validate a materials flow record"""
    errors = []
    warnings = []
    
    # Required fields
    if not flow.get('source'):
        errors.append("Missing source")
    
    if flow.get('target') == 'Unknown' and not flow.get('material_type'):
        errors.append("Unknown target and no material type")
    
    # Quality checks
    if not flow.get('material_type') or flow.get('material_type') == 'unknown':
        warnings.append("Unknown material type")
    
    if not flow.get('start_date'):
        warnings.append("No date specified")
    
    if not flow.get('source_citation'):
        warnings.append("No citation URL")
    
    # Calculate quality score
    base_score = 1.0
    base_score -= len(errors) * 0.3
    base_score -= len(warnings) * 0.1
    
    if flow.get('material_type') and flow.get('material_type') != 'unknown':
        base_score += 0.15
    if flow.get('start_date'):
        base_score += 0.1
    if flow.get('source_citation'):
        base_score += 0.1
    
    base_score = max(0.0, min(1.0, base_score))
    
    # Weight by source credibility
    source_cred = flow.get('source_credibility', 0.4)
    quality_score = (base_score * 0.7) + (source_cred * 0.3)
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'quality_score': quality_score
    }


def research_entity_materials(entity: Entity, db_session) -> List[Dict]:
    """Research materials and technology transfers for a single entity"""
    entity_name = entity.display_name
    print(f"\nResearching materials for: {entity_name} ({entity.entity_type})")
    
    # Get all entities from database for matching
    all_entities = db_session.query(Entity).all()
    database_entities = {normalize_name(e.display_name): e for e in all_entities}
    
    # Check cache
    cache_file = CACHE_DIR / f"mat_{hashlib.md5(entity_name.encode()).hexdigest()}.json"
    if cache_file.exists():
        print(f"  [CACHE] Using cached results")
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_flows = json.load(f)
            validated_flows = []
            for flow in cached_flows:
                validation = validate_materials_flow(flow)
                if validation['valid']:
                    validated_flows.append(flow)
            return validated_flows
    
    flows = []
    
    # Search queries for materials/technology transfers
    search_queries = [
        f'"{entity_name}" technology transfer agreement',
        f'"{entity_name}" equipment procurement contract',
        f'"{entity_name}" material supply',
        f'"{entity_name}" patent license',
        f'"{entity_name}" subcontract award',
        f'"{entity_name}" prototype development',
        f'"{entity_name}" IP licensing',
    ]
    
    for query in search_queries:
        print(f"  Searching: {query}")
        results = search_web(query, max_results=3)
        time.sleep(SEARCH_DELAY)
        
        print(f"    Found {len(results)} search results")
        extracted = extract_materials_info(entity_name, results, database_entities)
        print(f"    Extracted {len(extracted)} materials flows")
        flows.extend(extracted)
        
        if len(flows) >= MAX_RESULTS_PER_ENTITY:
            break
    
    # Validate flows
    validated_flows = []
    for flow in flows:
        validation = validate_materials_flow(flow)
        if validation['valid']:
            flow['quality_score'] = validation['quality_score']
            validated_flows.append(flow)
        else:
            print(f"  [SKIP] Flow rejected: {', '.join(validation['errors'])}")
    
    # Remove duplicates
    seen = set()
    unique_flows = []
    for flow in validated_flows:
        key = (flow['source'], flow['target'], flow['material_type'], flow['relationship'])
        if key not in seen:
            seen.add(key)
            unique_flows.append(flow)
    
    # Cache results
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(unique_flows, f, indent=2, default=str)
    
    print(f"  [OK] Found {len(unique_flows)} validated materials flows")
    return unique_flows


def save_materials_to_csv(flows: List[Dict], output_path: Path):
    """Save discovered materials flows to CSV file"""
    if not flows:
        return
    
    file_exists = output_path.exists()
    
    with open(output_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['source', 'target', 'material_type', 'relationship', 'description',
                     'start_date', 'end_date', 'source_citation', 'edge_id', 
                     'source_norm', 'target_norm', 'quality_score']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for flow in flows:
            edge_id = generate_edge_id(
                flow['source'],
                flow.get('target', 'Unknown'),
                flow.get('material_type', 'unknown'),
                flow['relationship']
            )
            
            writer.writerow({
                'source': flow['source'],
                'target': flow.get('target', 'Unknown'),
                'material_type': flow.get('material_type', 'unknown'),
                'relationship': flow['relationship'],
                'description': flow.get('description', '')[:500],
                'start_date': flow.get('start_date', ''),
                'end_date': '',
                'source_citation': flow.get('source_citation', ''),
                'edge_id': edge_id,
                'source_norm': normalize_name(flow['source']),
                'target_norm': normalize_name(flow.get('target', 'Unknown')),
                'quality_score': flow.get('quality_score', 0.0)
            })


def main():
    """Main materials research function"""
    print("=" * 70)
    print("Entity Materials & Technology Transfer Research Tool")
    print("=" * 70)
    
    db_path = PROJECT_ROOT / config['database']['path']
    engine = init_database(str(db_path))
    session_maker = get_session_maker(engine)
    db = session_maker()
    
    try:
        # Focus on organizations that deal with technology/materials
        entities = db.query(Entity).filter(
            Entity.entity_type.in_([
                'Corporation', 'Government Agency', 'Research Institution',
                'FFRDC', 'Laboratory', 'Contractor'
            ])
        ).all()
        
        print(f"\nFound {len(entities)} entities to research")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"Cache directory: {CACHE_DIR}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"materials_flows_{timestamp}.csv"
        
        all_flows = []
        
        for i, entity in enumerate(entities, 1):
            print(f"\n[{i}/{len(entities)}] Processing entity...")
            try:
                flows = research_entity_materials(entity, db)
                all_flows.extend(flows)
                
                if flows:
                    save_materials_to_csv(flows, output_file)
                
            except Exception as e:
                print(f"  [ERROR] Failed to research {entity.display_name}: {e}")
                continue
        
        print("\n" + "=" * 70)
        print(f"Materials research complete!")
        print(f"Total materials flows discovered: {len(all_flows)}")
        print(f"Output file: {output_file}")
        print("=" * 70)
        
        if all_flows:
            from collections import Counter
            type_counts = Counter(f.get('material_type', 'unknown') for f in all_flows)
            rel_counts = Counter(f['relationship'] for f in all_flows)
            
            print("\nSummary by material type:")
            for mat_type, count in type_counts.most_common():
                print(f"  {mat_type}: {count}")
            
            print("\nSummary by relationship:")
            for rel, count in rel_counts.most_common():
                print(f"  {rel}: {count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
