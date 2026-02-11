# Changelog - Project RawHorse v0.3.1Beta

## Release Date: January 2026

## Overview

This release focuses on three key areas: **data enrichment** from UAPGerb's "The Hidden Wing" transcript, **UI/UX improvements** for visualization navigation, and **production infrastructure** preparation for VPS deployment.

---

## New Features

### Data Enrichment - "The Hidden Wing" Transcript

Added 26 new entities and 28 relationships from UAPGerb's US Air Force UFO Reverse Engineering Programs analysis:

**New Air Force Organizations:**
- SAF-AQ (Air Force Acquisition)
- SAF-AQL (Air Force Special Programs)
- SAF-AQR (Science, Technology and Engineering)
- RCO (Rapid Capabilities Office)
- SAF-AAH (Sensitive Activities)
- SAF-AAZ (Special Programs Oversight)
- AFTE (Air Force Test and Evaluation)
- AFRL (Air Force Research Laboratory)
- AFMC (Air Force Materiel Command)
- 412th Test Wing
- And more...

**New FOIA Targets:** 8 high-priority targets focusing on Air Force acquisition programs

### UI/UX Improvements

#### Visualization Sub-Pages
- **Network Graph** now on dedicated page at `/analysis/network`
- **Sankey Diagram** now on dedicated page at `/analysis/sankey`
- **Analysis Overview** landing page with visualization cards
- Full-viewport containers eliminate scroll/zoom conflicts
- Breadcrumb navigation for easy return

#### Intelligence Stack Filter
- New pyramid-style toggle filter for entity categorization
- Filter by 6 hierarchy levels:
  1. Control Group (MITRE/JASON, NSC, Executive Branch)
  2. Administrators (NRO, NGA, CIA DS&T, SAF-AQ)
  3. FFRDCs (MITRE, Battelle, Sandia, National Labs)
  4. Prime Contractors (Lockheed, Northrop, Raytheon)
  5. Facilities (Area 51, Edwards AFB, Tonopah)
  6. Programs (Immaculate Constellation, Kona Blue)

#### Attribution Section
- Added "Data Sources and Attribution" card to About page
- Credits UAPGerb's research with YouTube links
- Lists government data sources

### Production Infrastructure

#### Docker Support
- Full Docker Compose configuration for VPS deployment
- Multi-service setup: Backend, Frontend, PostgreSQL, Redis, Caddy
- Development compose file with hot reload
- Automatic HTTPS via Caddy reverse proxy

#### Database Improvements
- **PostgreSQL support** alongside SQLite fallback
- Automatic database detection from environment
- Connection pooling for production workloads
- `intel_stack_level` field added to Entity model

#### Authentication System
- JWT-based authentication module
- Token generation and refresh endpoints
- Role-based access control (scopes)
- Optional auth - disabled by default for local use

#### Git LFS Removal
- Removed Git LFS dependency for CSV files
- Simplified `.gitattributes` configuration
- Easier cloning and contribution workflow

---

## Files Changed

### New Files (35+)

**Data Enrichment Pipeline:**
- `data/scripts/entity_recognition.py` - NER and pattern extraction
- `data/scripts/amount_extraction.py` - Financial amount parsing
- `data/scripts/date_extraction.py` - Date parsing utilities
- `data/scripts/validate_flows.py` - Quality gates and validation
- `data/scripts/enrich_entity_flows.py` - Main enrichment script
- `data/scripts/extract_materials_flows.py` - Materials transfer tracking
- `data/scripts/combine_all_data.py` - Unified data loading
- `data/scripts/compliance_filter.py` - Sensitive data filtering
- `data/scripts/test_enrichment_quick.py` - Pipeline testing
- `data/scripts/run_enrichment_sample.py` - Sample enrichment runner

**Hidden Wing Data:**
- `data/scripts/extract_hidden_wing_entities.py`
- `data/entities/hidden_wing_entities.csv`
- `data/entities/hidden_wing_relationships.csv`
- `data/foia/hidden_wing_foia_targets.csv`

