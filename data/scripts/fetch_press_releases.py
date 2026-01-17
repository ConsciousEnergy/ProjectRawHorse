#!/usr/bin/env python3
"""
Press release aggregator for contract announcements and M&A news
Sources: PR Newswire, Business Wire, GlobeNewswire, company investor relations
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
from amount_extraction import extract_amount
from date_extraction import extract_date
from entity_recognition import extract_entities_patterns

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "financial" / "press_releases"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Press release sources
PRESS_SOURCES = {
    'pr_newswire': {
        'base_url': 'https://www.prnewswire.com',
        'search_url': 'https://www.prnewswire.com/news-releases/news-list/',
    },
    'business_wire': {
        'base_url': 'https://www.businesswire.com',
        'search_url': 'https://www.businesswire.com/portal/site/home/news/',
    },
    'globenewswire': {
        'base_url': 'https://www.globenewswire.com',
        'search_url': 'https://www.globenewswire.com/en/search/subject/all',
    },
}

# Rate limiting
REQUEST_DELAY = 2
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def search_pr_newswire(query: str, max_results: int = 50) -> List[Dict]:
    """
    Search PR Newswire for press releases
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of press release metadata dictionaries
    """
    try:
        search_url = f"https://www.prnewswire.com/search/news/?keyword={quote_plus(query)}&page=1"
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html',
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        releases = []
        
        # Parse search results
        news_items = soup.find_all('div', class_='news-release-consolidated')
        
        for item in news_items[:max_results]:
            title_elem = item.find('h3')
            link_elem = item.find('a', href=True)
            date_elem = item.find('span', class_='release-date')
            snippet_elem = item.find('p')
            
            if title_elem and link_elem:
                release = {
                    'source': 'PR Newswire',
                    'title': title_elem.get_text(strip=True),
                    'url': urljoin(PRESS_SOURCES['pr_newswire']['base_url'], link_elem.get('href')),
                    'date': date_elem.get_text(strip=True) if date_elem else None,
                    'snippet': snippet_elem.get_text(strip=True)[:300] if snippet_elem else '',
                    'query': query,
                }
                
                is_compliant, _ = compliance_check(release['title'] + ' ' + release.get('snippet', ''))
                if is_compliant:
                    releases.append(release)
        
        time.sleep(REQUEST_DELAY)
        return releases
        
    except Exception as e:
        print(f"  [ERROR] Failed to search PR Newswire: {e}")
        return []


def search_business_wire(query: str, max_results: int = 50) -> List[Dict]:
    """
    Search Business Wire for press releases
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of press release metadata dictionaries
    """
    try:
        search_url = f"https://www.businesswire.com/portal/site/home/search/?vnsId=31338&searchText={quote_plus(query)}"
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html',
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        releases = []
        
        # Parse search results
        news_items = soup.find_all('div', class_='bw-news-release-item')
        
        for item in news_items[:max_results]:
            title_elem = item.find('h4')
            link_elem = item.find('a', href=True)
            date_elem = item.find('time')
            snippet_elem = item.find('p')
            
            if title_elem and link_elem:
                release = {
                    'source': 'Business Wire',
                    'title': title_elem.get_text(strip=True),
                    'url': urljoin(PRESS_SOURCES['business_wire']['base_url'], link_elem.get('href')),
                    'date': date_elem.get('datetime') if date_elem else None,
                    'snippet': snippet_elem.get_text(strip=True)[:300] if snippet_elem else '',
                    'query': query,
                }
                
                is_compliant, _ = compliance_check(release['title'] + ' ' + release.get('snippet', ''))
                if is_compliant:
                    releases.append(release)
        
        time.sleep(REQUEST_DELAY)
        return releases
        
    except Exception as e:
        print(f"  [ERROR] Failed to search Business Wire: {e}")
        return []


def extract_flows_from_release(release: Dict) -> List[Dict]:
    """
    Extract financial/material flows from press release
    
    Args:
        release: Press release metadata dictionary
    
    Returns:
        List of extracted flow dictionaries
    """
    flows = []
    
    combined_text = release.get('title', '') + ' ' + release.get('snippet', '')
    
    # Extract amount
    amount = extract_amount(combined_text)
    
    # Extract date
    date = extract_date(combined_text)
    
    # Extract relationship type
    relationship = "Financial Flow"
    if any(word in combined_text.lower() for word in ['acquire', 'acquisition', 'merger']):
        relationship = "M&A"
    elif any(word in combined_text.lower() for word in ['contract', 'award', 'deal']):
        relationship = "Contract"
    elif any(word in combined_text.lower() for word in ['partnership', 'partner']):
        relationship = "Partnership"
    
    # Extract entities (simple pattern matching)
    entities = extract_entities_patterns(combined_text, release.get('source', ''))
    
    if entities:
        for entity in entities[:2]:  # Limit to 2 entities per release
            flow = {
                'source': release.get('source', 'Unknown'),
                'target': entity,
                'relationship': relationship,
                'amount_usd': amount,
                'start_date': date.isoformat() if date else None,
                'source_citation': release.get('url', ''),
                'notes': release.get('title', '')[:200],
            }
            flows.append(flow)
    
    return flows


def save_to_csv(releases: List[Dict], flows: List[Dict], output_path: Path):
    """Save press releases and extracted flows to CSV"""
    # Save releases
    if releases:
        releases_file = output_path.parent / f"press_releases_{output_path.stem}.csv"
        fieldnames = ['source', 'title', 'url', 'date', 'snippet', 'query']
        
        with open(releases_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(releases)
        
        print(f"Saved {len(releases)} press releases to: {releases_file}")
    
    # Save flows
    if flows:
        flows_file = output_path.parent / f"flows_from_press_{output_path.stem}.csv"
        fieldnames = ['source', 'target', 'relationship', 'amount_usd', 'start_date', 'source_citation', 'notes']
        
        with open(flows_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flows)
        
        print(f"Saved {len(flows)} flows to: {flows_file}")


def main():
    """Main function to search press releases"""
    print("=" * 70)
    print("Press Release Aggregator")
    print("=" * 70)
    
    # Search queries
    search_queries = [
        'government contract',
        'defense contract award',
        'acquisition',
        'merger',
        'partnership',
    ]
    
    all_releases = []
    all_flows = []
    
    print("\nSearching PR Newswire...")
    for query in search_queries:
        print(f"  Query: {query}")
        releases = search_pr_newswire(query, max_results=20)
        print(f"    Found {len(releases)} releases")
        all_releases.extend(releases)
        
        # Extract flows
        for release in releases:
            flows = extract_flows_from_release(release)
            all_flows.extend(flows)
    
    print("\nSearching Business Wire...")
    for query in search_queries:
        print(f"  Query: {query}")
        releases = search_business_wire(query, max_results=20)
        print(f"    Found {len(releases)} releases")
        all_releases.extend(releases)
        
        # Extract flows
        for release in releases:
            flows = extract_flows_from_release(release)
            all_flows.extend(flows)
    
    print(f"\n{'=' * 70}")
    print(f"Total releases found: {len(all_releases)}")
    print(f"Total flows extracted: {len(all_flows)}")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"press_data_{timestamp}.csv"
    save_to_csv(all_releases, all_flows, output_file)
    
    print("=" * 70)


if __name__ == "__main__":
    main()
