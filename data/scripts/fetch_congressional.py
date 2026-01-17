#!/usr/bin/env python3
"""
Congressional records fetcher for hearing transcripts and GAO reports
Targets: Committee hearings, CRS reports, GAO audits, IG reports
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
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import re

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from compliance_filter import compliance_check, validate_record_for_storage

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "reference" / "congressional"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Congressional data sources
CONGRESSIONAL_SOURCES = {
    'gao': {
        'base_url': 'https://www.gao.gov/reports-testimonies',
        'search_url': 'https://www.gao.gov/api/v1/reports',
    },
    'crs': {
        'base_url': 'https://crsreports.congress.gov',
        'search_url': 'https://crsreports.congress.gov/search',
    },
    'congress': {
        'base_url': 'https://www.congress.gov',
        'hearing_url': 'https://www.congress.gov/search',
    },
}

# Rate limiting
REQUEST_DELAY = 2
USER_AGENT = "ProjectRawHorse/1.0 Research (contact@example.com)"


def search_gao_reports(query: str, max_results: int = 50) -> List[Dict]:
    """
    Search GAO reports
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of GAO report metadata dictionaries
    """
    try:
        # GAO API search
        params = {
            'q': query,
            'page': 1,
            'page_size': min(max_results, 50),
        }
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
        }
        
        response = requests.get(CONGRESSIONAL_SOURCES['gao']['search_url'], 
                              params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        reports = []
        
        if 'results' in data:
            for item in data['results']:
                report = {
                    'source': 'GAO',
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'date': item.get('published_date', ''),
                    'type': item.get('type', ''),
                    'description': item.get('summary', '')[:500],
                    'query': query,
                }
                
                # Compliance check
                combined_text = report['title'] + ' ' + report.get('description', '')
                is_compliant, _ = compliance_check(combined_text)
                if is_compliant:
                    reports.append(report)
        
        time.sleep(REQUEST_DELAY)
        return reports
        
    except Exception as e:
        print(f"  [ERROR] Failed to search GAO reports: {e}")
        return []


def search_congressional_hearings(query: str, max_results: int = 50) -> List[Dict]:
    """
    Search Congressional hearing transcripts
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of hearing metadata dictionaries
    """
    try:
        # Congress.gov search
        search_url = f"https://www.congress.gov/search?q={{{query}}}&searchResultViewType=expanded"
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html',
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        hearings = []
        
        # Parse search results
        result_items = soup.find_all('div', class_='search-result-item')
        
        for item in result_items[:max_results]:
            title_elem = item.find('h3')
            link_elem = item.find('a', href=True)
            date_elem = item.find('span', class_='date')
            
            if title_elem and link_elem:
                hearing = {
                    'source': 'Congress.gov',
                    'title': title_elem.get_text(strip=True),
                    'url': urljoin('https://www.congress.gov', link_elem.get('href')),
                    'date': date_elem.get_text(strip=True) if date_elem else None,
                    'type': 'Hearing',
                    'description': item.get_text(strip=True)[:500],
                    'query': query,
                }
                
                is_compliant, _ = compliance_check(hearing['title'] + ' ' + hearing.get('description', ''))
                if is_compliant:
                    hearings.append(hearing)
        
        time.sleep(REQUEST_DELAY)
        return hearings
        
    except Exception as e:
        print(f"  [ERROR] Failed to search Congressional hearings: {e}")
        return []


def extract_entities_from_text(text: str) -> List[str]:
    """Extract potential entity names from text"""
    if not text:
        return []
    
    # Pattern for capitalized entity names
    entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b'
    matches = re.findall(entity_pattern, text)
    
    # Filter out common words and short matches
    common_words = {'The', 'This', 'That', 'These', 'Those', 'With', 'From', 'For'}
    entities = [m for m in matches if m not in common_words and len(m) > 3]
    
    return list(set(entities))[:10]  # Return unique, limit to 10


def save_to_csv(records: List[Dict], output_path: Path):
    """Save records to CSV"""
    if not records:
        return
    
    fieldnames = ['source', 'title', 'url', 'date', 'type', 'description', 'query']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            writer.writerow(record)


def main():
    """Main function to search Congressional records"""
    print("=" * 70)
    print("Congressional Records Fetcher")
    print("=" * 70)
    
    # Search queries related to defense/intelligence
    search_queries = [
        'defense contract',
        'intelligence community',
        'UAP',
        'aerial phenomena',
        'material transfer',
        'subcontract',
    ]
    
    all_records = []
    
    print("\nSearching GAO reports...")
    for query in search_queries:
        print(f"  Query: {query}")
        gao_reports = search_gao_reports(query, max_results=20)
        print(f"    Found {len(gao_reports)} reports")
        all_records.extend(gao_reports)
    
    print("\nSearching Congressional hearings...")
    for query in search_queries:
        print(f"  Query: {query}")
        hearings = search_congressional_hearings(query, max_results=20)
        print(f"    Found {len(hearings)} hearings")
        all_records.extend(hearings)
    
    print(f"\n{'=' * 70}")
    print(f"Total records found: {len(all_records)}")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"congressional_records_{timestamp}.csv"
    save_to_csv(all_records, output_file)
    
    print(f"Saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
