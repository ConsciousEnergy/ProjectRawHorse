#!/usr/bin/env python3
"""
Court records fetcher using RECAP API for bid protests and contractor disputes
Targets: COFC, GAO bid protests, False Claims Act cases, whistleblower settlements
"""
import os
import sys
import csv
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from compliance_filter import compliance_check, validate_record_for_storage

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "reference" / "court_records"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# RECAP/CourtListener API (free alternative to PACER)
RECAP_API_BASE = "https://www.courtlistener.com/api/rest/v3"
COURTLISTENER_BASE = "https://www.courtlistener.com"

# Rate limiting
REQUEST_DELAY = 2
USER_AGENT = "ProjectRawHorse/1.0 Research (contact@example.com)"


def search_court_records(query: str, max_results: int = 50) -> List[Dict]:
    """
    Search court records via CourtListener/RECAP
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of court record metadata dictionaries
    """
    try:
        # Note: CourtListener requires API token for full access
        # For basic scraping, we can use their search interface
        search_url = f"{COURTLISTENER_BASE}/?q={quote_plus(query)}&type=docket&type=opinion"
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html',
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        records = []
        
        # Parse search results
        result_items = soup.find_all('div', class_='search-result-item')
        
        for item in result_items[:max_results]:
            title_elem = item.find('h4')
            link_elem = item.find('a', href=True)
            date_elem = item.find('span', class_='date')
            snippet_elem = item.find('p')
            
            if title_elem and link_elem:
                record = {
                    'source': 'CourtListener/RECAP',
                    'title': title_elem.get_text(strip=True),
                    'url': COURTLISTENER_BASE + link_elem.get('href'),
                    'date': date_elem.get_text(strip=True) if date_elem else None,
                    'type': 'Court Record',
                    'description': snippet_elem.get_text(strip=True)[:500] if snippet_elem else '',
                    'query': query,
                }
                
                is_compliant, _ = compliance_check(record['title'] + ' ' + record.get('description', ''))
                if is_compliant:
                    records.append(record)
        
        time.sleep(REQUEST_DELAY)
        return records
        
    except Exception as e:
        print(f"  [ERROR] Failed to search court records: {e}")
        return []


def extract_entities_from_records(records: List[Dict]) -> List[Dict]:
    """
    Extract entity relationships from court records
    
    Args:
        records: List of court record dictionaries
    
    Returns:
        List of extracted relationship dictionaries
    """
    relationships = []
    
    for record in records:
        # Look for bid protest patterns
        text = record.get('title', '') + ' ' + record.get('description', '')
        
        # Pattern: Bid protest cases
        if any(word in text.lower() for word in ['bid protest', 'contractor', 'award', 'solicitation']):
            # Extract entity names
            entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b'
            entities = re.findall(entity_pattern, text)
            
            # Filter common words
            common_words = {'Court', 'Federal', 'United', 'States', 'Government', 'Agency', 'Department'}
            entities = [e for e in entities if e not in common_words and len(e.split()) <= 3]
            
            if len(entities) >= 2:
                relationship = {
                    'source': entities[0],
                    'target': entities[1],
                    'label': 'Contractor Dispute',
                    'notes': f"From court record: {record.get('title', '')[:100]}",
                    'source_citation': record.get('url', ''),
                }
                relationships.append(relationship)
    
    return relationships


def save_to_csv(records: List[Dict], relationships: List[Dict], output_path: Path):
    """Save court records and relationships to CSV"""
    # Save records
    if records:
        records_file = output_path.parent / f"court_records_{output_path.stem}.csv"
        fieldnames = ['source', 'title', 'url', 'date', 'type', 'description', 'query']
        
        with open(records_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        
        print(f"Saved {len(records)} court records to: {records_file}")
    
    # Save relationships
    if relationships:
        rel_file = output_path.parent / f"relationships_from_court_{output_path.stem}.csv"
        fieldnames = ['source', 'target', 'label', 'notes', 'source_citation']
        
        with open(rel_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(relationships)
        
        print(f"Saved {len(relationships)} relationships to: {rel_file}")


def main():
    """Main function to search court records"""
    print("=" * 70)
    print("Court Records Fetcher")
    print("=" * 70)
    
    # Search queries related to defense contractors
    search_queries = [
        'bid protest',
        'contractor dispute',
        'false claims act',
        'government contract',
        'defense contractor',
    ]
    
    all_records = []
    
    for query in search_queries:
        print(f"\nSearching: {query}")
        records = search_court_records(query, max_results=20)
        print(f"  Found {len(records)} records")
        all_records.extend(records)
    
    print(f"\n{'=' * 70}")
    print(f"Total records found: {len(all_records)}")
    
    # Extract relationships
    relationships = extract_entities_from_records(all_records)
    print(f"Extracted {len(relationships)} relationships")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"court_data_{timestamp}.csv"
    save_to_csv(all_records, relationships, output_file)
    
    print("=" * 70)


if __name__ == "__main__":
    main()
