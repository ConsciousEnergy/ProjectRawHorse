# Changelog - Project RawHorse v0.3.1Beta

## Release Date: February 2026

## Overview

This release consolidates months of development (v0.3.0 through v0.3.3 Beta) into a single milestone. Key areas include: **data enrichment** from UAPGerb's "The Hidden Wing" transcript, **Intelligence Stack Pyramid** visualization, **advanced search** with suggestions and history, **one-click uninstall**, **CI/CD improvements**, and **production infrastructure** preparation for VPS deployment.

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

#### Entity Network Graph Overhaul (v0.4.0 Beta)
- 3-panel layout: GraphSidebar (left), force graph (center), RelationshipTimeline (right)
- New components: `GraphSidebar.tsx`, `RelationshipTimeline.tsx` + CSS
- Square-root node sizing by connection count (4-40px range)
- Radial force model pushing high-connection nodes to center
- Edge deduplication with count tracking
- Dual color modes: Entity Type (default) and Proximity
- Cyan selection highlighting with edge dimming for unconnected nodes
- Instructions banner ("Click nodes... Scroll to zoom... Drag to pan")
- Full-bleed dark background (#030712)

#### Search Quality Fixes (v0.4.0 Beta)
- Multi-word tokenized AND conditions across all four search functions
- `entity_id` added to entity search columns
- `parse_amount_query` returns multiple ranges (exact, K, M) for bare numbers
- Text fallback for numeric queries in award/flow descriptions
- Always-on fuzzy matching with WRatio scorer (not just fallback)
- Lower score cutoff (55) for short queries (< 8 chars)
- TTL-based name list cache (5 min) for fuzzy matching performance
- "Did you mean?" suggestions API field on zero results
- Frontend suggestion pills with cyan styling
- Multi-token highlighting in Browse HighlightText

### Intelligence Stack Pyramid (v0.3.2 Beta)
- **Dedicated Pyramid page** at `/analysis/pyramid` with trapezoid-tier visualization (L1 narrow top → L6 wide bottom)
- Chain-of-command tracing from any entity up through the hierarchy
- Entity detail panels with metadata, relationships, and connections
- Full-width layout for large datasets
- PyramidVisualization and PyramidPage components

### Advanced Search & Browse Enhancements (v0.3.1–v0.3.3 Beta)
- **Global SearchBar** with real-time debounced search (200ms) across all data types
- **Search Suggestions**: recent queries (last 10) and recent clicked results (last 8) from localStorage
- **Visual Row Highlighting**: clicking a search result navigates to Browse and flashes the matching row
- **Keyboard Navigation**: ↑↓ arrows, Enter to select, Esc to close, `/` global shortcut to focus
- **Browse Page Rewrite**: sortable columns, pagination (10/25/50/100), search highlighting, active filter chips
- **Backend Search**: multi-word/alias expansion, amount-aware queries, fuzzy matching with rapidfuzz
- Clear history button for recent results and queries

### One-Click Uninstall (v0.3.3 Beta)
- **UNINSTALL.bat** (Windows) and **UNINSTALL.sh** (macOS/Linux) remove all install artifacts
- Server detection via port 8000 (`netstat`/`lsof`/`ss`); option to stop the server before removal
- Optional prompts: keep database, remove Linux desktop entry
- `--force` / `/force` flag skips all prompts for scripted use
- Removal summary printed at end (R=removed, K=kept, N=not found)
- Windows long-path fallback for `node_modules` via `robocopy`

### CI/CD Improvements (v0.3.3 Beta)
- **Deprecated GitHub Actions upgraded**: upload/download-artifact v3→v4, setup-python v4→v5, gh-release v1→v2
- **Node.js**: 18→20 LTS with npm caching
- **Trigger tightened**: workflow runs only on `v*` tag pushes and `workflow_dispatch`, not branch pushes
- **Permissions**: top-level `contents: write` for release creation
- **Concurrency**: `cancel-in-progress: true` to prevent duplicate runs
- **Build hardening**: `NODE_OPTIONS: --max-old-space-size=4096`, `frontend/dist` existence check

#### CI Pipeline (v0.4.0 Beta)
- New `ci-check.yml` for PR status checks (tsc --noEmit, pip install, npm run build)
- Fixed `build-releases.yml` shell indentation (fi alignment)
- Regenerated `package-lock.json` to fix npm ci failure (vite version sync)

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

**Launch & Uninstall Scripts:**
- `START.bat` - Windows guided launcher
- `START.sh` - macOS/Linux guided launcher
- `UNINSTALL.bat` - Windows one-click uninstaller
- `UNINSTALL.sh` - macOS/Linux one-click uninstaller

**Search UX & Browse:**
- `frontend/src/components/SearchBar.tsx` - Suggestions, recent results/queries, keyboard nav
- `frontend/src/components/SearchBar.css` - Suggestion styles
- `frontend/src/pages/Browse.tsx` - Row highlight, stable row IDs, scroll-into-view
- `frontend/src/pages/Browse.css` - Flash animation

**Network Graph (v0.4.0 Beta):**
- `frontend/src/components/GraphSidebar.tsx` + `.css`
- `frontend/src/components/RelationshipTimeline.tsx` + `.css`

**Pyramid Visualization:**
- `frontend/src/pages/PyramidPage.tsx`
- `frontend/src/components/PyramidVisualization.tsx`
- `frontend/src/components/PyramidVisualization.css`

### Modified Files
- `frontend/src/pages/NetworkGraphPage.tsx` - 3-panel layout rewrite
- `frontend/src/pages/Analysis.tsx` - Replaced embedded NetworkGraph with link to dedicated page
- `frontend/src/components/SearchBar.tsx` - "Did you mean?" suggestions
- `frontend/src/types/index.ts` - suggestions field on SearchResponse
- `backend/routers/search.py` - Multi-word, multi-scale, always-on fuzzy, suggestions
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
- `.github/workflows/build-releases.yml` - Upgraded actions, caching, concurrency, trigger tightening
- `build_executable.py` - CI-safe UAPUFOResearch path handling

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

## What's Next

### v0.4.1
- [ ] **Dedicated FOIA Targets page** under Analysis (`/analysis/foia`)

### v0.5.0+ Roadmap

- [ ] **UFO Database Enrichment** - Ingest NUFORC, MUFON CMS, GEIPAN, and other public sighting databases
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

---

## Development History

This release consolidates the following incremental Beta releases:
- **v0.4.0 Beta** (Feb 2026) — Network Graph 3-panel overhaul, search quality fixes, CI pipeline, privacy compliance
- **v0.3.0** (Nov 2025) — Enhanced search, FOIA quality scoring, data versioning
- **v0.3.1 Beta** (Feb 2026) — Browse page rewrite with pagination, sorting, search highlighting
- **v0.3.2 Beta** (Feb 2026) — Intelligence Stack Pyramid, backend fuzzy search, L6 program expansion
- **v0.3.3 Beta** (Feb 2026) — Search UX (suggestions, history, row highlighting), CI fixes, one-click uninstall

See individual `CHANGELOG_v0.3.x` files for granular details.

---

**Full Changelog**: Compare with v0.3.0 on GitHub
