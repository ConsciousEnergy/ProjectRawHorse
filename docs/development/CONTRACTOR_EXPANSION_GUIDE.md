# Defense Contractor Database Expansion Guide

**Date:** November 30, 2025  
**Feature:** USASpending API contractor discovery and integration  
**Status:** ✅ Ready to Execute

---

## Overview

This guide documents the process for expanding the Project RawHorse entity database with defense and aerospace contractors discovered through the USASpending.gov API.

---

## Implementation Components

### 1. Configuration Files

#### Keywords File (`data/reference/keywords_expanded_contractors.txt`)

Contains 20+ UAP/aerospace-relevant search terms:
- UAP, unidentified aerial phenomena
- Aerospace, hypersonic, metamaterials
- Sensor fusion, quantum sensing
- Propulsion research, space technology
- Defense electronics, avionics
- And more...

#### Agencies File (`data/reference/agencies_contractor_expansion.json`)

Expanded agency list for comprehensive contractor discovery:
- Department of Defense (all branches)
- Air Force, Army, Navy
- DARPA, IARPA
- NASA, ODNI
- DOE, NSF, DHS

### 2. Data Fetching Scripts

#### `fetch_usaspending_multiagency.py`

**Purpose:** Query USASpending.gov API for awards matching keywords and agencies

**Usage:**
```bash
cd data/scripts
python fetch_usaspending_multiagency.py \
  --keywords_file ../reference/keywords_expanded_contractors.txt \
  --agencies_json ../reference/agencies_contractor_expansion.json \
  --out_dir ../external/contractors_expansion \
  --min_action_date 2019-01-01 \
  --pages 5
```

**Parameters:**
- `--keywords_file`: Path to keywords file
- `--agencies_json`: Path to agencies configuration
- `--out_dir`: Output directory for JSON results
- `--min_action_date`: Start date for award search (default: 2019-01-01)
- `--pages`: Number of pages to fetch per keyword/agency pair (default: 2, max: 10)

**Output:**
- Individual JSON files for each agency-keyword-page combination
- `_manifest.json` with execution summary
- Example: `Department_of_Defense_UAP_p1.json`

**Rate Limiting:**
- 0.4 second delay between requests (automatic)
- Respects USASpending API rate limits

**Expected Runtime:**
- 11 agencies × 20 keywords × 5 pages = 1,100 API calls
- At 0.4s/call = ~7-10 minutes total

---

### 3. Data Aggregation Scripts

#### `aggregate_top_recipients.py`

**Purpose:** Aggregate and rank contractors by total funding

**Usage:**
```bash
python aggregate_top_recipients.py \
  --data_dir ../external/contractors_expansion \
  --output ../contractors/top_contractors.csv \
  --top_n 100 \
  --min_amount 1000000
```

**Parameters:**
- `--data_dir`: Directory containing USASpending JSON files
- `--output`: Output CSV file path
- `--top_n`: Number of top recipients to output (default: 50)
- `--min_amount`: Minimum total amount threshold (default: 0)

**Output CSV Columns:**
- `rank`: Ranking by total funding
- `recipient_name`: Contractor name
- `uei`: Unique Entity Identifier
- `duns`: DUNS number
- `total_amount`: Sum of all award amounts
- `award_count`: Number of awards
- `agencies`: Semicolon-separated list of awarding agencies
- `first_seen`: Earliest award date
- `last_seen`: Most recent award date

**Sample Output:**
```
rank,recipient_name,uei,duns,total_amount,award_count,agencies
1,LOCKHEED MARTIN CORPORATION,ABC123,123456789,5000000000,250,Department of Defense; Department of the Air Force
2,RAYTHEON TECHNOLOGIES CORPORATION,DEF456,987654321,3500000000,180,Department of Defense; Department of the Navy
```

---

### 4. Database Migration Scripts

#### `migrate_contractors_to_entities.py`

**Purpose:** Import top contractors into `entities_master.csv` and `entity_identifiers.csv`

**Usage:**
```bash
python migrate_contractors_to_entities.py \
  --contractors_csv ../contractors/top_contractors.csv \
  --entities_master ../entities/entities_master.csv \
  --identifiers ../entities/entity_identifiers.csv \
  --max_contractors 50
```

**Parameters:**
- `--contractors_csv`: Input CSV from aggregate_top_recipients.py
- `--entities_master`: Path to entities_master.csv (will be updated)
- `--identifiers`: Path to entity_identifiers.csv (will be updated)
- `--max_contractors`: Maximum number of contractors to add (default: 50)

**Features:**
- Duplicate detection by normalized name
- Entity type inference (Corporation, Research Institution, etc.)
- UEI and DUNS identifier preservation
- Auto-generated descriptions with funding totals
- Maintains existing entity records

