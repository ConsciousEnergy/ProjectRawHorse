# Manual Data Verification & Review Queue System

**Date:** December 1, 2025  
**Feature:** Script-based review queue for manual data verification  
**Status:** ✅ Complete

---

## Overview

Implemented a lightweight, script-based review queue system for manually verifying auto-fetched data before integration into the main database. Provides workflow for adding items to queue, reviewing them, and exporting approved data.

---

## Components

### 1. Review Queue Manager (`data/scripts/create_review_queue.py`)

**Purpose:** Add data items to review queue

**Commands:**

#### Add Items to Queue
```bash
python create_review_queue.py add \
  --data_type entity \
  --data_file ../contractors/top_contractors.csv \
  --reason "auto-fetch-usaspending" \
  --max_items 50
```

#### List Pending Reviews
```bash
python create_review_queue.py list \
  --data_type entity
```

**Features:**
- Generates unique review IDs
- Prevents duplicate additions
- Stores full item data for review
- Timestamps all additions
- Supports entity, award, and money_flow types

---

### 2. Review Queue Processor (`data/scripts/review_queue_items.py`)

**Purpose:** Review and approve/reject queued items

**Commands:**

#### Review Single Item
```bash
python review_queue_items.py review \
  --review_id abc123def456 \
  --decision approve \
  --notes "Verified via SAM.gov" \
  --reviewer john_doe
```

#### Batch Approve
```bash
python review_queue_items.py batch \
  --decision approve \
  --data_type entity \
  --max_items 20 \
  --reviewer admin
```

#### Export Approved Items
```bash
python review_queue_items.py export \
  --output_dir ../review/approved
```

#### Show Statistics
```bash
python review_queue_items.py stats
```

**Features:**
- Single-item and batch review
- Approve/reject/edit decisions
- Reviewer attribution and timestamps
- Export approved items to CSV
- Queue statistics dashboard

---

## Review Queue Schema

**File:** `data/review/review_queue.csv`

**Columns:**
- `review_id`: Unique identifier (MD5 hash)
- `data_type`: entity, award, or money_flow
- `item_id`: Entity ID, award PIID, or flow edge ID
- `status`: pending or reviewed
- `reason`: Why item needs review (auto-fetch, duplicate, anomaly, etc.)
- `data_json`: Full item data as string
- `reviewer`: Name of person who reviewed
- `reviewed_date`: ISO timestamp of review
- `decision`: approve, reject, or edit
- `notes`: Review notes
- `added_date`: ISO timestamp when added to queue

---

## Workflow

### End-to-End Example: Contractor Verification

#### Step 1: Fetch Contractors
```bash
cd data/scripts

# Fetch USASpending data
python fetch_usaspending_multiagency.py \
  --keywords_file ../reference/keywords_expanded_contractors.txt \
  --agencies_json ../reference/agencies_contractor_expansion.json \
  --out_dir ../external/contractors_expansion

# Aggregate top recipients
python aggregate_top_recipients.py \
  --data_dir ../external/contractors_expansion \
  --output ../contractors/top_contractors_2025.csv \
  --top_n 100
```

#### Step 2: Add to Review Queue
```bash
# Add top 50 contractors for manual review
python create_review_queue.py add \
  --data_type entity \
  --data_file ../contractors/top_contractors_2025.csv \
  --reason "usaspending-auto-fetch" \
  --max_items 50
```

**Output:**
```
✅ Added 50 items to review queue
   Data type: entity
   Reason: usaspending-auto-fetch
   Queue file: data/review/review_queue.csv
```

#### Step 3: List Pending Reviews
```bash
python create_review_queue.py list
```

**Output:**
```
==================================================================
PENDING REVIEWS: 50
==================================================================

1. [entity] LOCKHEED MARTIN CORPORATION
   Review ID: a1b2c3d4e5f6
   Reason: usaspending-auto-fetch
   Added: 2025-12-01T10:30:00

2. [entity] RAYTHEON TECHNOLOGIES CORPORATION
   Review ID: f6e5d4c3b2a1
   Reason: usaspending-auto-fetch
   Added: 2025-12-01T10:30:01

...
```

