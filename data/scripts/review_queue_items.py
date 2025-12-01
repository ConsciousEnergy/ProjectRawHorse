"""
Review and approve/reject items in the review queue
"""
import os
import csv
import argparse
from datetime import datetime
import ast


def review_item(queue_file: str, review_id: str, decision: str, notes: str = "", reviewer: str = "admin"):
    """
    Mark an item as reviewed
    
    Args:
        queue_file: Path to review_queue.csv
        review_id: ID of review to process
        decision: approve, reject, or edit
        notes: Review notes
        reviewer: Reviewer name
    """
    if not os.path.exists(queue_file):
        print(f"Queue file not found: {queue_file}")
        return False
    
    # Read all reviews
    reviews = []
    found = False
    
    with open(queue_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['review_id'] == review_id:
                row['status'] = 'reviewed'
                row['decision'] = decision
                row['notes'] = notes
                row['reviewer'] = reviewer
                row['reviewed_date'] = datetime.now().isoformat()
                found = True
                print(f"\n✅ Reviewed: {row['data_type']} - {row['item_id']}")
                print(f"   Decision: {decision}")
                if notes:
                    print(f"   Notes: {notes}")
            reviews.append(row)
    
    if not found:
        print(f"Review ID not found: {review_id}")
        return False
    
    # Write back
    with open(queue_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['review_id', 'data_type', 'item_id', 'status', 'reason', 
                     'data_json', 'reviewer', 'reviewed_date', 'decision', 'notes', 'added_date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)
    
    return True


def batch_review(queue_file: str, decision: str, data_type: str = None, max_items: int = 10, reviewer: str = "admin"):
    """
    Batch review multiple pending items
    """
    if not os.path.exists(queue_file):
        print(f"Queue file not found: {queue_file}")
        return
    
    # Read pending reviews
    with open(queue_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        pending = [row for row in reader if row['status'] == 'pending']
        
        if data_type:
            pending = [row for row in pending if row['data_type'] == data_type]
    
    if not pending:
        print("No pending reviews")
        return
    
    # Review up to max_items
    reviewed_count = 0
    for review in pending[:max_items]:
        review_item(queue_file, review['review_id'], decision, f"Batch {decision}", reviewer)
        reviewed_count += 1
    
    print(f"\n✅ Batch reviewed {reviewed_count} items with decision: {decision}")


def export_approved(queue_file: str, output_dir: str):
    """
    Export approved items back to their respective data files
    """
    if not os.path.exists(queue_file):
        print(f"Queue file not found: {queue_file}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Read approved reviews
    with open(queue_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        approved = [row for row in reader if row['decision'] == 'approve']
    
    if not approved:
        print("No approved items to export")
        return
    
    # Group by data_type
    by_type = {}
    for review in approved:
        data_type = review['data_type']
        if data_type not in by_type:
            by_type[data_type] = []
        
        # Parse data_json back to dict
        try:
            data = ast.literal_eval(review['data_json'])
            by_type[data_type].append(data)
        except:
            print(f"Warning: Could not parse data for {review['review_id']}")
    
    # Write to files
    for data_type, items in by_type.items():
        output_file = os.path.join(output_dir, f"approved_{data_type}s.csv")
        
        if items:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
            
            print(f"✅ Exported {len(items)} {data_type}(s) to {output_file}")


def show_statistics(queue_file: str):
    """
    Show review queue statistics
    """
    if not os.path.exists(queue_file):
        print(f"Queue file not found: {queue_file}")
        return
    
    with open(queue_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reviews = list(reader)
    
    if not reviews:
        print("Queue is empty")
        return
    
    # Calculate stats
    total = len(reviews)
    pending = len([r for r in reviews if r['status'] == 'pending'])
    reviewed = len([r for r in reviews if r['status'] == 'reviewed'])
    approved = len([r for r in reviews if r['decision'] == 'approve'])
    rejected = len([r for r in reviews if r['decision'] == 'reject'])
    
    # By type
    by_type = {}
    for review in reviews:
        data_type = review['data_type']
        status = review['status']
        key = f"{data_type}_{status}"
        by_type[key] = by_type.get(key, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"REVIEW QUEUE STATISTICS")
    print(f"{'='*60}")
    print(f"Total items: {total}")
    print(f"Pending: {pending}")
    print(f"Reviewed: {reviewed}")
    print(f"  ├─ Approved: {approved}")
    print(f"  └─ Rejected: {rejected}")
    print(f"\nBy Type:")
    for key, count in sorted(by_type.items()):
        print(f"  {key}: {count}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Review queue items')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Review command
    review_parser = subparsers.add_parser('review', help='Review a single item')
    review_parser.add_argument('--queue_file', default='data/review/review_queue.csv')
    review_parser.add_argument('--review_id', required=True, help='Review ID')
    review_parser.add_argument('--decision', required=True, choices=['approve', 'reject', 'edit'])
    review_parser.add_argument('--notes', default='', help='Review notes')
    review_parser.add_argument('--reviewer', default='admin', help='Reviewer name')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch review items')
    batch_parser.add_argument('--queue_file', default='data/review/review_queue.csv')
    batch_parser.add_argument('--decision', required=True, choices=['approve', 'reject'])
    batch_parser.add_argument('--data_type', choices=['entity', 'award', 'money_flow'])
    batch_parser.add_argument('--max_items', type=int, default=10)
    batch_parser.add_argument('--reviewer', default='admin')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export approved items')
    export_parser.add_argument('--queue_file', default='data/review/review_queue.csv')
    export_parser.add_argument('--output_dir', default='data/review/approved')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show queue statistics')
    stats_parser.add_argument('--queue_file', default='data/review/review_queue.csv')
    
    args = parser.parse_args()
    
    if args.command == 'review':
        review_item(args.queue_file, args.review_id, args.decision, args.notes, args.reviewer)
    
    elif args.command == 'batch':
        batch_review(args.queue_file, args.decision, args.data_type, args.max_items, args.reviewer)
    
    elif args.command == 'export':
        export_approved(args.queue_file, args.output_dir)
    
    elif args.command == 'stats':
        show_statistics(args.queue_file)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

