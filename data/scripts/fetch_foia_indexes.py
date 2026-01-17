#!/usr/bin/env python3
"""
FOIA reading room scraper for agency document indexes
Extracts released document metadata to identify FOIA-verifiable data
"""
import os
import sys
import csv
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from compliance_filter import compliance_check, validate_record_for_storage

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "foia" / "reading_rooms"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# FOIA Reading Room URLs
FOIA_READING_ROOMS = {
    'DOD': {
        'url': 'https://www.esd.whs.mil/FOIA/Reading-Room/',
        'description': 'DoD FOIA Reading Room'
    },
    'DOE': {
        'url': 'https://www.energy.gov/management/foia-library',
        'description': 'DOE FOIA Library'
    },
    'NASA': {
        'url': 'https://www.nasa.gov/news-release-category/foia-reading-room/',
        'description': 'NASA FOIA Reading Room'
    },
    'DHS': {
        'url': 'https://www.dhs.gov/foia-library',
        'description': 'DHS FOIA Library'
    },
    'NRO': {
        'url': 'https://www.nro.gov/FOIA/Reading-Room/',
        'description': 'NRO FOIA Reading Room'
    },
    'NGA': {
        'url': 'https://www.nga.mil/FOIA/',
        'description': 'NGA FOIA Reading Room'
    },
}

# Rate limiting
REQUEST_DELAY = 2
USER_AGENT = "ProjectRawHorse/1.0 Research (contact@example.com)"


def scrape_reading_room(url: str, agency: str) -> List[Dict]:
    """
    Scrape a FOIA reading room for document metadata
    
    Args:
        url: Base URL of the FOIA reading room
        agency: Agency name
    
    Returns:
        List of document metadata dictionaries
    """
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        documents = []
        
        # Common patterns for FOIA reading room pages
        # Look for links to documents, tables, lists
        
        # Pattern 1: Document links in tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 2:
                    continue
                
                # Look for links
                link_elem = row.find('a', href=True)
                if link_elem:
                    doc_title = link_elem.get_text(strip=True)
                    doc_url = urljoin(url, link_elem.get('href'))
                    
                    # Extract date from row if present
                    date_text = ' '.join([col.get_text(strip=True) for col in cols])
                    date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', date_text)
                    date_str = date_match.group(0) if date_match else None
                    
                    doc_metadata = {
                        'agency': agency,
                        'title': doc_title[:200] if doc_title else '',
                        'url': doc_url,
                        'date': date_str,
                        'description': ' '.join([col.get_text(strip=True) for col in cols])[:500],
                        'scraped_date': datetime.now().isoformat(),
                    }
                    
                    # Compliance check
                    is_compliant, _ = compliance_check(doc_metadata['title'] + ' ' + doc_metadata.get('description', ''))
                    if is_compliant:
                        documents.append(doc_metadata)
        
        # Pattern 2: List of links
        link_lists = soup.find_all(['ul', 'ol'])
        for link_list in link_lists:
            links = link_list.find_all('a', href=True)
            for link in links:
                link_text = link.get_text(strip=True)
                link_url = urljoin(url, link.get('href'))
                
                # Check if it looks like a document link
                if any(ext in link_url.lower() for ext in ['.pdf', '.doc', '.html', '.txt']):
                    doc_metadata = {
                        'agency': agency,
                        'title': link_text[:200] if link_text else '',
                        'url': link_url,
                        'date': None,
                        'description': '',
                        'scraped_date': datetime.now().isoformat(),
                    }
                    
                    is_compliant, _ = compliance_check(link_text)
                    if is_compliant:
                        documents.append(doc_metadata)
        
        # Pattern 3: Direct document links in content
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if any(keyword in href.lower() for keyword in ['foia', 'reading', 'release', 'document']):
                link_text = link.get_text(strip=True)
                if link_text and len(link_text) > 10:  # Filter out navigation links
                    doc_metadata = {
                        'agency': agency,
                        'title': link_text[:200],
                        'url': urljoin(url, href),
                        'date': None,
                        'description': '',
                        'scraped_date': datetime.now().isoformat(),
                    }
                    
                    is_compliant, _ = compliance_check(link_text)
                    if is_compliant:
                        documents.append(doc_metadata)
        
        time.sleep(REQUEST_DELAY)
        return documents
        
    except Exception as e:
        print(f"  [ERROR] Failed to scrape {agency} reading room: {e}")
        return []


def extract_foia_targets_from_documents(documents: List[Dict]) -> List[Dict]:
    """
    Extract potential FOIA targets from document metadata
    
    Args:
        documents: List of document metadata dictionaries
    
    Returns:
        List of FOIA target suggestions
    """
    foia_targets = []
    
    # Keywords that suggest valuable FOIA targets
    valuable_keywords = [
        'contract', 'award', 'program', 'initiative',
        'material', 'transfer', 'analysis', 'study',
        'relationship', 'partnership', 'agreement',
    ]
    
    for doc in documents:
        title_lower = doc.get('title', '').lower()
        desc_lower = doc.get('description', '').lower()
        combined = title_lower + ' ' + desc_lower
        
        # Check if document mentions valuable topics
        if any(keyword in combined for keyword in valuable_keywords):
            # Extract entity names (simple pattern)
            entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            entities = re.findall(entity_pattern, doc.get('title', '') + ' ' + doc.get('description', ''))
            
            for entity in entities:
                if len(entity.split()) <= 4:  # Reasonable entity name length
                    foia_target = {
                        'agency': doc.get('agency', ''),
                        'record_request': f"All documents related to {entity} mentioned in {doc.get('title', 'document')[:100]}",
                        'timeframe': doc.get('date', 'Unknown'),
                        'relevance': 'Identified from reading room document',
                        'notes': f"Source: {doc.get('url', '')}",
                    }
                    foia_targets.append(foia_target)
    
    return foia_targets


def save_documents_to_csv(documents: List[Dict], output_path: Path):
    """Save document metadata to CSV"""
    if not documents:
        return
    
    fieldnames = ['agency', 'title', 'url', 'date', 'description', 'scraped_date']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for doc in documents:
            writer.writerow(doc)


def main():
    """Main function to scrape FOIA reading rooms"""
    print("=" * 70)
    print("FOIA Reading Room Scraper")
    print("=" * 70)
    
    all_documents = []
    
    for agency, info in FOIA_READING_ROOMS.items():
        print(f"\nScraping {agency} reading room: {info['url']}")
        documents = scrape_reading_room(info['url'], agency)
        print(f"  Found {len(documents)} documents")
        all_documents.extend(documents)
    
    print(f"\n{'=' * 70}")
    print(f"Total documents found: {len(all_documents)}")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"foia_documents_{timestamp}.csv"
    save_documents_to_csv(all_documents, output_file)
    
    print(f"Saved to: {output_file}")
    
    # Extract FOIA targets
    foia_targets = extract_foia_targets_from_documents(all_documents)
    print(f"\nExtracted {len(foia_targets)} potential FOIA targets")
    
    if foia_targets:
        targets_file = OUTPUT_DIR / f"foia_targets_suggestions_{timestamp}.csv"
        fieldnames = ['agency', 'record_request', 'timeframe', 'relevance', 'notes']
        
        with open(targets_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(foia_targets)
        
        print(f"FOIA targets saved to: {targets_file}")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
