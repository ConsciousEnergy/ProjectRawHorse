# Release Notes - Project RawHorse v0.4.0

**Release Date:** February 2026

## Summary

This major release delivers five key areas of improvement:
1. **Data Enrichment Pipeline** - Automated entity and flow extraction with NLP
2. **UI/UX Enhancements** - Separate visualization pages and Intelligence Stack filter
3. **Network Graph Overhaul** - 3-panel Epstein Doc Explorer-style layout with GraphSidebar and RelationshipTimeline
4. **Search Quality Fixes** - Multi-word tokenization, multi-scale amounts, always-on fuzzy, "Did you mean?" suggestions
5. **Production Infrastructure** - Docker deployment and PostgreSQL support

## Highlights

### For Users

- **One-Click Launchers**: New `START.bat` and `START.sh` guide you through installation and launch
- **3-Panel Entity Network Graph**: Left sidebar (search, filters, stats), center force graph, right relationship timeline
- **"Did you mean?" Search Suggestions**: Zero-result searches show clickable suggestion pills
- **Multi-word and Fuzzy Search**: "National Geospatial" finds NGA; typos like "Pereton" match "Peraton"
- **Improved Analysis Page**: Network Graph and Sankey Diagram now have dedicated full-screen pages
- **Intelligence Stack Filter**: Filter entities by hierarchy level (Control Group → Programs)
- **UAPGerb Attribution**: Proper credit to research sources on Dashboard and About pages

### For Researchers

- **26 New Air Force Entities**: From "The Hidden Wing" transcript analysis
- **8 New FOIA Targets**: High-priority Air Force acquisition program requests
- **Data Enrichment Pipeline**: Automated discovery of financial and material flows
- **Source Credibility Scoring**: Tiered scoring system for data sources
- **Proximity Color Mode**: Red (selected) → orange (direct) → green (distant) for high-connection entity discovery
- **Radial Force Layout**: High-connection nodes cluster toward center for easier pattern recognition
- **Epstein Dataset Cross-Reference**: Research note added to UFO_DATABASE_ENRICHMENT_PLAN.md

### For Developers

- **Docker Deployment**: Full multi-service deployment with PostgreSQL, Redis, Caddy
- **PostgreSQL Support**: Production-ready database alongside SQLite fallback
- **JWT Authentication**: Token-based auth for secure write operations
- **NLP Pipeline**: spaCy entity recognition + custom extraction algorithms
- **CI Check Workflow**: `ci-check.yml` for PR status checks (tsc, pip install, npm build)
- **Contributor Privacy**: Public-handle-only attribution guidelines in CONTRIBUTING.md and CODE_OF_CONDUCT.md

## New Features

### Data Enrichment System

Complete automated enrichment pipeline:

| Module | Function |
|--------|----------|
| `entity_recognition.py` | spaCy NER + pattern extraction |
| `amount_extraction.py` | Financial amount parsing |
| `date_extraction.py` | Flexible date parsing |
| `validate_flows.py` | Quality gates and scoring |
| `enrich_entity_flows.py` | Financial flow discovery |
| `extract_materials_flows.py` | Technology transfer tracking |
| `combine_all_data.py` | Unified data loading |

### UI Improvements

- **Analysis Overview** (`/analysis`): Hub page with visualization cards
- **Network Graph** (`/analysis/network`): 3-panel Epstein Doc Explorer-style layout
  - **GraphSidebar** (left): Stats, entity search with autocomplete, color mode toggle, Intel Stack filter, collapsible legend
  - **RelationshipTimeline** (right): Selected actor timeline with relationship badges, entity filter, browse link
  - Square-root node sizing (connection count, 4–40px), radial force model, edge deduplication
  - Proximity color mode (red=selected, orange=direct, green=distant), cyan selection highlighting with edge dimming
  - Instructions banner at bottom ("Click nodes… Scroll to zoom… Drag to pan")
- **Sankey Diagram** (`/analysis/sankey`): Full-viewport flow diagram
- **Intelligence Stack Pyramid**: Coming soon preview on Analysis page

### Search Quality Fixes

- **Multi-word Tokenized AND**: e.g., "National Geospatial" finds NGA across all four search functions
- **Multi-scale Amount Parsing**: $223, $223K, $223M supported in search
- **Always-on Fuzzy Matching**: WRatio scorer with TTL-cached name lists; lower score cutoff (55) for short queries
- **"Did you mean?" Suggestions**: Zero-result searches return clickable suggestion pills
- **Multi-token Highlighting**: Browse page highlights all matched tokens

### Infrastructure

- `docker-compose.yml` - Production deployment
- `docker-compose.dev.yml` - Development with hot reload
- PostgreSQL with connection pooling
- Redis caching support
- Caddy reverse proxy with auto-HTTPS

## Installation

### Quick Start (Recommended)

**Windows:**
```
Double-click START.bat
```

**macOS/Linux:**
```bash
chmod +x START.sh && ./START.sh
```

### Full Installation

See [INSTALL_GUIDE.md](../INSTALL_GUIDE.md) for detailed instructions.

### For Docker Deployment

```bash
# Copy environment file
cp docker/.env.example docker/.env

# Edit with your settings
nano docker/.env

# Start services
docker-compose up -d
```

## Breaking Changes

### Route Changes
- `/analysis` now shows overview page (not visualizations directly)
- Network graph moved to `/analysis/network`
- Sankey diagram moved to `/analysis/sankey`

### Database Changes
- New `intel_stack_level` column on Entity table
- New `materials_flows` table
- Run `python reload_database.py` to migrate

## Dependencies Added

```
spacy>=3.8.0
en_core_web_sm (spaCy model)
rapidfuzz>=3.0.0
dateparser>=1.2.0
validators>=0.20.0
duckduckgo-search>=5.0.0
```

To install:
```bash
pip install spacy rapidfuzz dateparser validators duckduckgo-search
python -m spacy download en_core_web_sm
```

## Data Attribution

Special thanks to **UAPGerb** for research that informed this update:
- YouTube: [@uapgerb](https://www.youtube.com/@uapgerb)
- "The Hidden Wing" - US Air Force UFO Reverse Engineering Programs (2026)

## Known Issues

- Web search may occasionally return 0 results due to external service limitations (search quality improved with fuzzy matching and suggestions)
- Frontend build requires Node.js 18+ (Vite 5.x compatibility)

## Coming in v0.4.1

- [ ] **Dedicated FOIA Targets page** under Analysis (planned)

## Coming in v0.5.0

- [ ] Intelligence Stack Pyramid visualization
- [ ] VPS deployment guide
- [ ] User authentication UI
- [ ] Timeline visualization (RelationshipTimeline component exists; full standalone page in v0.5.0)
- [ ] Batch CSV import

## Contributors

- Development: Project RawHorse Team
- Research: UAPGerb
- Community: Open source contributors

---

**Full Changelog**: [CHANGELOG_v0.4.0.md](../CHANGELOG_v0.4.0.md)

**Previous Release**: [RELEASE_NOTES_v0.3.0.md](RELEASE_NOTES_v0.3.0.md)
