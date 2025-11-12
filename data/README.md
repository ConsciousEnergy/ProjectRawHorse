# Project RawHorse - Data Organization

**Last Updated:** 2025-11-11  
**Status:** ✅ Refactored and Unified

This directory contains the organized and consolidated UAP/UFO research dataset from multiple authoritative public sources.

## 🎯 Recent Refactoring (2025-11-11)

The data folder has been **completely refactored** to eliminate redundancy and improve clarity:
- **74 files → 48 active files** (35% reduction)
- **26 files archived** (no data lost)
- **All date stamps removed** from filenames (use Git for versioning)
- **All version suffixes removed** (v1, v2, v3)
- **Unified naming convention** applied throughout
- **FOIA templates organized** into dedicated subfolder

## Directory Structure

```
data/
├── entities/              # Entity and organization data [5 files]
├── financial/             # Awards, contracts, money flows [9 files]
├── foia/                  # FOIA requests and templates [3 files + templates/]
├── reference/             # Lookup tables [7 files]
├── evidence/              # Evidence bundles [1 file]
├── visualizations/        # Network graphs [8 files]
├── scripts/               # Data processing [11 files]
├── docs/                  # Documentation [5 files]
└── _archive/              # Historical files (archived)
```

## Data Files

### 1. Entities (`entities/`) - 5 Files

**Purpose:** Master entity data, identifiers, and relationships

| File | Description | Rows |
|------|-------------|------|
| `entities_master.csv` | Master list of all entities with full metadata | ~11 |
| `entity_identifiers.csv` | UEI, DUNS, CAGE codes for entities | ~varies |
| `entity_relationships.csv` | Entity-to-entity relationship edges | ~15 |
| `entities_seeds.csv` | Seed data for entity expansion | ~varies |
| `entities_orphaned.csv` | Entities without clear connections | ~varies |

**Key Fields:**
- **entities_master.csv**: entity_id, name, uei, duns, cage, type, country, state, city, url
- **entity_identifiers.csv**: Various identifier formats
- **entity_relationships.csv**: source, target, label

### 2. Financial (`financial/`) - 9 Files

**Purpose:** Federal spending, awards, and money flow analysis

| File | Description |
|------|-------------|
| `awards_master.csv` | All awards with enrichment (scoring, keywords) |
| `awards_usaspending.csv` | USAspending-specific award data |
| `solicitations.csv` | Federal procurement solicitations |
| `money_flows.csv` | All money flow edges (cleaned and normalized) |
| `money_flows_veritas_peraton.csv` | Veritas/Peraton specific flow analysis |
| `federal_flows_by_agency.csv` | Federal spending rolled up by agency |
| `federal_flows_by_recipient.csv` | Federal spending by recipient and FY |
| `federal_agency_peraton.csv` | Agency-to-Peraton connection edges |
| `fiscal_year_totals.csv` | Fiscal year summary totals |

**Key Fields:**
- **awards_master.csv**: award_uid, piid, award_type, action_date, current_total_value, description, funding_agency, recipient_uei, credibility_score
- **money_flows.csv**: source, target, amount_usd, date, type, relationship, edge_id

### 3. FOIA (`foia/`) - 3 Files + Templates Folder

**Purpose:** Freedom of Information Act requests and targets

| File | Description |
|------|-------------|
| `foia_queue.csv` | All FOIA requests in queue |
| `foia_queue_top10.csv` | Top 10 priority FOIA requests |
| `foia_targets.csv` | Target agencies and entities for FOIA |
| `foia_template_generic.txt` | Generic FOIA request template |

**Templates Folder (`foia/templates/`):**
- 14 entity-specific pre-filled FOIA request templates
- Companies include: Advanced Ceramic Fibers, Aegis Technologies, HYPRES, Intrinsic Semiconductor, Peraton (5 divisions), Plasmonics, SEEQC, Sivananthan Laboratories, UES

### 4. Reference (`reference/`) - 7 Files

**Purpose:** Lookup tables, keywords, and reference data