**Entity Type Inference Logic:**
1. **Corporation**: Contains "defense", "aerospace", "technologies", "corporation", etc.
2. **Government Agency**: Contains "department of", "agency", "government"
3. **Research Institution**: Contains "university", "institute", "laboratory"
4. **Organization**: Default fallback

---

## Execution Workflow

### Step-by-Step Process

#### Step 1: Fetch Contractor Data from USASpending API

```bash
cd c:\Users\brand\Project RaHorus\project_rawhorse\data\scripts

python fetch_usaspending_multiagency.py \
  --keywords_file ../reference/keywords_expanded_contractors.txt \
  --agencies_json ../reference/agencies_contractor_expansion.json \
  --out_dir ../external/contractors_expansion \
  --min_action_date 2020-01-01 \
  --pages 3
```

**Expected Output:**
- 660+ JSON files in `data/external/contractors_expansion/`
- `_manifest.json` with execution summary

**Verification:**
```bash
# Check manifest
type ..\external\contractors_expansion\_manifest.json | findstr "count"

# Count files
dir ..\external\contractors_expansion\*.json | find /c ".json"
```

---

#### Step 2: Aggregate Top Recipients

```bash
python aggregate_top_recipients.py \
  --data_dir ../external/contractors_expansion \
  --output ../contractors/top_contractors_2025.csv \
  --top_n 100 \
  --min_amount 500000
```

**Expected Output:**
- CSV with 100 top contractors
- Console summary showing top 10 with amounts

**Verification:**
```bash
# View top 10 lines
type ..\contractors\top_contractors_2025.csv | head -10

# Check total entries
type ..\contractors\top_contractors_2025.csv | find /c /v ""
```

---

#### Step 3: Review and Filter (Optional)

**Manual Review:**
1. Open `top_contractors_2025.csv` in Excel or text editor
2. Review contractor names for relevance to UAP/aerospace
3. Remove any obviously irrelevant entries
4. Save filtered version as `top_contractors_filtered.csv`

**Filtering Criteria:**
- Aerospace primes (Boeing, Lockheed Martin, Northrop Grumman, Raytheon, etc.)
- Defense electronics companies
- Advanced materials manufacturers
- Space technology companies
- Sensor/detection technology providers
- Research labs with aerospace focus

---

#### Step 4: Migrate to Entities Database

```bash
python migrate_contractors_to_entities.py \
  --contractors_csv ../contractors/top_contractors_filtered.csv \
  --entities_master ../entities/entities_master.csv \
  --identifiers ../entities/entity_identifiers.csv \
  --max_contractors 50
```

**Expected Output:**
- Updated `entities_master.csv` with 50 new entities
- Updated `entity_identifiers.csv` with UEI/DUNS mappings
- Console summary showing entity type breakdown

**Verification:**
```bash
# Count entities before and after
type ..\entities\entities_master.csv | find /c /v ""

# Check for duplicates
type ..\entities\entities_master.csv | sort | uniq -d
```

---

#### Step 5: Reload Database

After migrating contractors, reload the database to reflect new entities:

```bash
cd c:\Users\brand\Project RaHorus\project_rawhorse

# Delete existing database
del data\prh.db

# Restart application (will trigger data reload)
RUN.bat
```

The data loader will automatically import the updated entities and identifiers.

---

## Expected Results

### Dataset Expansion Goals

**Before Expansion:**
- ~50-70 entities
- Primarily government agencies and a few major contractors

**After Expansion:**
- 100-120 entities (+50 contractors)
- Comprehensive coverage of aerospace/defense industry
- Enhanced network visualization with contractor nodes

### Entity Types Added

| Entity Type | Count | Examples |
|------------|-------|----------|
| Corporation | 35-40 | Lockheed Martin, Raytheon, Boeing, Northrop Grumman |
| Research Institution | 5-10 | MITRE, Aerospace Corporation, RAND |
| Organization | 5-10 | Specialized technology firms |

### Identifiers Added

- 50+ UEI (Unique Entity Identifier) entries
- 50+ DUNS numbers
- Verified linkage to USASpending data

---

## Troubleshooting

### Issue: API Rate Limit Errors

**Symptoms:**
- 429 status codes
- "Rate limit exceeded" messages

**Solutions:**
1. Increase delay between requests (`time.sleep(0.6)` instead of `0.4`)
2. Reduce number of pages (`--pages 2` instead of 5)
3. Split execution into smaller batches by keyword

---

### Issue: Empty or Missing Results

**Symptoms:**
- Zero awards returned
- Empty JSON files

**Solutions:**
1. Verify agency names match USASpending API exactly
2. Check keyword spelling and relevance
3. Adjust date range (`--min_action_date`)
4. Inspect `_manifest.json` for API errors

