"""
Normalize SBIR/STTR award data into standard CSV format.

Processes JSON files fetched by fetch_sbir_multiagency.py and converts them
into the awards_master.csv and money_flows.csv format.

Usage:
    python data/scripts/normalize_sbir_multiagency.py --in_dir external/sbir_data --out_csv processed/awards_sbir.csv
"""

import os
import json
import csv
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def generate_entity_id(name: str) -> str:
    """Generate consistent entity_id hash from name."""
    return hashlib.md5(name.encode('utf-8')).hexdigest()[:16]


def parse_sbir_award(award_data: Dict) -> Optional[Dict]:
    """
    Parse SBIR award JSON into normalized format.
    
    Expected fields from SBIR.gov API:
    - agency
    - awardNumber / award_number
    - awardee / company
    - principalInvestigator / pi_name
    - phase
    - awardAmount / award_amount
    - awardYear / award_year
    - projectTitle / title
    - abstract
    - keywords
    """
    try:
        # Handle different field naming conventions
        award_id = (
            award_data.get('awardNumber') or 
            award_data.get('award_number') or
            award_data.get('award_id') or
            ''
        )
        
        company = (
            award_data.get('awardee') or
            award_data.get('company') or
            award_data.get('recipient_name') or
            ''
        )
        
        agency = (
            award_data.get('agency') or
            award_data.get('awarding_agency') or
            ''
        )
        
        amount = award_data.get('awardAmount') or award_data.get('award_amount') or 0
        
        # Convert amount to float if it's a string
        if isinstance(amount, str):
            amount = float(amount.replace('$', '').replace(',', '').strip() or 0)
        
        year = award_data.get('awardYear') or award_data.get('award_year') or ''
        phase = award_data.get('phase') or ''
        
        title = (
            award_data.get('projectTitle') or
            award_data.get('title') or
            award_data.get('description') or
            ''
        )
        
        abstract = award_data.get('abstract') or ''
        
        # Create description combining title and abstract
        description = title
        if abstract and len(abstract) > 0:
            description = f"{title}. {abstract[:200]}..."  # Limit abstract length
        
        # Construct action date from year
        action_date = ''
        if year:
            try:
                action_date = f"{year}-01-01"
            except:
                pass
        
        # Generate unique ID if not present
        if not award_id:
            award_id = f"SBIR-{generate_entity_id(f'{company}{title}{year}')}"
        
        return {
            'award_uid': award_id,
            'piid': award_id,
            'mod_number': '',
            'fain': '',
            'uri': '',
            'award_type': f'SBIR/STTR Phase {phase}' if phase else 'SBIR/STTR',
            'action_date': action_date,
            'current_total_value': amount,
            'description': description,
            'funding_agency': agency,
            'awarding_agency': agency,
            'recipient_uei': '',
            'recipient_duns': '',
            'recipient_cage': '',
            'recipient_name': company,
            'source_file': 'sbir_multiagency',
            'action_date_std': action_date,
            'current_total_value_std': amount,
            'kw_hits': 0,
            'kw_top3': '',
            'entity_id': generate_entity_id(company),
            'credibility_score': 0.8  # SBIR awards are highly credible
        }
    
    except Exception as e:
        print(f"Error parsing award: {e}")
        return None


def normalize_sbir_files(input_dir: str, output_csv: str):
    """
    Process all SBIR JSON files in directory and output normalized CSV.
    
    Args:
        input_dir: Directory containing fetched JSON files
        output_csv: Path to output CSV file
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        return
    
    # Find all JSON files (exclude manifest)
    json_files = [f for f in input_path.glob('*.json') if not f.name.startswith('_')]
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return
    
    print("🔄 SBIR Data Normalizer")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output CSV: {output_csv}")
    print(f"Files to process: {len(json_files)}")
    print("=" * 60)
    
    all_awards = []
    awards_seen = set()  # Track unique awards to avoid duplicates
    
    for json_file in json_files:
        print(f"\nProcessing {json_file.name}...", end=" ")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different response structures
            results = data.get('results', [])
            if not results and isinstance(data, list):
                results = data
            
            file_awards = 0
            for award_data in results:
                normalized = parse_sbir_award(award_data)
                
                if normalized:
                    # Check for duplicates using award_uid
                    award_key = (normalized['award_uid'], normalized['recipient_name'])
                    if award_key not in awards_seen:
                        all_awards.append(normalized)
                        awards_seen.add(award_key)
                        file_awards += 1
            
            print(f"✓ {file_awards} awards")
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Write to CSV
    if all_awards:
        print(f"\n📝 Writing {len(all_awards)} awards to CSV...")
        
        # Ensure output directory exists
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns (matching awards_master.csv format)
        fieldnames = [
            'award_uid', 'piid', 'mod_number', 'fain', 'uri', 'award_type',
            'action_date', 'current_total_value', 'description', 'funding_agency',
            'awarding_agency', 'recipient_uei', 'recipient_duns', 'recipient_cage',
            'recipient_name', 'source_file', 'action_date_std', 'current_total_value_std',
            'kw_hits', 'kw_top3', 'entity_id', 'credibility_score'
        ]
        
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_awards)
        
        print(f"✓ CSV written successfully: {output_csv}")
    else:
        print("\n⚠️  No awards to write (all files empty or invalid)")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("✅ Normalization Complete!")
    print("=" * 60)
    print(f"Total awards normalized: {len(all_awards)}")
    print(f"Unique recipients: {len(set(a['recipient_name'] for a in all_awards))}")
    print(f"Unique agencies: {len(set(a['funding_agency'] for a in all_awards))}")
    
    # Award value summary
    total_value = sum(a['current_total_value'] for a in all_awards)
    avg_value = total_value / len(all_awards) if all_awards else 0
    print(f"\nTotal award value: ${total_value:,.2f}")
    print(f"Average award value: ${avg_value:,.2f}")
    
    # Top recipients
    recipient_totals = {}
    for award in all_awards:
        recipient = award['recipient_name']
        recipient_totals[recipient] = recipient_totals.get(recipient, 0) + award['current_total_value']
    
    top_recipients = sorted(recipient_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("\n📊 Top 10 Recipients by Total Award Value:")
    for i, (recipient, total) in enumerate(top_recipients, 1):
        print(f"  {i}. {recipient}: ${total:,.2f}")
    
    print("\n📋 Next Steps:")
    print("  1. Review normalized CSV for data quality")
    print("  2. Merge with awards_master.csv")
    print("  3. Create money_flows entries for agency → recipient")
    print("  4. Add recipient entities to entities_master.csv if missing")


def main():
    parser = argparse.ArgumentParser(
        description='Normalize SBIR/STTR award JSON data to CSV format'
    )
    parser.add_argument(
        '--in_dir',
        default='external/sbir_data',
        help='Input directory containing SBIR JSON files'
    )
    parser.add_argument(
        '--out_csv',
        default='processed/awards_sbir.csv',
        help='Output CSV file path'
    )
    
    args = parser.parse_args()
    
    normalize_sbir_files(args.in_dir, args.out_csv)


if __name__ == '__main__':
    main()

