# Academic Institution Integration Guide

**Date:** December 1, 2025  
**Feature:** NSF Awards API integration for academic institution discovery  
**Status:** ✅ Ready to Execute

---

## Overview

This guide documents the process for discovering and integrating academic institutions into Project RawHorse using the NSF (National Science Foundation) Awards Search API.

---

## Implementation Components

### 1. NSF Awards Fetcher (`data/scripts/fetch_nsf_awards.py`)

**Purpose:** Query NSF Awards API for grants matching UAP/aerospace keywords

**API Documentation:** https://www.research.gov/common/webapi/awardapisearch-v1.htm

**Usage:**
```bash
cd data/scripts

python fetch_nsf_awards.py \
  --keywords_file ../reference/keywords_academic_institutions.txt \
  --output_dir ../external/nsf_awards \
  --start_date "01/01/2019" \
  --max_pages 10 \
  --rows_per_page 25
```

**Parameters:**
- `--keywords_file`: Path to keywords file (one keyword per line)
- `--output_dir`: Output directory for JSON results
- `--start_date`: Start date in MM/DD/YYYY format (default: 01/01/2019)
- `--max_pages`: Max pages to fetch per keyword (default: 10)
- `--rows_per_page`: Results per page (max 25, default: 25)

**Features:**
- Automatic rate limiting (1 second between requests)
- OR logic for keyword searches
- Comprehensive award data extraction
- Manifest generation for tracking

**Output:**
- Individual JSON files per keyword: `nsf_quantum_sensing.json`
- Manifest file: `_manifest.json`

---

### 2. Institution Extractor (`data/scripts/extract_institutions_from_nsf.py`)

**Purpose:** Parse NSF awards and aggregate institution data

**Usage:**
```bash
python extract_institutions_from_nsf.py \
  --data_dir ../external/nsf_awards \
  --output ../academic/nsf_institutions.csv \
  --min_awards 2 \
  --min_funding 100000 \
  --top_n 50
```

**Parameters:**
- `--data_dir`: Directory with NSF JSON files
- `--output`: Output CSV file
- `--min_awards`: Minimum award count threshold (default: 2)
- `--min_funding`: Minimum total funding threshold (default: $100,000)
- `--top_n`: Number of top institutions to output (default: 50)

**Features:**
- Institution deduplication by normalized name
- Funding aggregation across all awards
- Research area extraction from award titles
- PI (Principal Investigator) tracking
- Date range tracking (first/last award)

**Output CSV Columns:**
- `rank`: Ranking by total funding
- `name`: Institution name
- `city`, `state`, `zip`, `country`: Location
- `award_count`: Number of NSF awards
- `total_funding`: Sum of all award amounts
- `research_areas`: Semicolon-separated research areas
- `pi_count`: Number of unique PIs
- `first_award`, `last_award`: Award date range

---

### 3. Institution Migrator (`data/scripts/migrate_institutions_to_entities.py`)

**Purpose:** Import academic institutions into entities database

**Usage:**
```bash
python migrate_institutions_to_entities.py \
  --institutions_csv ../academic/nsf_institutions.csv \
  --entities_master ../entities/entities_master.csv \
  --max_institutions 30
```

**Parameters:**
- `--institutions_csv`: Input CSV from extract_institutions_from_nsf.py
- `--entities_master`: Path to entities_master.csv (will be updated)
- `--max_institutions`: Maximum institutions to add (default: 30)

**Features:**
- Duplicate detection by normalized name
- Entity type inference (Academic Institution vs Research Institution)
- Rich descriptions with location and research areas
- Comprehensive notes with funding and PI data
- Maintains existing entity records

---

## Keywords Configuration

**File:** `data/reference/keywords_academic_institutions.txt`

**Keywords (15 total):**
- UAP, unidentified aerial phenomena
- Aerospace engineering
- Plasma physics
- Quantum sensing
- Advanced materials, metamaterials
- Propulsion systems
- High energy physics
- Atmospheric/optical/space physics
- Sensor systems
- Electromagnetic radiation
- Gravitational physics