| File | Description |
|------|-------------|
| `ffrdc_lookup_master.csv` | Federally Funded R&D Centers lookup table |
| `ffrdc_uarc_search_kits_full.csv` | Full FFRDC/UARC search kits |
| `keywords_deduped.txt` | Deduplicated keyword list for scoring |
| `keyword_weights.csv` | Keyword weighting for credibility scoring |
| `mission_rollup.csv` | Mission category rollups |
| `advisors_fees.csv` | M&A advisors and reported fees |
| `veritas_lps.csv` | Veritas Capital Limited Partners data |

**Purpose:** Support data enrichment, scoring algorithms, and entity matching

### 5. Evidence (`evidence/`) - 1 File

**Purpose:** Comprehensive evidence bundles

| File | Description |
|------|-------------|
| `evidence_bundle.csv` | Compiled evidence bundle (CSV format) |

**Note:** Excel format archived (use CSV for consistency)

### 6. Visualizations (`visualizations/`) - 8 Files

**Purpose:** Network graphs and analytical charts (PNG format)

- `uap_entity_graph.png` - Entity relationship network
- `uap_money_flow_graph_v3.png` - Money flow visualization
- `lp_network_graph_v1.png` - Limited partners network
- `lp_alignment_chart.png` - LP alignment analysis
- `Financial and Organizational Ties in UAP_UFO research.png` - Organizational ties
- `Financial Spending in UAP_UFO Research.png` - Spending overview
- `money_inflows_bar_v3.png` - Money inflows bar chart
- `time_series_alignment.png` - Time series analysis

### 7. Scripts (`scripts/`) - 11 Files

**Purpose:** Python scripts for data fetching, normalization, and scoring

**Fetchers (4 files):**
- `fetch_arpae_projects.py` - Fetch ARPA-E projects
- `fetch_sam_entities_bulk.py` - Bulk SAM.gov entity fetching
- `fetch_usaspending_multiagency.py` - Multi-agency USAspending
- `fetch_usaspending_weighted.py` - Keyword-weighted USAspending

**Normalizers (3 files):**
- `normalize_arpae_projects.py` - Normalize ARPA-E data
- `normalize_usaspending_multiagency.py` - Normalize multi-agency awards
- `normalize_usaspending_weighted.py` - Normalize weighted awards

**Scorers (2 files):**
- `score_join_doe_v2.py` - DOE-specific scoring (v2)
- `score_join_integrated.py` - Integrated scoring pipeline

**Utilities (2 files):**
- `deconflict_geotime.py` - Geospatial/temporal deconfliction
- `watch_processed_to_json.py` - Watch and convert to JSON

### 8. Documentation (`docs/`) - 5 Files

**Purpose:** Methodology and data integrity documentation

- `README.md` - Main contractor pack documentation
- `CREDIBILITY_SCORING.md` - Scoring methodology
- `ENTITY_EXPANSION.md` - Entity expansion process
- `INTEGRATED_PIPELINE.md` - Pipeline integration guide
- `uap_data_integrity_profile_2025-11-06.md` - Data integrity profile

## Naming Conventions

### ✅ New Unified Convention

1. **Descriptive names:** `entities_master.csv` not `entities.csv`
2. **No dates:** Use Git for versioning, not filenames
3. **No versions:** Use Git tags, not v1/v2/v3 suffixes
4. **Underscores:** Use `_` for word separation
5. **Lowercase:** All filenames lowercase
6. **CSV primary:** CSV as primary format (Excel archived)

### Examples

| ❌ Old | ✅ New |
|---------|---------|
| `uap_entities_master_2025-11-06.csv` | `entities_master.csv` |
| `uap_money_edges_v3.csv` | `money_flows.csv` |
| `federal_flows_rollup_agency_total_2025-11-06.csv` | `federal_flows_by_agency.csv` |
| `foia_queue_2025-11-06.xlsx` | `foia_queue.csv` |

## Data Sources

All data sourced from authoritative public sources:

- ✅ **USAspending.gov** - Federal spending and awards
- ✅ **SAM.gov** - System for Award Management
- ✅ **OSTI** - Office of Scientific and Technical Information
- ✅ **SBIR.gov** - Small Business Innovation Research
- ✅ **DOE OSDBU** - Department of Energy forecasts
- ✅ **FedConnect** - Federal procurement opportunities
- ✅ **AARO.mil** - All-domain Anomaly Resolution Office
- ✅ **FOIA Reading Rooms** - Agency FOIA databases
- ✅ **ARPA-E** - Advanced Research Projects Agency-Energy

