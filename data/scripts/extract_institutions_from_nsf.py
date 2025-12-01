"""
Extract and aggregate academic institutions from NSF awards data
"""
import os
import json
import csv
import argparse
from collections import defaultdict
from typing import Dict, List


def parse_nsf_awards(data_dir: str) -> Dict[str, Dict]:
    """
    Parse NSF awards JSON files and aggregate institutions
    
    Returns:
        Dictionary mapping institution name -> institution data
    """
    institutions = defaultdict(lambda: {
        'name': '',
        'city': '',
        'state': '',
        'zip': '',
        'country': 'US',
        'award_count': 0,
        'total_funding': 0.0,
        'pi_names': set(),
        'research_areas': set(),
        'first_award': None,
        'last_award': None
    })
    
    # Walk through all JSON files
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            if not filename.endswith('.json') or filename.startswith('_'):
                continue
            
            file_path = os.path.join(root, filename)
            print(f"Processing {filename}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    awards = json.load(f)
                
                # Handle both list and single award formats
                if not isinstance(awards, list):
                    awards = [awards]
                
                for award in awards:
                    # Extract institution info
                    awardee = award.get('awardee', {})
                    if not awardee:
                        continue
                    
                    inst_name = awardee.get('name', '').strip()
                    if not inst_name:
                        continue
                    
                    # Normalize institution name
                    inst_key = inst_name.lower()
                    
                    inst = institutions[inst_key]
                    
                    # Update institution info
                    if not inst['name']:
                        inst['name'] = inst_name
                        inst['city'] = awardee.get('city', '').strip()
                        inst['state'] = awardee.get('stateCode', '').strip()
                        inst['zip'] = awardee.get('zipCode', '').strip()
                        inst['country'] = awardee.get('countryCode', 'US').strip()
                    
                    # Aggregate awards
                    inst['award_count'] += 1
                    
                    # Extract funding amount
                    funds = award.get('fundsObligatedAmt', 0)
                    if isinstance(funds, str):
                        try:
                            funds = float(funds.replace(',', '').replace('$', ''))
                        except ValueError:
                            funds = 0.0
                    inst['total_funding'] += float(funds)
                    
                    # Track PI names
                    pi_first = award.get('piFirstName', '').strip()
                    pi_last = award.get('piLastName', '').strip()
                    if pi_first and pi_last:
                        inst['pi_names'].add(f"{pi_first} {pi_last}")
                    
                    # Track research areas (from title)
                    title = award.get('title', '').lower()
                    if 'quantum' in title:
                        inst['research_areas'].add('Quantum Physics')
                    if 'plasma' in title:
                        inst['research_areas'].add('Plasma Physics')
                    if 'aerospace' in title or 'aeronautics' in title:
                        inst['research_areas'].add('Aerospace')
                    if 'materials' in title:
                        inst['research_areas'].add('Materials Science')
                    if 'sensor' in title or 'sensing' in title:
                        inst['research_areas'].add('Sensor Technology')
                    if 'propulsion' in title:
                        inst['research_areas'].add('Propulsion')
                    
                    # Track date range
                    start_date = award.get('startDate', '')
                    if start_date:
                        if not inst['first_award'] or start_date < inst['first_award']:
                            inst['first_award'] = start_date
                        if not inst['last_award'] or start_date > inst['last_award']:
                            inst['last_award'] = start_date
            
            except (json.JSONDecodeError, Exception) as e:
                print(f"  Error processing {filename}: {e}")
                continue
    
    # Convert sets to lists for JSON serialization
    for inst in institutions.values():
        inst['pi_names'] = sorted(list(inst['pi_names']))
        inst['research_areas'] = sorted(list(inst['research_areas']))
    
    return dict(institutions)


def filter_institutions(
    institutions: Dict[str, Dict],
    min_awards: int = 2,
    min_funding: float = 100000,
    us_only: bool = True
) -> List[Dict]:
    """
    Filter institutions by criteria and return ranked list
    """
    filtered = []
    
    for inst_key, inst in institutions.items():
        # Apply filters
        if inst['award_count'] < min_awards:
            continue
        if inst['total_funding'] < min_funding:
            continue
        if us_only and inst['country'] != 'US':
            continue
        
        filtered.append(inst)
    
    # Sort by total funding
    filtered.sort(key=lambda x: x['total_funding'], reverse=True)
    
    return filtered


def main():
    parser = argparse.ArgumentParser(description='Extract institutions from NSF awards')
    parser.add_argument('--data_dir', required=True, help='Directory with NSF JSON files')
    parser.add_argument('--output', required=True, help='Output CSV file')
    parser.add_argument('--min_awards', type=int, default=2, help='Minimum award count')
    parser.add_argument('--min_funding', type=float, default=100000, help='Minimum total funding')
    parser.add_argument('--top_n', type=int, default=50, help='Number of institutions to output')
    
    args = parser.parse_args()
    
    print(f"Parsing NSF awards from {args.data_dir}...")
    institutions = parse_nsf_awards(args.data_dir)
    print(f"Found {len(institutions)} unique institutions")
    
    print(f"\nFiltering institutions (min_awards={args.min_awards}, min_funding=${args.min_funding:,.0f})...")
    filtered = filter_institutions(institutions, args.min_awards, args.min_funding)
    print(f"After filtering: {len(filtered)} institutions")
    
    # Limit to top N
    top_institutions = filtered[:args.top_n]
    print(f"Outputting top {len(top_institutions)} institutions")
    
    # Write to CSV
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'rank', 'name', 'city', 'state', 'zip', 'country',
            'award_count', 'total_funding', 'research_areas',
            'pi_count', 'first_award', 'last_award'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for rank, inst in enumerate(top_institutions, 1):
            writer.writerow({
                'rank': rank,
                'name': inst['name'],
                'city': inst['city'],
                'state': inst['state'],
                'zip': inst['zip'],
                'country': inst['country'],
                'award_count': inst['award_count'],
                'total_funding': inst['total_funding'],
                'research_areas': '; '.join(inst['research_areas']) if inst['research_areas'] else '',
                'pi_count': len(inst['pi_names']),
                'first_award': inst['first_award'] or '',
                'last_award': inst['last_award'] or ''
            })
    
    print(f"\n✅ Written to {args.output}")
    
    # Print top 10 summary
    print("\n=== Top 10 Institutions ===")
    for rank, inst in enumerate(top_institutions[:10], 1):
        print(f"{rank}. {inst['name']}")
        print(f"   Location: {inst['city']}, {inst['state']}")
        print(f"   Awards: {inst['award_count']}, Funding: ${inst['total_funding']:,.0f}")
        if inst['research_areas']:
            print(f"   Areas: {', '.join(inst['research_areas'][:3])}")
        print()


if __name__ == "__main__":
    main()

