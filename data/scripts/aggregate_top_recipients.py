"""
Aggregate top recipients from USASpending API results
Identifies top contractors by total funding amount
"""
import os
import json
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple
import csv


def parse_usaspending_json(file_path: str) -> List[Dict]:
    """Parse a single USASpending JSON file and extract award data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('results', [])
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {file_path}: {e}")
        return []


def aggregate_recipients(data_dir: str) -> Dict[str, Dict]:
    """
    Aggregate all recipients from USASpending data
    
    Returns dictionary mapping UEI -> {name, duns, total_amount, award_count, agencies}
    """
    recipients = defaultdict(lambda: {
        'name': '',
        'uei': '',
        'duns': '',
        'total_amount': 0.0,
        'award_count': 0,
        'agencies': set(),
        'first_seen': None,
        'last_seen': None
    })
    
    # Walk through all JSON files in directory
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            if not filename.endswith('.json') or filename.startswith('_'):
                continue
            
            file_path = os.path.join(root, filename)
            awards = parse_usaspending_json(file_path)
            
            for award in awards:
                # Extract recipient information
                recipient_name = award.get('Recipient Name', '').strip()
                recipient_uei = award.get('Recipient UEI', '').strip()
                recipient_duns = award.get('Recipient DUNS', '').strip()
                
                # Skip if no identifier
                if not recipient_uei and not recipient_duns:
                    continue
                
                # Use UEI as primary key, fall back to DUNS
                key = recipient_uei or recipient_duns
                
                # Extract amount
                award_amount_str = award.get('Award Amount', '0')
                try:
                    # Remove dollar signs and commas
                    if isinstance(award_amount_str, str):
                        award_amount = float(award_amount_str.replace('$', '').replace(',', ''))
                    else:
                        award_amount = float(award_amount_str)
                except (ValueError, TypeError):
                    award_amount = 0.0
                
                # Extract dates
                action_date = award.get('Action Date', '')
                
                # Extract agency
                awarding_agency = award.get('Awarding Agency', '').strip()
                funding_agency = award.get('Funding Agency', '').strip()
                
                # Update recipient record
                recipient = recipients[key]
                if not recipient['name'] and recipient_name:
                    recipient['name'] = recipient_name
                if not recipient['uei'] and recipient_uei:
                    recipient['uei'] = recipient_uei
                if not recipient['duns'] and recipient_duns:
                    recipient['duns'] = recipient_duns
                
                recipient['total_amount'] += award_amount
                recipient['award_count'] += 1
                
                if awarding_agency:
                    recipient['agencies'].add(awarding_agency)
                if funding_agency and funding_agency != awarding_agency:
                    recipient['agencies'].add(funding_agency)
                
                # Track date range
                if action_date:
                    if not recipient['first_seen'] or action_date < recipient['first_seen']:
                        recipient['first_seen'] = action_date
                    if not recipient['last_seen'] or action_date > recipient['last_seen']:
                        recipient['last_seen'] = action_date
    
    # Convert sets to lists for JSON serialization
    for key, recipient in recipients.items():
        recipient['agencies'] = sorted(list(recipient['agencies']))
    
    return dict(recipients)


def rank_recipients(recipients: Dict[str, Dict], top_n: int = 50) -> List[Tuple[str, Dict]]:
    """Rank recipients by total funding amount"""
    ranked = sorted(recipients.items(), key=lambda x: x[1]['total_amount'], reverse=True)
    return ranked[:top_n]


def main():
    parser = argparse.ArgumentParser(description='Aggregate top recipients from USASpending data')
    parser.add_argument('--data_dir', required=True, help='Directory containing USASpending JSON files')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--top_n', type=int, default=50, help='Number of top recipients to output')
    parser.add_argument('--min_amount', type=float, default=0, help='Minimum total amount threshold')
    
    args = parser.parse_args()
    
    print(f"Aggregating recipients from {args.data_dir}...")
    recipients = aggregate_recipients(args.data_dir)
    print(f"Found {len(recipients)} unique recipients")
    
    print(f"Ranking top {args.top_n} by total funding...")
    ranked = rank_recipients(recipients, args.top_n)
    
    # Filter by minimum amount
    if args.min_amount > 0:
        ranked = [(key, data) for key, data in ranked if data['total_amount'] >= args.min_amount]
        print(f"After filtering by min_amount={args.min_amount}: {len(ranked)} recipients")
    
    # Write to CSV
    print(f"Writing output to {args.output}...")
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['rank', 'recipient_name', 'uei', 'duns', 'total_amount', 'award_count', 'agencies', 'first_seen', 'last_seen']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for rank, (key, data) in enumerate(ranked, 1):
            writer.writerow({
                'rank': rank,
                'recipient_name': data['name'],
                'uei': data['uei'],
                'duns': data['duns'],
                'total_amount': data['total_amount'],
                'award_count': data['award_count'],
                'agencies': '; '.join(data['agencies']),
                'first_seen': data['first_seen'] or '',
                'last_seen': data['last_seen'] or ''
            })
    
    # Print summary
    print("\n=== Top 10 Recipients ===")
    for rank, (key, data) in enumerate(ranked[:10], 1):
        print(f"{rank}. {data['name']}")
        print(f"   Total: ${data['total_amount']:,.2f} ({data['award_count']} awards)")
        print(f"   Agencies: {', '.join(data['agencies'][:3])}")
        print()
    
    print(f"Complete! {len(ranked)} recipients written to {args.output}")


if __name__ == "__main__":
    main()

