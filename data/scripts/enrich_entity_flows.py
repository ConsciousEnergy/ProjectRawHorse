#!/usr/bin/env python3
"""
Enrich entity data by researching financial and material flows via web search
IMPROVED VERSION with all enhancements
"""
import os
import sys
import csv
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from urllib.parse import quote_plus

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, Entity, MoneyFlow, Relationship
import yaml

# Import improved extraction modules
from entity_recognition import extract_target_entity
from amount_extraction import extract_amount
from date_extraction import extract_date
from validate_flows import calculate_specificity_score, validate_flow
from compliance_filter import compliance_check, validate_record_for_storage

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "financial"
CACHE_DIR = PROJECT_ROOT / "data" / "scripts" / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# Load configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Web search configuration
SEARCH_DELAY = 2  # Seconds between searches to avoid rate limiting
MAX_RESULTS_PER_ENTITY = 5  # Maximum search results to process per entity


def generate_edge_id(source: str, target: str, relationship: str, amount: Optional[float] = None) -> str:
    """Generate unique edge ID"""
    key = f"{source}|{target}|{relationship}|{amount or ''}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def normalize_name(name: str) -> str:
    """Normalize entity name for matching"""
    return name.strip().upper().replace('"', '').replace("'", "")


def search_web(query: str, max_results: int = 5) -> List[Dict]:
    """
    Perform web search using duckduckgo-search library (no API key required)
    Returns list of search results with title, snippet, and URL
    """
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            from duckduckgo_search import DDGS
        
        results = []
        
        # Use duckduckgo-search library for actual web search
        with DDGS() as ddgs:
            # Perform text search
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
        print(f"  [WARNING] duckduckgo-search not installed. Install with: pip install duckduckgo-search")
        return []
    except Exception as e:
        # Silently fail to avoid spamming warnings
        return []


def extract_financial_info(entity_name: str, search_results: List[Dict], database_entities: Dict[str, Entity]) -> List[Dict]:
    """
    Extract financial and material flow information from search results
    Uses improved extraction algorithms for better accuracy
    """
    flows = []
    
    financial_keywords = [
        'contract', 'award', 'acquisition', 'merger', 'investment', 'funding',
        'partnership', 'deal', 'transaction', 'purchase', 'sale', 'divestiture',
        'million', 'billion', 'dollar', '$', 'USD', 'acquired', 'acquires'
    ]
    
    for result in search_results:
        # Phase 4: Specificity filtering
        specificity_score = calculate_specificity_score(result)
        if specificity_score <= 0:
            continue
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in financial_keywords):
            # Phase 2: Improved amount extraction
            amount = extract_amount(text)
            
            # Phase 3: Date extraction
            start_date = extract_date(text)
            
            # Relationship type
            relationship = "Financial Flow"
            if any(word in text_lower for word in ['acquire', 'acquisition', 'merger', 'purchase']):
                relationship = "M&A"
            elif any(word in text_lower for word in ['contract', 'award', 'deal']):
                relationship = "Contract"
            elif any(word in text_lower for word in ['investment', 'funding', 'fund']):
                relationship = "Investment"
            elif any(word in text_lower for word in ['partnership', 'partner', 'collaborate']):
                relationship = "Partnership"
            
            # Phase 1: Enhanced target entity extraction
            target = extract_target_entity(text, entity_name, database_entities)
            
            if amount or relationship != "Financial Flow" or target:
                flow_data = {
                    'source': entity_name,
                    'target': target or 'Unknown',
                    'relationship': relationship,
                    'amount_usd': amount,
                    'start_date': start_date.isoformat() if start_date else None,
                    'source_citation': result.get('url', ''),
                    'notes': result.get('snippet', '')[:200],
                    'specificity_score': specificity_score
                }
                flows.append(flow_data)
                if target:
                    print(f"    [EXTRACTED] Target: {target}")
                if amount:
                    print(f"    [EXTRACTED] Amount: ${amount:,.0f}")
                if start_date:
                    print(f"    [EXTRACTED] Date: {start_date}")
    
    return flows


