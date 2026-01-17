# Data Scraping Quick Start Guide

## Overview

The data scraping system provides 7 new scrapers for collecting credible financial flows, material transfers, and FOIA-verifiable data from authoritative public sources.

---

## Quick Start

### 1. Test Compliance Filter

```bash
cd data/scripts
python -c "from compliance_filter import compliance_check; print(compliance_check('Public contract award'))"
```

### 2. Run Individual Scrapers

```bash
# SEC EDGAR filings
python fetch_sec_edgar.py

# FOIA reading rooms
python fetch_foia_indexes.py

# Congressional records
python fetch_congressional.py

# Press releases
python fetch_press_releases.py

# Court records
python fetch_court_records.py

# State corporate filings (template)
python fetch_state_corps.py
```

### 3. Review Outputs

All scrapers output CSV files in their respective directories:
- SEC EDGAR: `data/financial/sec_edgar/`
- FOIA Indexes: `data/foia/reading_rooms/`
- Congressional: `data/reference/congressional/`
- Press Releases: `data/financial/press_releases/`
- Court Records: `data/reference/court_records/`

### 4. Load to Database

After reviewing CSV outputs, use existing data loader to import:
```bash
python combine_all_data.py
```

---

## Compliance Protection

All scrapers include automatic compliance filtering:

- **Keyword Detection**: Filters restricted terms (classified, atomic energy, ITAR, etc.)
- **Source Validation**: Verifies URLs are from public sources
- **Record Filtering**: Rejects records containing restricted content

---

## Source Credibility Tiers

| Tier | Score | Sources |
|------|-------|---------|
| 1 | 0.9-1.0 | .gov, .mil, USAspending, SEC, FPDS, CourtListener |
| 2 | 0.7-0.9 | PR Newswire, Business Wire, Reuters, Bloomberg |
| 3 | 0.5-0.7 | OrangeSlices AI, Crunchbase, Tracxn |
| 4 | 0.3-0.5 | Unknown sources |

---

## Rate Limiting

All scrapers respect rate limits:
- 2 second delay between requests
- User-Agent headers configured
- Retry logic for 429 responses

---

## New Database Model

**MaterialsFlow** table added to track non-financial transfers:
- Technology transfers
- Equipment procurement
- IP licensing
- Material supply agreements

See `backend/database.py` for schema.

---

## Next Steps

1. Run scrapers to populate initial datasets
2. Review CSV outputs for accuracy
3. Load validated records to database
4. Schedule periodic runs (weekly/monthly)
5. Monitor compliance filter hits

---

## Files Created

All new files are in `data/scripts/`:
- `compliance_filter.py` - Legal compliance checks
- `fetch_sec_edgar.py` - SEC filings
- `fetch_foia_indexes.py` - FOIA reading rooms
- `fetch_congressional.py` - Congressional records
- `fetch_press_releases.py` - Press releases
- `fetch_court_records.py` - Court records
- `fetch_state_corps.py` - State corporate filings (template)

---

## Documentation

- **Full Implementation Summary**: [`docs/SCRAPING_IMPLEMENTATION_SUMMARY.md`](docs/SCRAPING_IMPLEMENTATION_SUMMARY.md)
- **Original Plan**: [`docs/ENRICHMENT_IMPROVEMENT_PLAN.md`](docs/ENRICHMENT_IMPROVEMENT_PLAN.md)
