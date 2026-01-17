# Entity Flow Enrichment Guide

## Overview

The entity flow enrichment tool researches financial and material flows between entities using web searches. It automatically discovers contracts, acquisitions, investments, and partnerships that may not be in the current database.

## Features

- **Automated Web Research**: Searches for financial information about entities
- **Smart Extraction**: Identifies contracts, M&A deals, investments, and partnerships
- **Amount Detection**: Extracts dollar amounts from search results
- **Caching**: Caches results to avoid redundant searches
- **CSV Export**: Saves discovered flows to CSV files for review

## Usage

### Basic Usage

```bash
python run_enrichment.py
```

This will:
1. Load all entities from the database (focusing on Corporations, Government Agencies, Research Institutions, and Investment Firms)
2. Search the web for financial/material flow information
3. Extract relevant data
4. Save results to `data/financial/enriched_flows_YYYYMMDD_HHMMSS.csv`

### Advanced Usage

You can modify the script to:
- Change which entity types to research
- Adjust search queries
- Modify extraction patterns
- Change output format

## Output Format

The script generates CSV files with the following columns:

- `source`: Source entity name
- `target`: Target entity name (if identified)
- `relationship`: Type of flow (M&A, Contract, Investment, Partnership, Financial Flow)
- `amount_usd`: Dollar amount (if extracted)
- `start_date`: Date of transaction (if found)
- `end_date`: End date (if applicable)
- `source_citation`: URL of the source article/page
- `notes`: Relevant snippet from search results
- `edge_id`: Unique identifier for the flow
- `source_norm`: Normalized source name
- `target_norm`: Normalized target name

## Reviewing Results

After running the enrichment:

1. **Review the CSV file** in `data/financial/enriched_flows_*.csv`
2. **Verify accuracy** of extracted information
3. **Add missing dates** if you can find them
4. **Load into database** using the data loader

## Loading Enriched Data

Once you've reviewed and verified the enriched flows:

```python
from backend.data_loader import load_money_flows
from backend.database import init_database, get_session_maker

# Initialize database
engine = init_database("data/prh.db")
session_maker = get_session_maker(engine)
db = session_maker()

# Load enriched flows
load_money_flows(db, "data/financial/enriched_flows_YYYYMMDD_HHMMSS.csv")

db.close()
```

## Configuration

Edit `enrich_entity_flows.py` to customize:

- `SEARCH_DELAY`: Delay between searches (default: 2 seconds)
- `MAX_RESULTS_PER_ENTITY`: Max results per entity (default: 5)
- Entity types to research
- Search query patterns

## Limitations

- **Rate Limiting**: Web searches are rate-limited to avoid blocking
- **Accuracy**: Extracted data should be verified manually
- **Coverage**: Not all entities may have publicly available financial information
- **Target Detection**: Target entity extraction is heuristic-based and may miss some relationships

## Best Practices

1. **Run during off-peak hours** to avoid rate limiting
2. **Review results carefully** before loading into database
3. **Verify amounts and dates** from source citations
4. **Check for duplicates** with existing money flows
5. **Update source citations** with accurate URLs

## Troubleshooting

### No results found
- Entity may not have public financial information
- Try different search queries
- Check if entity name needs normalization

### Rate limiting errors
- Increase `SEARCH_DELAY` in the script
- Run the script in smaller batches
- Use cached results when available

### Import errors
- Install required packages: `pip install requests beautifulsoup4`
- Check Python version (3.8+ required)
