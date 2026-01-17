# Data Enrichment - Quick Start Guide

## Overview

The data enrichment system automatically discovers financial and material flows between entities using web search and advanced extraction algorithms.

## Quick Start

### 1. Test the System

```bash
# Run test on 3 sample entities
python test_enrichment.py
```

### 2. Run Full Enrichment

```bash
# Process all entities (Corporations, Government Agencies, etc.)
python run_enrichment.py
```

### 3. Review Results

```bash
# Review extracted flows for accuracy
python review_enrichment.py
```

## Output

Results are saved to:
- **CSV**: `data/financial/enriched_flows_YYYYMMDD_HHMMSS.csv`
- **Cache**: `data/scripts/.cache/*.json` (for faster reruns)

## What Gets Extracted

- **Target Entities**: Who is involved (using NER + pattern matching)
- **Amounts**: Financial values (12+ patterns, handles millions/billions)
- **Dates**: When transactions occurred (multiple formats)
- **Relationship Types**: M&A, Contract, Investment, Partnership

## Quality Gates

All flows are validated before saving:
- ✅ Must have source entity
- ✅ Must have target entity OR amount/date
- ✅ Must pass specificity filtering (no generic list pages)
- ✅ Duplicate detection

## Search Behavior

- Uses DuckDuckGo web search (no API key needed)
- 7 query types per entity (acquisitions, contracts, M&A, etc.)
- Rate limited (2 seconds between searches)
- Results cached for faster reruns

## Troubleshooting

**No results found?**
- Some entities may not have public financial information
- Some search queries may return 0 results (normal)
- Check cache directory for previous results

**Low quality results?**
- Review specificity scores in debug output
- Adjust search queries in `enrich_entity_flows.py`
- Check extraction algorithms in individual modules

## Configuration

Edit `data/scripts/enrich_entity_flows.py`:
- `SEARCH_DELAY`: Delay between searches (default: 2 seconds)
- `MAX_RESULTS_PER_ENTITY`: Max results per entity (default: 5)
- `search_queries`: Query types to use

## Advanced

See full documentation:
- `docs/ENRICHMENT_IMPROVEMENT_PLAN.md` - Original improvement plan
- `docs/ENRICHMENT_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `docs/ENRICHMENT_SUCCESS.md` - Success metrics