These keywords target universities and institutions conducting relevant research.

---

## Execution Workflow

### Step 1: Fetch NSF Awards

```bash
cd c:\Users\brand\Project RaHorus\project_rawhorse\data\scripts

python fetch_nsf_awards.py \
  --keywords_file ../reference/keywords_academic_institutions.txt \
  --output_dir ../external/nsf_awards \
  --start_date "01/01/2020" \
  --max_pages 5
```

**Expected Output:**
- 75+ JSON files (15 keywords × 5 pages)
- 250-500+ awards total
- `_manifest.json` summary

**Runtime:** ~2-3 minutes with rate limiting

**Verification:**
```bash
# Check manifest
type ..\external\nsf_awards\_manifest.json | findstr "count"

# Count files
dir ..\external\nsf_awards\*.json | find /c ".json"
```

---

### Step 2: Extract and Rank Institutions

```bash
python extract_institutions_from_nsf.py \
  --data_dir ../external/nsf_awards \
  --output ../academic/nsf_institutions_2025.csv \
  --min_awards 2 \
  --min_funding 100000 \
  --top_n 50
```

**Expected Output:**
- CSV with 30-50 institutions
- Ranked by total NSF funding
- Console showing top 10 summary

**Verification:**
```bash
# View first 10 lines
type ..\academic\nsf_institutions_2025.csv | head -10

# Count institutions
type ..\academic\nsf_institutions_2025.csv | find /c /v ""
```

---

### Step 3: Review Institutions (Optional)

**Manual Review:**
1. Open `nsf_institutions_2025.csv` in Excel
2. Review for relevance to UAP/aerospace
3. Remove generic institutions (e.g., community colleges without relevant research)
4. Save as `nsf_institutions_filtered.csv`

**Filtering Criteria:**
- R1 research universities (major research institutions)
- Institutions with aerospace/physics departments
- Labs with relevant research areas
- Remove: Teaching-focused institutions, non-technical schools

---

### Step 4: Migrate to Database

```bash
python migrate_institutions_to_entities.py \
  --institutions_csv ../academic/nsf_institutions_filtered.csv \
  --entities_master ../entities/entities_master.csv \
  --max_institutions 30
```

**Expected Output:**
- 30 new entities added to `entities_master.csv`
- Console showing entity type breakdown
- Sample institutions list

**Verification:**
```bash
# Count entities before and after
type ..\entities\entities_master.csv | find /c /v ""

# Check new Academic Institution entries
type ..\entities\entities_master.csv | findstr "Academic Institution" | find /c /v ""
```

---

### Step 5: Reload Database

```bash
cd c:\Users\brand\Project RaHorus\project_rawhorse

# Delete existing database
del data\prh.db

# Restart application
RUN.bat
```

---

## Expected Results

### Dataset Expansion

**Before:**
- ~70-90 entities
- Limited academic institutions

**After:**
- 100-120 entities (+30 institutions)
- Comprehensive coverage of US research universities
- Enhanced network density

### Top Institutions (Examples)

Based on NSF funding for UAP-relevant research:
- MIT (Massachusetts Institute of Technology)
- Stanford University
- UC Berkeley
- Caltech (California Institute of Technology)
- University of Michigan
- Georgia Tech
- University of Illinois
- Princeton University
- Cornell University
- University of Texas at Austin

### Entity Details

Each institution includes:
- Location (city, state)
- Research areas (quantum, plasma, aerospace, etc.)
- NSF award count and total funding
- PI count and active research period

---

## Research Area Classification

**Automatic Detection from Award Titles:**
- **Quantum Physics**: Awards mentioning "quantum"
- **Plasma Physics**: Awards mentioning "plasma"
- **Aerospace**: Awards mentioning "aerospace" or "aeronautics"
- **Materials Science**: Awards mentioning "materials"
- **Sensor Technology**: Awards mentioning "sensor" or "sensing"
- **Propulsion**: Awards mentioning "propulsion"