---

### Issue: Duplicate Entities

**Symptoms:**
- Migration script reports many duplicates
- Same contractor appears multiple times

**Solutions:**
1. Run deduplication script first: `python detect_entity_duplicates.py`
2. Review and merge duplicates: `python merge_entities.py`
3. Use `--max_contractors` to limit additions
4. Manually review `top_contractors.csv` before migration

---

### Issue: Incorrect Entity Types

**Symptoms:**
- Research institutions classified as corporations
- Government entities classified incorrectly

**Solutions:**
1. Update `infer_entity_type()` function in migration script
2. Add more keyword patterns for entity type detection
3. Manually edit `entities_master.csv` after migration
4. Re-run database reload

---

## Performance Optimization

### Parallel Execution

For faster data fetching, split by agency:

```bash
# Terminal 1: DoD branches
python fetch_usaspending_multiagency.py \
  --agencies_json dod_agencies.json \
  --out_dir ../external/dod_contractors

# Terminal 2: NASA & NSF
python fetch_usaspending_multiagency.py \
  --agencies_json civilian_agencies.json \
  --out_dir ../external/civilian_contractors
```

Then aggregate both directories:
```bash
python aggregate_top_recipients.py \
  --data_dir ../external/dod_contractors \
  --output ../contractors/dod_top.csv

python aggregate_top_recipients.py \
  --data_dir ../external/civilian_contractors \
  --output ../contractors/civilian_top.csv
```

---

## Data Quality Checks

### Post-Migration Validation

**1. Check Entity Count:**
```sql
SELECT COUNT(*) FROM entities;
-- Should increase by ~50
```

**2. Verify Entity Types:**
```sql
SELECT entity_type, COUNT(*) 
FROM entities 
GROUP BY entity_type;
-- Should show Corporation as majority
```

**3. Check Identifiers:**
```sql
SELECT COUNT(*) 
FROM entity_identifiers 
WHERE identifier_type IN ('UEI', 'DUNS');
-- Should increase by ~100 (50 entities × 2 identifiers)
```

**4. Verify No Duplicates:**
```sql
SELECT normalized_name, COUNT(*) 
FROM entities 
GROUP BY normalized_name 
HAVING COUNT(*) > 1;
-- Should return 0 rows
```

---

## Future Enhancements

### Automated Enrichment

**SAM.gov Integration:**
- Fetch additional contractor details (address, business type, capabilities)
- Link UEI to SAM.gov entity profiles
- Auto-populate website and description fields

**USASpending Sub-Awards:**
- Discover subcontractors receiving flow-through funding
- Build multi-tier contractor relationships
- Enhance money flow graph with prime-sub connections

**Historical Trends:**
- Track contractor award trends over time
- Identify emerging contractors (rapid funding growth)
- Detect declining contractors (funding drop-off)

### Machine Learning Classification

**Entity Type Prediction:**
- Train classifier on existing labeled entities
- Auto-classify new contractors with confidence scores
- Reduce manual review burden

**Relevance Scoring:**
- Score contractors by UAP/aerospace relevance
- Prioritize high-relevance entities for inclusion
- Filter noise from generic contractors

---

## Maintenance Schedule

### Monthly Updates

Run contractor expansion monthly to discover new entities:

```bash
# Last day of each month
cd data/scripts
python fetch_usaspending_multiagency.py --min_action_date YYYY-MM-01
python aggregate_top_recipients.py
python migrate_contractors_to_entities.py --max_contractors 10
```

### Quarterly Deep Dives

Full re-fetch with extended date range:

```bash
# Every 3 months
python fetch_usaspending_multiagency.py \
  --min_action_date 2020-01-01 \
  --pages 10 \
  --out_dir ../external/quarterly_refresh
```

---

## Success Metrics

✅ **Completed:**
- Configuration files created (keywords, agencies)
- 3 Python scripts implemented and tested
- Documentation complete

📊 **Expected Outcomes:**
- 50+ defense/aerospace contractors added
- 100+ new identifiers (UEI/DUNS)
- Enhanced network visualization density
- Improved financial flow tracking coverage

🎯 **Quality Targets:**
- <5% duplicate entities
- 100% USASpending source attribution
- 90%+ correct entity type classification

---

## Conclusion

The contractor expansion implementation is complete and ready for execution. All necessary scripts, configuration files, and documentation are in place. The user can now run the 4-step workflow at their convenience to expand the entity database with 50+ defense and aerospace contractors.

**Next Steps:**
1. User executes Step 1-4 workflow when ready
2. Review aggregated contractors for relevance
3. Run migration to update database
4. Restart application to see new entities in network graphs

**Status:** ✅ Implementation Complete - Ready for User Execution

