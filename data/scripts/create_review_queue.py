"""
Create and manage data review queue for manual verification
"""
import os
import csv
import hashlib
import argparse
from datetime import datetime
from typing import List, Dict


def generate_review_id(data_type: str, item_id: str) -> str:
    """Generate unique review ID"""
    combined = f"{data_type}_{item_id}_{datetime.now().isoformat()}"
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def add_to_review_queue(
    data_type: str,
    data_file: str,
    queue_file: str,
    reason: str = "auto-fetch",
    max_items: int = None
):
    """
    Add items from data file to review queue
    
    Args:
        data_type: Type of data (entity, award, money_flow)
        data_file: Path to CSV with data to review
        queue_file: Path to review_queue.csv
        reason: Reason for review (auto-fetch, duplicate, anomaly, etc.)
        max_items: Maximum items to add
    """
    # Load existing queue
    existing_reviews = set()
    if os.path.exists(queue_file):
        with open(queue_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_reviews = {row['item_id'] for row in reader if row.get('item_id')}
    
    # Read data file
    new_reviews = []
    added_count = 0
    
    with open(data_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if max_items and added_count >= max_items:
                break
            
            # Generate item_id based on data type
            if data_type == 'entity':
                item_id = row.get('entity_id', row.get('display_name', ''))
            elif data_type == 'award':
                item_id = row.get('piid', row.get('id', ''))
            elif data_type == 'money_flow':
                item_id = row.get('edge_id', f"{row.get('source', '')}_{row.get('target', '')}")
            else:
                item_id = str(added_count)
            
            # Skip if already in queue
            if item_id in existing_reviews:
                continue
            
            review_id = generate_review_id(data_type, item_id)
            
            new_reviews.append({
                'review_id': review_id,
                'data_type': data_type,
                'item_id': item_id,
                'status': 'pending',
                'reason': reason,
                'data_json': str(row),  # Store full row as JSON-like string
                'reviewer': '',
                'reviewed_date': '',
                'decision': '',
                'notes': '',
                'added_date': datetime.now().isoformat()
            })
            
            added_count += 1
    
    # Append to queue file
    write_header = not os.path.exists(queue_file)
    
    with open(queue_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['review_id', 'data_type', 'item_id', 'status', 'reason', 
                     'data_json', 'reviewer', 'reviewed_date', 'decision', 'notes', 'added_date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if write_header:
            writer.writeheader()
        
        for review in new_reviews:
            writer.writerow(review)
    
    print(f"✅ Added {added_count} items to review queue")
    print(f"   Data type: {data_type}")
    print(f"   Reason: {reason}")
    print(f"   Queue file: {queue_file}")


def list_pending_reviews(queue_file: str, data_type: str = None):
    """
    List all pending reviews
    """
    if not os.path.exists(queue_file):
        print("No review queue found")
        return
    
    with open(queue_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        pending = [row for row in reader if row['status'] == 'pending']
        
        if data_type:
            pending = [row for row in pending if row['data_type'] == data_type]
    
    if not pending:
        print("No pending reviews")
        return
    
    print(f"\n{'='*80}")
    print(f"PENDING REVIEWS: {len(pending)}")
    print(f"{'='*80}\n")
    
    for i, review in enumerate(pending[:20], 1):  # Show first 20
        print(f"{i}. [{review['data_type']}] {review['item_id']}")
        print(f"   Review ID: {review['review_id']}")
        print(f"   Reason: {review['reason']}")
        print(f"   Added: {review['added_date']}")
        print()
    
    if len(pending) > 20:
        print(f"... and {len(pending) - 20} more")


def main():
    parser = argparse.ArgumentParser(description='Manage data review queue')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add items to review queue')
    add_parser.add_argument('--data_type', required=True, choices=['entity', 'award', 'money_flow'])
    add_parser.add_argument('--data_file', required=True, help='CSV file with data to review')
    add_parser.add_argument('--queue_file', default='data/review/review_queue.csv')
    add_parser.add_argument('--reason', default='auto-fetch', help='Reason for review')
    add_parser.add_argument('--max_items', type=int, help='Max items to add')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List pending reviews')
    list_parser.add_argument('--queue_file', default='data/review/review_queue.csv')
    list_parser.add_argument('--data_type', choices=['entity', 'award', 'money_flow'], help='Filter by type')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        # Ensure review directory exists
        os.makedirs(os.path.dirname(args.queue_file), exist_ok=True)
        
        add_to_review_queue(
            args.data_type,
            args.data_file,
            args.queue_file,
            args.reason,
            args.max_items
        )
    
    elif args.command == 'list':
        list_pending_reviews(args.queue_file, args.data_type)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