def research_entity_flows(entity: Entity, db_session) -> List[Dict]:
    """Research financial and material flows for a single entity"""
    entity_name = entity.display_name
    print(f"\nResearching: {entity_name} ({entity.entity_type})")
    
    # Get all entities from database for matching
    all_entities = db_session.query(Entity).all()
    database_entities = {normalize_name(e.display_name): e for e in all_entities}
    
    # Check cache
    cache_file = CACHE_DIR / f"{hashlib.md5(entity_name.encode()).hexdigest()}.json"
    if cache_file.exists():
        print(f"  [CACHE] Using cached results")
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_flows = json.load(f)
            validated_flows = []
            for flow in cached_flows:
                validation = validate_flow(flow)
                if validation['valid']:
                    validated_flows.append(flow)
            return validated_flows
    
    flows = []
    
    # Phase 6: Enhanced search queries
    search_queries = [
        f'"{entity_name}" acquisition announcement',
        f'"{entity_name}" contract award news',
        f'"{entity_name}" merger deal value',
        f'"{entity_name}" USAspending contract',
        f'"{entity_name}" federal award',
        f'"{entity_name}" M&A news',
        f'"{entity_name}" investment announcement',
    ]
    
    for query in search_queries:
        print(f"  Searching: {query}")
        results = search_web(query, max_results=3)
        time.sleep(SEARCH_DELAY)
        
        print(f"    Found {len(results)} search results")
        extracted = extract_financial_info(entity_name, results, database_entities)
        print(f"    Extracted {len(extracted)} flows from results")
        flows.extend(extracted)
        
        if len(flows) >= MAX_RESULTS_PER_ENTITY:
            break
    
    # Phase 5: Validation
    validated_flows = []
    for flow in flows:
        validation = validate_flow(flow)
        if validation['valid']:
            flow['quality_score'] = validation['quality_score']
            validated_flows.append(flow)
        else:
            target_info = f"target={flow.get('target', 'None')}"
            amount_info = f"amount=${flow.get('amount_usd', 0):,.0f}" if flow.get('amount_usd') else "amount=None"
            print(f"  [SKIP] Flow rejected: {', '.join(validation['errors'])} ({target_info}, {amount_info})")
    
    # Remove duplicates
    seen = set()
    unique_flows = []
    for flow in validated_flows:
        key = (flow['source'], flow['target'], flow['relationship'])
        if key not in seen:
            seen.add(key)
            unique_flows.append(flow)
    
    # Cache results
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(unique_flows, f, indent=2, default=str)
    
    print(f"  [OK] Found {len(unique_flows)} validated flows")
    return unique_flows


def save_flows_to_csv(flows: List[Dict], output_path: Path):
    """Save discovered flows to CSV file"""
    if not flows:
        return
    
    file_exists = output_path.exists()
    
    with open(output_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['source', 'target', 'relationship', 'amount_usd', 'start_date', 
                     'end_date', 'source_citation', 'notes', 'edge_id', 'source_norm', 'target_norm']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for flow in flows:
            edge_id = generate_edge_id(
                flow['source'], 
                flow.get('target', 'Unknown'),
                flow['relationship'],
                flow.get('amount_usd')
            )
            
            writer.writerow({
                'source': flow['source'],
                'target': flow.get('target', 'Unknown'),
                'relationship': flow['relationship'],
                'amount_usd': flow.get('amount_usd', ''),
                'start_date': flow.get('start_date', ''),
                'end_date': '',
                'source_citation': flow.get('source_citation', ''),
                'notes': flow.get('notes', ''),
                'edge_id': edge_id,
                'source_norm': normalize_name(flow['source']),
                'target_norm': normalize_name(flow.get('target', 'Unknown'))
            })


def main():
    """Main research function"""
    print("=" * 70)
    print("Entity Financial Flow Research Tool (Enhanced)")
    print("=" * 70)
    
    db_path = PROJECT_ROOT / config['database']['path']
    engine = init_database(str(db_path))
    session_maker = get_session_maker(engine)
    db = session_maker()
    
    try:
        entities = db.query(Entity).filter(
            Entity.entity_type.in_(['Corporation', 'Government Agency', 'Research Institution', 'Investment Firm'])
        ).all()
        
        print(f"\nFound {len(entities)} entities to research")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"Cache directory: {CACHE_DIR}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"enriched_flows_{timestamp}.csv"
        
        all_flows = []
        
        for i, entity in enumerate(entities, 1):
            print(f"\n[{i}/{len(entities)}] Processing entity...")
            try:
                flows = research_entity_flows(entity, db)
                all_flows.extend(flows)
                
                if flows:
                    save_flows_to_csv(flows, output_file)
                
            except Exception as e:
                print(f"  [ERROR] Failed to research {entity.display_name}: {e}")
                continue
        
        print("\n" + "=" * 70)
        print(f"Research complete!")
        print(f"Total flows discovered: {len(all_flows)}")
        print(f"Output file: {output_file}")
        print("=" * 70)
        
        if all_flows:
            from collections import Counter
            rel_counts = Counter(f['relationship'] for f in all_flows)
            print("\nSummary by relationship type:")
            for rel, count in rel_counts.most_common():
                print(f"  {rel}: {count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