**Frontend Components:**
- `frontend/src/pages/AnalysisOverview.tsx`
- `frontend/src/pages/NetworkGraphPage.tsx`
- `frontend/src/pages/SankeyDiagramPage.tsx`
- `frontend/src/components/IntelStackFilter.tsx`
- `frontend/src/components/IntelStackFilter.css`

**Docker & Infrastructure:**
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker/Caddyfile`
- `docker/init-db.sql`
- `docker/.env.example`
- `backend/auth.py`
- `backend/routers/auth_router.py`

**Launch Scripts:**
- `START.bat` - Windows guided launcher
- `START.sh` - macOS/Linux guided launcher

### Modified Files
- `backend/data_loader.py` - Load Hidden Wing data
- `backend/database.py` - PostgreSQL support
- `backend/main.py` - Auth router
- `backend/requirements.txt` - Organized dependencies
- `backend/models/schemas.py` - intel_stack_level field
- `backend/routers/analysis.py` - Return intel level
- `frontend/src/App.tsx` - Nested analysis routes
- `frontend/src/pages/About.tsx` - Attribution section
- `frontend/src/types/index.ts` - Intel stack types
- `frontend/src/components/NetworkGraph.tsx` - Filter support
- `.gitattributes` - Remove LFS for CSV

---

## Breaking Changes

- Analysis page route changed:
  - Old: `/analysis` showed all visualizations
  - New: `/analysis` shows overview, use `/analysis/network` or `/analysis/sankey` for visualizations

## Migration Notes

1. **Database Migration**: Run `python reload_database.py` to add new Hidden Wing entities
2. **Frontend Routes**: Update any bookmarks from `/analysis` to `/analysis/network` or `/analysis/sankey`
3. **Git LFS**: If you had LFS installed, you may want to run `git lfs uninstall` for this repo

---

## Data Attribution

Special thanks to **UAPGerb** for the research that informed this update:
- [YouTube Channel](https://www.youtube.com/@uapgerb)
- "The Hidden Wing" - US Air Force UFO Reverse Engineering Programs (2026)
- Previous transcripts on NRO, CIA DS&T, FFRDCs

---

### Data Enrichment Pipeline

New automated data collection and enrichment system:

**Core Modules:**
- `entity_recognition.py` - spaCy NER + pattern-based entity extraction
- `amount_extraction.py` - Financial amount parsing ($M, $B, ranges)
- `date_extraction.py` - Flexible date parsing with dateparser
- `validate_flows.py` - Quality gates and specificity scoring
- `enrich_entity_flows.py` - Main financial flow enrichment
- `extract_materials_flows.py` - Materials and technology transfer tracking
- `combine_all_data.py` - Unified data loading across all routes

**Features:**
- Source credibility scoring (gov=0.95, news=0.8, etc.)
- Duplicate detection with fuzzy matching
- Compliance filtering for sensitive data
- Web search integration (DuckDuckGo)
- Result caching for efficiency

### One-Click Installation Improvements

- **START.bat** / **START.sh** - New guided launchers with auto-install
- **install.bat** / **install.sh** - Improved 6-step installation with progress
- **LaunchRawHorse.vbs** - Windows launcher with custom icon support
- Multi-location venv detection for flexible setups
- ASCII art banner for professional appearance
- Better error messages for non-technical users

---

## What's Next (v0.5.0 Roadmap)

- [ ] **Intelligence Stack Pyramid** - Hierarchical visualization of U.S. intelligence agencies
- [ ] VPS deployment guide and one-click deploy script
- [ ] User authentication UI in frontend
- [ ] Enhanced Sankey diagram with intel stack coloring
- [ ] Timeline visualization for entity relationships
- [ ] Batch entity import from CSV upload
- [ ] API rate limiting and caching with Redis

---

## Dependencies Added

```
spacy>=3.8.0
en_core_web_sm (spaCy model)
rapidfuzz>=3.0.0
dateparser>=1.2.0
validators>=0.20.0
duckduckgo-search>=5.0.0
```

---

## Contributors

- Development: Project RawHorse Team
- Research: UAPGerb (data source attribution)
- Community: Open source contributors

---

**Full Changelog**: Compare with v0.3.0 on GitHub
