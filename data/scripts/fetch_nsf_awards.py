"""
Fetch NSF awards data for academic institutions
Uses the NSF Awards Search API
"""
import os
import json
import time
import argparse
import requests
from datetime import datetime
from typing import List, Dict


def fetch_nsf_awards(
    keywords: List[str],
    start_date: str = "01/01/2019",
    page: int = 1,
    rows_per_page: int = 25
) -> Dict:
    """
    Fetch NSF awards matching keywords
    
    API Documentation: https://www.research.gov/common/webapi/awardapisearch-v1.htm
    
    Args:
        keywords: List of search keywords
        start_date: Start date in MM/DD/YYYY format
        page: Page number (1-indexed)
        rows_per_page: Number of results per page (max 25)
    
    Returns:
        Dictionary with 'response' containing awards data
    """
    base_url = "https://www.research.gov/awardapi-service/v1/awards.json"
    
    # Build keyword query (OR logic)
    keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
    
    params = {
        'keyword': keyword_query,
        'dateStart': start_date,
        'printFields': 'id,title,fundsObligatedAmt,startDate,expDate,agency,awardee,piFirstName,piLastName,piEmail,abstractText',
        'offset': (page - 1) * rows_per_page + 1,  # NSF API uses 1-indexed offset
        'rpp': rows_per_page
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NSF awards: {e}")
        return {'response': {'award': []}}


def parse_institution(awardee_data: Dict) -> Dict:
    """
    Extract institution information from awardee data
    
    Returns:
        Dictionary with institution details
    """
    if not awardee_data:
        return {}
    
    return {
        'name': awardee_data.get('name', '').strip(),
        'city': awardee_data.get('city', '').strip(),
        'state': awardee_data.get('stateCode', '').strip(),
        'zip': awardee_data.get('zipCode', '').strip(),
        'country': awardee_data.get('countryCode', 'US').strip()
    }


def main():
    parser = argparse.ArgumentParser(description='Fetch NSF awards for academic institutions')
    parser.add_argument('--keywords_file', required=True, help='File with search keywords (one per line)')
    parser.add_argument('--output_dir', default='data/external/nsf_awards', help='Output directory')
    parser.add_argument('--start_date', default='01/01/2019', help='Start date (MM/DD/YYYY)')
    parser.add_argument('--max_pages', type=int, default=10, help='Max pages per keyword')
    parser.add_argument('--rows_per_page', type=int, default=25, help='Results per page (max 25)')
    
    args = parser.parse_args()
    
    # Load keywords
    with open(args.keywords_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(keywords)} keywords")
    print(f"Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Fetch awards for each keyword
    manifest = {
        'generated': datetime.utcnow().isoformat(),
        'start_date': args.start_date,
        'keywords': keywords,
        'fetches': []
    }
    
    total_awards = 0
    
    for keyword in keywords:
        print(f"\n=== Fetching awards for: {keyword} ===")
        
        keyword_awards = []
        
        for page in range(1, args.max_pages + 1):
            print(f"  Page {page}...", end=' ')
            
            data = fetch_nsf_awards([keyword], args.start_date, page, args.rows_per_page)
            
            awards = data.get('response', {}).get('award', [])
            
            if not awards:
                print("No more results")
                break
            
            print(f"{len(awards)} awards")
            keyword_awards.extend(awards)
            
            # Check if we've hit the last page
            if len(awards) < args.rows_per_page:
                break
            
            # Rate limiting (be nice to NSF API)
            time.sleep(1)
        
        if keyword_awards:
            # Save to file
            safe_keyword = keyword.replace(' ', '_').replace('/', '_')
            filename = f"nsf_{safe_keyword}.json"
            filepath = os.path.join(args.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(keyword_awards, f, indent=2)
            
            print(f"  Saved {len(keyword_awards)} awards to {filename}")
            total_awards += len(keyword_awards)
            
            manifest['fetches'].append({
                'keyword': keyword,
                'count': len(keyword_awards),
                'file': filename
            })
    
    # Save manifest
    manifest_path = os.path.join(args.output_dir, '_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Total awards fetched: {total_awards}")
    print(f"Manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()