#### Step 4: Review Items

**Option A: Manual Review (One by One)**
```bash
# Review and approve
python review_queue_items.py review \
  --review_id a1b2c3d4e5f6 \
  --decision approve \
  --notes "Verified major defense contractor, relevant to UAP research" \
  --reviewer jane_smith

# Review and reject
python review_queue_items.py review \
  --review_id f6e5d4c3b2a1 \
  --decision reject \
  --notes "Not relevant to UAP/aerospace focus" \
  --reviewer jane_smith
```

**Option B: Batch Approval**
```bash
# Approve all pending entities (up to 20)
python review_queue_items.py batch \
  --decision approve \
  --data_type entity \
  --max_items 20 \
  --reviewer admin
```

#### Step 5: Check Statistics
```bash
python review_queue_items.py stats
```

**Output:**
```
============================================================
REVIEW QUEUE STATISTICS
============================================================
Total items: 50
Pending: 10
Reviewed: 40
  ├─ Approved: 35
  └─ Rejected: 5

By Type:
  entity_pending: 10
  entity_reviewed: 40
============================================================
```

#### Step 6: Export Approved Items
```bash
python review_queue_items.py export \
  --output_dir ../review/approved
```

**Output:**
```
✅ Exported 35 entity(s) to data/review/approved/approved_entitys.csv
```

#### Step 7: Migrate to Database
```bash
# Use approved entities for migration
python migrate_contractors_to_entities.py \
  --contractors_csv ../review/approved/approved_entitys.csv \
  --entities_master ../entities/entities_master.csv \
  --max_contractors 35
```

---

## Use Cases

### 1. Auto-Fetched Data Verification

**Scenario:** USASpending API returns 100 contractors, need manual review before adding

**Workflow:**
1. Fetch → Aggregate → Add to queue
2. Review each for relevance
3. Approve relevant, reject irrelevant
4. Export approved
5. Migrate to database

**Reason Tags:**
- `usaspending-auto-fetch`
- `nsf-auto-fetch`
- `sbir-auto-fetch`

---

### 2. Duplicate Detection Review

**Scenario:** Deduplication script flags potential duplicates

**Workflow:**
1. Run `detect_entity_duplicates.py`
2. Add flagged pairs to review queue
3. Manual review to confirm or reject duplicate
4. Merge confirmed duplicates with `merge_entities.py`

**Reason Tags:**
- `duplicate-candidate`
- `fuzzy-match-80`
- `identifier-mismatch`

---

### 3. Anomaly Review

**Scenario:** Pattern detection flags unusual transactions

**Workflow:**
1. Run pattern detection endpoints
2. Add anomalies to review queue
3. Investigate context
4. Approve legitimate, reject errors

**Reason Tags:**
- `spending-spike-detected`
- `award-clustering`
- `unusual-amount`

---

### 4. Manual Contribution Triage

**Scenario:** Community members submit data via contribution form

**Workflow:**
1. Contribution endpoint adds to review queue automatically
2. Admin reviews for quality and relevance
3. Approve good contributions
4. Reject spam or low-quality

**Reason Tags:**
- `community-contribution`
- `foia-submission`
- `crowdsourced`

---

## Integration Points

### With USASpending Fetcher

Add this to `aggregate_top_recipients.py`:
```python
# After creating CSV, optionally add to review queue
if args.add_to_review:
    import subprocess
    subprocess.run([
        'python', 'create_review_queue.py', 'add',
        '--data_type', 'entity',
        '--data_file', args.output,
        '--reason', 'usaspending-auto-fetch',
        '--max_items', str(args.top_n)
    ])
```

### With Deduplication Detector