Multiple areas can be assigned to a single institution.

---

## Troubleshooting

### Issue: NSF API Rate Limiting

**Symptoms:**
- 429 status codes
- Connection timeouts

**Solutions:**
1. Increase delay between requests (modify `time.sleep(1)` to `time.sleep(2)`)
2. Reduce pages per keyword (`--max_pages 3`)
3. Split execution by keyword groups

---

### Issue: No Results for Keywords

**Symptoms:**
- Empty JSON files
- Zero awards in manifest

**Solutions:**
1. Verify keywords are spelled correctly
2. Adjust date range (try earlier start date)
3. Try broader keywords (e.g., "physics" instead of "plasma physics")

---

### Issue: Institution Name Variations

**Symptoms:**
- Same institution appears multiple times with different names
- Duplicate detection misses variations

**Solutions:**
1. Manual review and consolidation in CSV before migration
2. Run deduplication script: `python detect_entity_duplicates.py`
3. Update fuzzy matching thresholds

---

## Alternative Data Sources

### NIH RePORTER (Future Enhancement)

**API:** https://api.reporter.nih.gov/

**Relevant Institutes:**
- National Institute of Biomedical Imaging and Bioengineering (NIBIB) - sensor technology
- National Institute of General Medical Sciences (NIGMS) - biophysics

**Keywords:**
- Biomedical imaging
- Biosensors
- Radiation detection

### ARPA-E (Advanced Research Projects Agency-Energy)

**API:** USASpending API with ARPA-E filter

**Keywords:**
- Advanced energy
- Plasma energy
- High energy density
- Novel materials

### NASA Grants

**API:** NASA SBIR/STTR database

**Keywords:**
- Space technology
- Aerospace research
- Propulsion
- Sensor systems

---

## Data Quality Checks

### Post-Migration Validation

**1. Entity Count:**
```sql
SELECT COUNT(*) FROM entities WHERE entity_type = 'Academic Institution';
-- Should show ~30 new institutions
```

**2. Funding Verification:**
```sql
SELECT display_name, notes 
FROM entities 
WHERE source = 'NSF Awards API' 
ORDER BY display_name;
-- Verify funding amounts are present
```

**3. Research Areas:**
```sql
SELECT display_name, description 
FROM entities 
WHERE description LIKE '%Research areas:%';
-- Check research areas are populated
```

---

## Future Enhancements

### Automated Grant-to-MoneyFlow Mapping

Convert NSF awards into money_flows:
```
Source: NSF
Target: University
Amount: Award amount
Relationship: Grant
```

### PI Entity Creation

Create individual entities for prominent PIs:
- Extract PI names from awards
- Create "Individual" entity type
- Link to institution via relationships

### Research Collaboration Detection

Identify multi-institution awards:
- Extract co-PIs and collaborating institutions
- Create collaboration relationships
- Build inter-institutional research networks

### Real-time Award Monitoring

Set up periodic NSF API polling:
- Monthly checks for new awards
- Alert on awards to existing entities
- Auto-add newly funded institutions

---

## Success Metrics

✅ **Completed:**
- NSF Awards fetcher implemented
- Institution extractor with aggregation
- Migration script with duplicate detection
- Keywords configuration
- Documentation complete

📊 **Expected Outcomes:**
- 30+ academic institutions added
- 100% NSF source attribution
- Rich metadata (location, research areas, funding)
- Zero duplicates

🎯 **Quality Targets:**
- R1 research universities prioritized
- Institutions with 2+ relevant awards
- Minimum $100K in NSF funding
- US-based institutions (configurable)

---

## Conclusion

The academic institution integration is complete and ready for execution. The NSF Awards API provides a rich source of data for discovering universities and research labs conducting UAP-relevant research. The 3-step workflow (fetch, extract, migrate) ensures high-quality data integration with minimal duplicates.

**Status:** ✅ Implementation Complete - Ready for User Execution

**Estimated Additions:** 30 academic institutions with NSF funding data