## Data Integrity

### Provenance
- Every data point traceable to public source
- Source files documented in data integrity profiles
- No classified, PII, or export-controlled content

### Versioning
- Git used for all version control
- Date stamps removed from filenames
- Version history in Git log
- Original files preserved in `_archive/`

### Quality
- Deduplicated keywords and entities
- Normalized identifiers (UEI, DUNS, CAGE)
- Validated relationships
- Scored for credibility

## Archive Directory

Old/redundant files moved to `_archive/2025-11-06_original/`:
- All original files with date stamps
- All versioned files (v1, v2, v3)
- Duplicate formats (XLSX when CSV exists)
- 26 files total archived
- **No data lost** - all originals preserved

## Usage Guidelines

### 1. Loading Data

```python
import pandas as pd

# Load entities
entities = pd.read_csv('data/entities/entities_master.csv')

# Load financial data
awards = pd.read_csv('data/financial/awards_master.csv')
money_flows = pd.read_csv('data/financial/money_flows.csv')

# Load FOIA targets
foia_targets = pd.read_csv('data/foia/foia_targets.csv')
```

### 2. Updating Data

When updating data:
1. **DO NOT** add date stamps to filenames
2. **DO** commit changes to Git with descriptive message
3. **DO** update data integrity profiles
4. **DO** run validation scripts

### 3. Adding New Data

When adding new data files:
1. Follow naming conventions (no dates, no versions)
2. Place in appropriate category folder
3. Update this README
4. Add to data integrity profile
5. Commit with clear message

## Application Integration

The unified structure maps cleanly to application endpoints:

```
API Endpoint                    → Data File
──────────────────────────────────────────────────────
/api/data/entities              → entities/entities_master.csv
/api/data/entity-identifiers    → entities/entity_identifiers.csv
/api/data/relationships         → entities/entity_relationships.csv
/api/data/awards                → financial/awards_master.csv
/api/data/money-flows           → financial/money_flows.csv
/api/data/solicitations         → financial/solicitations.csv
/api/data/foia-targets          → foia/foia_targets.csv
/api/data/foia-queue            → foia/foia_queue.csv
```

## Key Entities

Primary focus entities in this dataset:
- **Peraton** (and 5 subsidiaries)
- **Veritas Capital** (private equity)
- **Lockheed Martin**
- **Huntington Ingalls Industries (HII)**
- **NGA** (National Geospatial-Intelligence Agency)
- **DCSA** (Defense Counterintelligence and Security Agency)

## Statistics

```
Total Active Files:    48 files
Total Archived:        26 files
Total Directories:      9 directories

By Category:
  Entities:             5 files
  Financial:            9 files
  FOIA:                 3 files + 15 templates
  Reference:            7 files
  Evidence:             1 file
  Visualizations:       8 files
  Scripts:             11 files
  Documentation:        5 files

File Reduction:        35% (74 → 48 files)
```

## Maintenance

### Regular Updates
- Run fetcher scripts monthly for fresh data
- Check FOIA releases quarterly
- Update entity relationships as new connections emerge
- Refresh visualizations with new data

### Quality Assurance
- Validate data integrity on load
- Check for duplicate entries
- Verify data completeness
- Review scoring accuracy

### Version Control
- Commit data changes with descriptive messages
- Tag major data releases
- Document breaking changes
- Maintain backward compatibility when possible

## Migration History

- **2025-11-11:** Major refactoring - unified naming, archived redundant files, organized templates
- **2025-11-11:** Initial data organization from UAPUFOData folder

## Questions or Issues

For questions about data sources, methodology, or integrity:
- Review documentation in `docs/`
- Check data integrity profile
- See refactoring plan: `REFACTORING_PLAN.md`
- Check archive documentation: `_archive/README.md`

## License

This data compilation follows public domain and open government data principles.
See main project LICENSE (GNU AGPL v3) for application code.

---

**Project RawHorse** - Clean data through unified organization and reproducible research.