Add this to `detect_entity_duplicates.py`:
```python
# After detecting duplicates, add to queue
for pair in duplicate_pairs:
    subprocess.run([
        'python', 'create_review_queue.py', 'add',
        '--data_type', 'entity',
        '--data_file', 'temp_duplicate_pair.csv',
        '--reason', f'duplicate-candidate-score-{pair.score}'
    ])
```

### With Pattern Detector

Create new endpoint that adds anomalies to queue:
```python
@router.post("/patterns/add-to-review")
async def add_patterns_to_review(
    entity: str,
    pattern_type: str,
    db: Session = Depends(get_db)
):
    """Add detected patterns to review queue"""
    # Run pattern detection
    # Write results to temp CSV
    # Call create_review_queue script
    # Return success
```

---

## Future Enhancements

### Web UI (Future v2)

**Admin Review Dashboard:**
- View pending reviews in web interface
- One-click approve/reject buttons
- Side-by-side comparison for duplicates
- Bulk actions
- Search and filter

**Technology Stack:**
- React frontend with admin route
- FastAPI endpoints for queue CRUD
- Database table instead of CSV

**Sample UI:**
```tsx
<ReviewQueue>
  <ReviewItem>
    <EntityCard data={item.data_json} />
    <ReviewActions>
      <Button onClick={approve}>✓ Approve</Button>
      <Button onClick={reject}>✗ Reject</Button>
      <Button onClick={edit}>✏ Edit</Button>
    </ReviewActions>
    <NotesField />
  </ReviewItem>
</ReviewQueue>
```

### Database-Backed Queue

**Migration to SQLite:**
```sql
CREATE TABLE review_queue (
    review_id TEXT PRIMARY KEY,
    data_type TEXT NOT NULL,
    item_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    reason TEXT,
    data_json TEXT,
    reviewer TEXT,
    reviewed_date TEXT,
    decision TEXT,
    notes TEXT,
    added_date TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Notifications

- Email notifications when items added to queue
- Slack integration for team collaboration
- Weekly summary reports

### Analytics

- Review velocity (items/day)
- Approval/rejection rates
- Most common rejection reasons
- Reviewer performance metrics

---

## Best Practices

### Review Guidelines

**Entities:**
- ✓ Relevant to UAP/aerospace research
- ✓ Legitimate organization (verify website)
- ✓ No obvious data errors
- ✗ Generic/unrelated companies
- ✗ Duplicate of existing entity

**Awards:**
- ✓ Description matches keywords
- ✓ Amount is reasonable
- ✓ Agency and recipient make sense
- ✗ Clearly off-topic
- ✗ Duplicate PIID

**Money Flows:**
- ✓ Source and target are correct
- ✓ Amount is reasonable
- ✓ Relationship is appropriate
- ✗ Circular or illogical flows
- ✗ Duplicate edges

### Batch vs. Individual Review

**Use Batch Approval When:**
- High confidence in data source
- Similar items from same fetch
- Time constraints
- Low-risk additions

**Use Individual Review When:**
- First time with data source
- High-stakes data (core entities)
- Potential duplicates
- Anomalies or outliers

---

## Success Metrics

✅ **Completed:**
- Review queue manager script
- Review processor script
- CSV-based queue storage
- Add, list, review, batch, export, stats commands
- Documentation complete

📊 **Capabilities:**
- Queue management for all data types
- Single and batch review modes
- Approve/reject/edit decisions
- Export approved items
- Statistics dashboard

🎯 **Quality:**
- Prevents automatic addition of unverified data
- Maintains audit trail (reviewer, timestamps)
- Supports iterative review process

---

## Conclusion

The manual data verification and review queue system provides a lightweight, script-based workflow for ensuring data quality before integration into the main database. While currently file-based, the system is designed for future enhancement with a web UI and database backend.

**Status:** ✅ Production-Ready (Script-Based)

**Next Steps:** Web UI for admin review dashboard (future enhancement)

