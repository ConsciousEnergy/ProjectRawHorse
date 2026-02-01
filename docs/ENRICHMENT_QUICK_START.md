# Data Enrichment - Quick Start Guide

## Overview

The data enrichment system automatically discovers financial and material flows between entities using web search and advanced NLP extraction algorithms.

## Prerequisites

The enrichment pipeline requires additional Python packages:

```bash
# Install enrichment dependencies
pip install spacy rapidfuzz dateparser validators duckduckgo-search

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Quick Start

### 1. Test the Pipeline

```bash
# Navigate to scripts directory
cd data/scripts

# Run quick test (verifies all modules work)
python test_enrichment_quick.py
```

Expected output:
- Amount extraction: 6/6 tests passed
- Date extraction: 4/4 tests passed
- Entity recognition: Working
- Specificity scoring: Working
- Source credibility: Tiered scoring
- Flow validation: Quality scoring

### 2. Run Sample Enrichment

```bash
# Test enrichment on a few entities
python run_enrichment_sample.py
```

### 3. Run Full Enrichment

```bash
# Process all entities (Corporations, Government Agencies, etc.)
python enrich_entity_flows.py
```

### 4. Run Materials Flow Enrichment

```bash
# Extract technology and materials transfers
python extract_materials_flows.py
```

### 5. Combine All Data

```bash
# Load all data into database (ensures consistency across routes)
python combine_all_data.py

# Check data integrity
python combine_all_data.py --check

# Append new data only (skip existing)
python combine_all_data.py --append
```

## Pipeline Modules

| Module | Purpose |
|--------|---------|
| `entity_recognition.py` | NER with spaCy + pattern-based extraction |
| `amount_extraction.py` | Financial amount parsing ($M, $B, ranges) |
| `date_extraction.py` | Flexible date parsing with dateparser |
| `validate_flows.py` | Quality gates, specificity scoring, duplicate detection |
| `compliance_filter.py` | Filter sensitive/classified information |
| `enrich_entity_flows.py` | Main financial flow enrichment |
| `extract_materials_flows.py` | Materials and technology transfers |
| `combine_all_data.py` | Unified data loading |

## Output Files

Results are saved to:
- **Financial CSV**: `data/financial/enriched_flows_YYYYMMDD_HHMMSS.csv`
- **Materials CSV**: `data/materials/materials_flows_YYYYMMDD_HHMMSS.csv`
- **Cache**: `data/scripts/.cache/*.json` (for faster reruns)

## What Gets Extracted

### Financial Flows
- **Target Entities**: Using NER + pattern matching
- **Amounts**: 12+ regex patterns (millions, billions, ranges)
- **Dates**: Multiple formats via dateparser
- **Relationship Types**: M&A, Contract, Investment, Partnership

### Materials Flows
- **Material Types**: Technology, equipment, IP, prototype, software
- **Relationship Types**: Technology Transfer, Material Supply, IP Licensing, Subcontract

## Quality Gates

All flows are validated before saving:
- ✅ Must have source entity
- ✅ Must have target entity OR amount/date
- ✅ Must pass specificity filtering (no generic list pages)
- ✅ Duplicate detection with fuzzy matching
- ✅ Source credibility scoring

### Source Credibility Tiers

| Tier | Score | Examples |
|------|-------|----------|
| 1 (Gov) | 0.95 | usaspending.gov, sam.gov, sec.gov |
| 2 (News) | 0.80 | reuters.com, bloomberg.com, wsj.com |
| 3 (Aggregators) | 0.60 | crunchbase.com, tracxn.com |
| 4 (Other) | 0.40 | Unknown sources |

## Search Behavior

- Uses DuckDuckGo web search (no API key needed)
- 7 query types per entity (acquisitions, contracts, M&A, etc.)
- Rate limited (2 seconds between searches)
- Results cached for faster reruns

## Troubleshooting

**No results found?**
- Some entities may not have public financial information
- Web search services may temporarily limit results
- Check cache directory for previous results

**Low quality results?**
- Review specificity scores in debug output
- Adjust search queries in enrichment scripts
- Check extraction algorithms in individual modules

**Module import errors?**
- Ensure all dependencies installed: `pip install spacy rapidfuzz dateparser validators duckduckgo-search`
- Download spaCy model: `python -m spacy download en_core_web_sm`

## Configuration

Edit `data/scripts/enrich_entity_flows.py`:
- `SEARCH_DELAY`: Delay between searches (default: 2 seconds)
- `MAX_RESULTS_PER_ENTITY`: Max results per entity (default: 5)
- `search_queries`: Query types to use

## Advanced Documentation

- `docs/ENRICHMENT_IMPROVEMENT_PLAN.md` - Full improvement plan (7 phases)
- `docs/ENRICHMENT_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `docs/ENRICHMENT_SUCCESS.md` - Success metrics

## Example Usage

```python
# In Python
from entity_recognition import extract_target_entity
from amount_extraction import extract_amount
from date_extraction import extract_date
from validate_flows import validate_flow, get_source_credibility_score

# Extract amount from text
amount = extract_amount("Contract worth $1.5 billion awarded")
# Returns: 1500000000.0

# Extract date
date = extract_date("Announced on January 15, 2024")
# Returns: datetime.date(2024, 1, 15)

# Get source credibility
score = get_source_credibility_score("https://usaspending.gov/award/123")
# Returns: 0.95

# Validate a flow
result = validate_flow({
    'source': 'Lockheed Martin',
    'target': 'MITRE',
    'amount_usd': 1900000000,
    'source_citation': 'https://usaspending.gov/award/123'
})
# Returns: {'valid': True, 'quality_score': 0.98, ...}
```
