# Project RawHorse v0.3.1 Beta Release Notes

**Release Date:** February 1, 2026  
**Version:** 0.3.1 Beta  
**Branch:** PRH_v0.3.1Beta

---

## Overview

This release brings significant improvements to the Browse page with enhanced search capabilities, new federal contract data from deep research, and backend API improvements for better filtering and pagination.

---

## New Features

### Enhanced Browse Page

#### Debounced Auto-Search
- Search automatically triggers as you type (300ms delay)
- No need to press Enter or click Search button
- Provides instant feedback on search results

#### Search Highlighting
- Matching search terms are highlighted in yellow within results
- Makes it easy to identify why results matched your query

#### Recent Searches
- Last 5 searches are saved locally
- Quick-click chips to repeat recent searches
- Persists across browser sessions

#### Quick Search Chips
One-click filters for common searches:
- **Corporations** - Filter to Corporation entity type
- **Gov Agencies** - Filter to Government Agency type
- **Individuals** - Filter to Individual type
- **Flows > $1M** - Money flows over $1 million
- **FOIA Targets** - Jump to FOIA targets tab

#### Active Filter Chips
- Visual display of all currently active filters
- One-click removal of individual filters
- "Clear All" button to reset everything

#### Sortable Columns
- Click any column header to sort ascending/descending
- Sort indicator shows current sort direction (▲/▼)
- Works across all data tabs

#### Pagination Controls
- Navigate through large result sets
- Choose items per page: 10, 25, 50, or 100
- Page navigation with Previous/Next buttons

#### Entity Type Multi-Select
- Checkbox filters for all entity types
- Select multiple types simultaneously
- Available types: Corporation, Government Agency, Individual, Research Institution, Facility, Program, Organization, Investment Firm

#### Intel Stack Level Filter
- Filter entities by intelligence hierarchy level (1-6)
- Levels correspond to pyramid hierarchy:
  - L1: Control Group
  - L2: Administrators
  - L3: FFRDCs
  - L4: Prime Contractors
  - L5: Facilities
  - L6: Programs

#### Agency Filter
- Filter Awards and FOIA targets by agency name
- Partial text matching supported

#### Improved Entity Display
- Color-coded type badges for entity types
- Intel level badges (L1-L6) with color coding
- "View Network" button to see entity in network graph

### New Federal Contract Data

Added 20 new money flows from 2024-2025 federal contract research:

| Source | Target | Amount | Description |
|--------|--------|--------|-------------|
| US Air Force | MITRE Corporation | $541M | FFRDC NSEC Support Contract |
| US Army | Leidos | $7.9B | Tactical IT Hardware (CHS-6) |
| NSA | Leidos | $390M | SIGINT Capabilities |
| DIA | Leidos | $143M | TCPED System (AI/ML) |
| Space Force | Northrop Grumman | $1.8B | Next-Gen OPIR Satellites |
| NRO | SpaceX | $1.8B | Classified Spy Satellite Constellation |
| NRO | Northrop Grumman | $500M | Satellite Sensors |
| NRO | HawkEye 360 | $50M | RF Geolocation Extension |
| NRO | Capella Space | $30M | Commercial SAR Extension |
| NRO | ICEYE US | $30M | Commercial SAR Extension |
| NRO | Umbra Lab | $30M | Commercial SAR Extension |
| Missile Defense Agency | Lockheed Martin | $17B | NGI Development |
| US Air Force | Lockheed Martin | $3.91B | F-35 Training Systems |
| DOE | Battelle Memorial Institute | $2.5B | PNNL GOCO Management |
| DOE | Battelle Energy Alliance | $1.8B | INL GOCO Management |
| DOE | Triad National Security | $2.8B | LANL GOCO Management |
| US Air Force | Rapid Capabilities Office | $5B | Annual Budget Allocation |
| DARPA | Lockheed Martin | $250M | R&D Contracts |
| DARPA | Northrop Grumman | $200M | R&D Contracts |
| Air Force Research Lab | Boeing | $150M | R&D Contracts |

---

## Backend Improvements

### Date Range Filtering
- Money flows and awards now support date range filtering
- Filter by start_date and end_date parameters
- Proper date parsing and validation

### Intel Stack Level Filter
- New query parameter for filtering entities by intel level
- Supports single level filtering

### Pagination with Offset
- Proper offset/skip support for pagination
- Limit parameter up to 1000 results

### Expanded Search Fields
- Entities: Now searches entity_id in addition to names
- Money Flows: Now searches source_citation
- Awards: Now searches PIID and awarding_agency
- FOIA: Now searches agency and timeframe

### Default Sorting
- Entities: Sorted alphabetically by display_name
- Money Flows: Sorted by amount descending
- Awards: Sorted by amount descending
- FOIA Targets: Sorted by priority score descending

---

## UI/UX Improvements

### Browse Page Styling
- New CSS module for Browse page (`Browse.css`)
- Improved filter panel design
- Better responsive layout for mobile
- Enhanced empty state messages with suggestions
- Loading skeleton during data fetch

### Type Badges
Color-coded badges for entity types:
- **Corporation** - Blue
- **Government Agency** - Red
- **Individual** - Green
- **Research Institution** - Purple
- **Facility** - Amber
- **Program** - Pink
- **Organization** - Gray
- **Investment Firm** - Teal

### Score Badges
For FOIA targets:
- **High** (≥70%) - Green
- **Medium** (40-70%) - Yellow
- **Low** (<40%) - Red

---

## Bug Fixes

- Fixed ASCII art display in START.bat startup banner
- Fixed date filtering in backend (was not implemented)
- Fixed pagination offset parameter handling
- Fixed search field expansion for better results

---

## Database Statistics

After this release:
- **188 Entities** total
- **49 Money Flows** (including 20 new federal contracts)
- **208 Relationships**
- **28 FOIA Targets**

---

## Files Changed

### New Files
- `frontend/src/pages/Browse.css` - Dedicated styles for Browse page
- `data/financial/money_flows_2026_research.csv` - New federal contract data

### Modified Files
- `frontend/src/pages/Browse.tsx` - Complete rewrite with new features
- `backend/routers/data.py` - Added date filtering, intel level filter, pagination
- `backend/data_loader.py` - Added loading for new money flows file
- `START.bat` - Fixed ASCII art banner

---

## Upgrade Notes

1. The Browse page has been completely rewritten - clear browser cache if you experience issues
2. New money flows data will be loaded on next database rebuild or refresh
3. Hard refresh (Ctrl+Shift+R) recommended after upgrade

---

## Known Issues

- CSV comment lines (starting with #) cause non-critical errors during data load
- These errors do not affect data loading and can be safely ignored

---

## Contributors

- Project RawHorse Development Team
- Data research from public federal contract databases

---

## Next Steps

- Add export functionality for filtered results
- Implement saved search presets
- Add advanced search with AND/OR operators
- Entity detail view with full relationship graph
