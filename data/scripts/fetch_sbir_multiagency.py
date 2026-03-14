"""
Fetch SBIR/STTR awards from multiple agencies (DARPA, IARPA, NSF, etc.)

This script queries the SBIR.gov API for Small Business Innovation Research
and Small Business Technology Transfer awards across multiple agencies.

Usage:
    python data/scripts/fetch_sbir_multiagency.py --out_dir external/sbir_data --pages 5

Note: SBIR.gov API has rate limits. Use appropriate delays between requests.
"""

import os
import json
import time
import argparse
import requests
import datetime
from typing import Dict, List, Optional


def ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def fetch_sbir_awards(
    agency: str,
    keyword: Optional[str] = None,
    phase: Optional[str] = None,
    year_from: int = 2019,
    year_to: Optional[int] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict:
    """
    Fetch SBIR/STTR awards from SBIR.gov API.
    
    Args:
        agency: Agency abbreviation (DARPA, NSF, IARPA, etc.)
        keyword: Optional keyword search
        phase: Optional phase filter (I, II, III)
        year_from: Start year for awards
        year_to: End year for awards (default: current year)
        page: Page number
        page_size: Results per page
    
    Returns:
        JSON response from API
    """
    base_url = "https://www.sbir.gov/api/solicitations.json"
    
    if year_to is None:
        year_to = datetime.datetime.now().year
    
    # Build query parameters
    params = {
        'agency': agency,
        'page': page,
        'per_page': page_size,
    }
    
    if keyword:
        params['keyword'] = keyword
    
    if phase:
        params['phase'] = phase
    
    # Add year range (SBIR API uses fiscal year)
    params['year_from'] = year_from
    params['year_to'] = year_to
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SBIR data: {e}")
        return {"error": str(e), "results": []}


def fetch_sbir_awards_alt_endpoint(
    agency: str,
    keyword: Optional[str] = None,
    phase: Optional[str] = None,
    year_from: int = 2019,
    page: int = 1,
    page_size: int = 50
) -> Dict:
    """
    Alternative endpoint for SBIR awards (broader search).
    
    Uses the awards endpoint instead of solicitations.
    """
    base_url = "https://www.sbir.gov/api/awards.json"
    
    params = {
        'agency': agency,
        'page': page,
        'per_page': page_size,
        'year': year_from
    }
    
    if keyword:
        params['keyword'] = keyword
    
    if phase:
        params['phase'] = phase
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SBIR awards (alt endpoint): {e}")
        return {"error": str(e), "results": []}


def main():
    parser = argparse.ArgumentParser(
        description='Fetch SBIR/STTR awards from multiple agencies'
    )
    parser.add_argument(
        '--agencies',
        nargs='+',
        default=['DARPA', 'NSF', 'NASA', 'DOE', 'DHS', 'DOD', 'NIH'],
        help='List of agency abbreviations to fetch'
    )
    parser.add_argument(
        '--keywords',
        nargs='+',
        default=['UAP', 'unidentified', 'anomalous', 'sensor', 'detection', 
                 'aerospace', 'quantum', 'metamaterial', 'hypersonic', 'plasma'],
        help='Keywords to search for'
    )
    parser.add_argument(
        '--phases',
        nargs='+',
        default=['I', 'II'],
        help='SBIR phases to include (I, II, III)'
    )
    parser.add_argument(
        '--year_from',
        type=int,
        default=2019,
        help='Start year for awards'
    )
    parser.add_argument(
        '--year_to',
        type=int,
        default=None,
        help='End year for awards (default: current year)'
    )
    parser.add_argument(
        '--pages',
        type=int,
        default=3,
        help='Number of pages to fetch per query'
    )
    parser.add_argument(
        '--page_size',
        type=int,
        default=50,
        help='Results per page'
    )
    parser.add_argument(
        '--out_dir',
        default='external/sbir_data',
        help='Output directory for fetched data'
    )
    parser.add_argument(
        '--use_alt_endpoint',
        action='store_true',
        help='Use alternative awards endpoint'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests (seconds) to respect rate limits'
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    ensure_dir(args.out_dir)
    
    # Initialize manifest
    manifest = {
        'generated': datetime.datetime.utcnow().isoformat(),
        'parameters': {
            'agencies': args.agencies,
            'keywords': args.keywords,
            'phases': args.phases,
            'year_from': args.year_from,
            'year_to': args.year_to,
            'pages': args.pages,
            'page_size': args.page_size
        },
        'runs': []
    }
    
    total_results = 0
    
    print("🚀 SBIR/STTR Multi-Agency Data Fetcher")
    print("=" * 60)
    print(f"Agencies: {', '.join(args.agencies)}")
    print(f"Keywords: {', '.join(args.keywords)}")
    print(f"Phases: {', '.join(args.phases)}")
    print(f"Year range: {args.year_from} - {args.year_to or 'current'}")
    print("=" * 60)
    
    # Fetch data for each combination
    for agency in args.agencies:
        for keyword in args.keywords:
            for phase in args.phases:
                print(f"\n📡 Fetching {agency} / {keyword} / Phase {phase}...")
                
                for page in range(1, args.pages + 1):
                    print(f"  Page {page}/{args.pages}...", end=" ")
                    
                    # Choose endpoint
                    if args.use_alt_endpoint:
                        data = fetch_sbir_awards_alt_endpoint(
                            agency=agency,
                            keyword=keyword,
                            phase=phase,
                            year_from=args.year_from,
                            page=page,
                            page_size=args.page_size
                        )
                    else:
                        data = fetch_sbir_awards(
                            agency=agency,
                            keyword=keyword,
                            phase=phase,
                            year_from=args.year_from,
                            year_to=args.year_to,
                            page=page,
                            page_size=args.page_size
                        )
                    
                    # Save to file
                    filename = f"{agency}_{keyword.replace(' ', '_')}_Phase{phase}_p{page}.json"
                    filepath = os.path.join(args.out_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    
                    # Track results
                    result_count = len(data.get('results', []))
                    total_results += result_count
                    
                    manifest['runs'].append({
                        'agency': agency,
                        'keyword': keyword,
                        'phase': phase,
                        'page': page,
                        'file': filepath,
                        'count': result_count,
                        'has_error': 'error' in data
                    })
                    
                    print(f"✓ {result_count} results")
                    
                    # Respect rate limits
                    time.sleep(args.delay)
    
    # Save manifest
    manifest_path = os.path.join(args.out_dir, '_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Fetch Complete!")
    print("=" * 60)
    print(f"Total results fetched: {total_results}")
    print(f"Total files created: {len(manifest['runs'])}")
    print(f"Output directory: {args.out_dir}")
    print(f"Manifest: {manifest_path}")
    
    # Summary by agency
    print("\n📊 Results by Agency:")
    agency_counts = {}
    for run in manifest['runs']:
        agency = run['agency']
        agency_counts[agency] = agency_counts.get(agency, 0) + run['count']
    
    for agency, count in sorted(agency_counts.items()):
        print(f"  {agency}: {count} awards")
    
    # Note about next steps
    print("\n📋 Next Steps:")
    print("  1. Review fetched data in:", args.out_dir)
    print("  2. Create normalizer script to convert to standard format")
    print("  3. Map awards to entities in entities_master.csv")
    print("  4. Add to awards_master.csv and money_flows.csv")


if __name__ == '__main__':
    main()

