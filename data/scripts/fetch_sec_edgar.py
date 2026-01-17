#!/usr/bin/env python3
"""
SEC EDGAR filings scraper for financial flows and material transfers
Targets: 8-K, 10-K, 10-Q, DEF 14A, Form 4
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
OUTPUT_DIR = PROJECT_ROOT / "data" / "financial" / "sec_edgar"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = PROJECT_ROOT / "data" / "scripts" / ".cache" / "sec_edgar"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# SEC EDGAR API endpoints
SEC_EDGAR_BASE = "https://www.sec.gov"
SEC_COMPANY_SEARCH = f"{SEC_EDGAR_BASE}/cgi-bin/browse-edgar"
SEC_FILING_API = f"{SEC_EDGAR_BASE}/cgi-bin/viewer"

# Target form types
TARGET_FORMS = [
    "8-K",      # Material events (M&A, major contracts)
    "10-K",     # Annual reports (contract disclosures)
    "10-Q",     # Quarterly reports
    "DEF 14A",  # Proxy statements (executive connections)
    "4",        # Insider transactions (Form 4)
]

# Keywords to search for in filings
SEC_KEYWORDS = [
    "government contract", "defense contract", "classified",
    "security clearance", "DoD", "intelligence community",
    "subcontract", "material transfer", "acquisition",
    "merger", "partnership", "joint venture",
    "federal", "contract award", "task order",
]

# Rate limiting
SEARCH_DELAY = 1  # SEC requires user-agent and reasonable delays
USER_AGENT = "ProjectRawHorse/1.0 Research (contact@example.com)"


def get_company_filings(company_name: str, form_type: str = None, max_results: int = 100) -> List[Dict]:
    """
    Get filings for a company from SEC EDGAR
    
    Args:
        company_name: Company name to search
        form_type: Form type filter (8-K, 10-K, etc.)
        max_results: Maximum number of filings to return
    
    Returns:
        List of filing metadata dictionaries
    """
    try:
        # SEC EDGAR company search
        params = {
            'action': 'getcompany',
            'company': company_name,
            'type': form_type or '',
            'dateb': '',
            'owner': 'exclude',
            'count': max_results,
            'search_text': '',
        }
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(SEC_COMPANY_SEARCH, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        filings = []
        
        # Parse filing table
        table = soup.find('table', {'class': 'tableFile2'})
        if not table:
            return filings
        
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            
            filing_link = cols[1].find('a')
            if not filing_link:
                continue
            
            filing_info = {
                'form_type': cols[0].get_text(strip=True),
                'filing_date': cols[3].get_text(strip=True),
                'filing_url': SEC_EDGAR_BASE + filing_link.get('href'),
                'description': cols[2].get_text(strip=True),
                'company_name': company_name,
            }
            
            filings.append(filing_info)
        
        time.sleep(SEARCH_DELAY)
        return filings
        
    except Exception as e:
        print(f"  [ERROR] Failed to get filings for {company_name}: {e}")
        return []


def extract_filing_content(filing_url: str) -> Optional[str]:
    """
    Extract text content from SEC filing
    
    Args:
        filing_url: URL to SEC filing
    
    Returns:
        Filing text content or None
    """
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        response = requests.get(filing_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from filing document
        # SEC filings are often in specific divs or can be direct HTML
        content = soup.get_text()
        
        # Basic cleanup
        content = re.sub(r'\s+', ' ', content)
        
        return content
        
    except Exception as e:
        print(f"  [ERROR] Failed to extract filing content: {e}")
        return None


def extract_flows_from_filing(filing_text: str, company_name: str) -> List[Dict]:
    """
    Extract financial/material flows from SEC filing text
    
    Args:
        filing_text: Full text of SEC filing
        company_name: Name of company filing
    
    Returns:
        List of extracted flow dictionaries
    """
    if not filing_text:
        return []
    
    # Check compliance first
    is_compliant, keywords = compliance_check(filing_text)
    if not is_compliant:
        print(f"  [SKIP] Filing contains restricted keywords: {', '.join(keywords)}")
        return []
    
    flows = []
    
    # Pattern: Contract awards
    contract_patterns = [
        r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:contract|award|agreement)\s+(?:with|to|for)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s+for|\s+worth|\s+valued|\s|,|\.|$)',
        r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+awarded\s+(?:a\s+)?(?:\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?\s+)?(?:contract|agreement)\s+(?:to|with)\s+([A-Z][A-Za-z0-9\s&,.-]+?)',
    ]
    
    # Pattern: Acquisitions/M&A
    acquisition_patterns = [
        r'(?:acquired|acquisition|merger|to acquire)\s+(?:of\s+)?([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s+for|\s+worth|\s+valued|\s|,|\.|$)',
    ]
    
    # Extract contracts
    for pattern in contract_patterns:
        matches = re.finditer(pattern, filing_text, re.IGNORECASE)
        for match in matches:
            target = match.group(1) if match.lastindex >= 1 else None
            amount_str = match.group(2) if match.lastindex >= 2 else None
            
            if target and len(target.strip()) > 2:
                flow = {
                    'source': company_name,
                    'target': target.strip(),
                    'relationship': 'Contract',
                    'amount_usd': None,  # Will be extracted separately
                    'source_citation': '',
                    'notes': match.group(0)[:200],
                }
                flows.append(flow)
    
    # Extract acquisitions
    for pattern in acquisition_patterns:
        matches = re.finditer(pattern, filing_text, re.IGNORECASE)
        for match in matches:
            target = match.group(1) if match.lastindex >= 1 else None
            
            if target and len(target.strip()) > 2:
                flow = {
                    'source': company_name,
                    'target': target.strip(),
                    'relationship': 'M&A',
                    'amount_usd': None,
                    'source_citation': '',
                    'notes': match.group(0)[:200],
                }
                flows.append(flow)
    
    return flows


def search_entities_for_filings(entities: List[str], form_types: List[str] = None) -> List[Dict]:
    """
    Search SEC EDGAR for filings related to entities
    
    Args:
        entities: List of entity names to search
        form_types: List of form types to search (default: all target forms)
    
    Returns:
        List of all filings found
    """
    if form_types is None:
        form_types = TARGET_FORMS
    
    all_filings = []
    
    for entity in entities:
        print(f"\nSearching SEC EDGAR for: {entity}")
        
        for form_type in form_types:
            filings = get_company_filings(entity, form_type=form_type)
            print(f"  Found {len(filings)} {form_type} filings")
            
            for filing in filings:
                filing['entity_searched'] = entity
                all_filings.append(filing)
            
            time.sleep(SEARCH_DELAY)
    
    return all_filings


def save_filings_to_csv(filings: List[Dict], output_path: Path):
    """Save filings metadata to CSV"""
    if not filings:
        return
    
    fieldnames = ['company_name', 'form_type', 'filing_date', 'filing_url', 
                 'description', 'entity_searched']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for filing in filings:
            writer.writerow({
                'company_name': filing.get('company_name', ''),
                'form_type': filing.get('form_type', ''),
                'filing_date': filing.get('filing_date', ''),
                'filing_url': filing.get('filing_url', ''),
                'description': filing.get('description', ''),
                'entity_searched': filing.get('entity_searched', ''),
            })


def main():
    """Main function to search SEC EDGAR for entity filings"""
    print("=" * 70)
    print("SEC EDGAR Filings Scraper")
    print("=" * 70)
    
    # Example: Search for known entities
    # In production, load from database
    entities_to_search = [
        "Lockheed Martin",
        "Northrop Grumman",
        "General Dynamics",
        "Raytheon",
        "Boeing",
    ]
    
    print(f"\nSearching SEC EDGAR for {len(entities_to_search)} entities")
    print(f"Target forms: {', '.join(TARGET_FORMS)}")
    
    all_filings = search_entities_for_filings(entities_to_search)
    
    print(f"\n{'=' * 70}")
    print(f"Total filings found: {len(all_filings)}")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"sec_filings_{timestamp}.csv"
    save_filings_to_csv(all_filings, output_file)
    
    print(f"Saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
