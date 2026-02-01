# Changelog - v0.3.1 Beta

**Date**: February 1, 2026  
**Branch**: PRH_v0.3.1Beta  
**Status**: Ready for PR

---

## 🚀 Major Features

### Enhanced Browse Page
Complete rewrite of the Browse page with modern search and filtering capabilities:

- **Debounced Auto-Search** - Search triggers automatically as you type (300ms delay)
- **Search Highlighting** - Matching terms highlighted in yellow within results
- **Recent Searches** - Last 5 searches saved locally for quick access
- **Quick Search Chips** - One-click filters for common searches
- **Active Filter Chips** - Visual display of all active filters with one-click removal
- **Sortable Columns** - Click any column header to sort ascending/descending
- **Pagination Controls** - Navigate through results with page controls (10/25/50/100 per page)
- **Entity Type Multi-Select** - Checkbox filters for multiple entity types
- **Intel Stack Level Filter** - Filter by intelligence hierarchy levels (L1-L6)
- **Agency Filter** - Filter Awards/FOIA by agency name

### New Federal Contract Data
Added 20 new money flows from 2024-2025 federal contract research:

| Contract | Amount | Description |
|----------|--------|-------------|
| MITRE NSEC (Air Force) | $541M | FFRDC Support Contract |
| Leidos CHS-6 (Army) | $7.9B | Tactical IT Hardware |
| Leidos SIGINT (NSA) | $390M | Signals Intelligence |
| Leidos TCPED (DIA) | $143M | AI/ML System |
| Northrop OPIR (Space Force) | $1.8B | Missile Warning Satellites |
| SpaceX Constellation (NRO) | $1.8B | Classified Spy Satellites |
| Lockheed NGI (MDA) | $17B | Next-Gen Interceptor |
| Lockheed F-35 Training | $3.91B | Training Systems |
| Battelle PNNL (DOE) | $2.5B | Lab Management |
| Triad LANL (DOE) | $2.8B | Lab Management |
| + 10 more contracts | | |

---

## 🐛 Bug Fixes

- Fixed ASCII art display in START.bat startup banner
- Fixed date range filtering in backend (was not implemented)
- Fixed pagination offset parameter handling
- Fixed search field expansion for comprehensive results

---

## 📁 Files Added

### Frontend
- `src/pages/Browse.css` - Dedicated styles for enhanced Browse page

### Data
- `data/financial/money_flows_2026_research.csv` - 20 new federal contracts

### Documentation
- `docs/RELEASE_NOTES_v0.3.1.md` - Comprehensive release documentation
- `CHANGELOG_v0.3.1.md` - This changelog

---

## 📝 Files Modified

### Frontend
- `src/pages/Browse.tsx` - Complete rewrite with new features:
  - Debounced search hook
  - HighlightText component
  - SortableHeader component
  - Filter state management
  - Recent searches (localStorage)
  - Quick search chips
  - Active filter chips
  - Pagination controls
  - Column sorting
  - Improved empty states

### Backend
- `routers/data.py` - Enhanced API endpoints:
  - Added date range filtering (start_date, end_date)
  - Added intel_stack_level filter for entities
  - Added offset parameter for pagination
  - Expanded search fields (entity_id, source_citation, PIID)
  - Added default sorting for all endpoints

- `data_loader.py` - Added loading for new money flows file

### Startup
- `START.bat` - Fixed ASCII art banner display

---

## 🗄️ Database Statistics

After this release:
| Category | Count |
|----------|-------|
| Entities | 188 |
| Money Flows | 49 |
| Relationships | 208 |
| FOIA Targets | 28 |

Entity breakdown:
- Corporations: 48
- Government Agencies: 64
- Individuals: 32
- Facilities: 17
- Programs: 15
- Research Institutions: 10
- Organizations: 1
- Investment Firms: 1

---

## 🎨 UI/UX Improvements

### Type Badges (Color-Coded)
| Type | Color |
|------|-------|
| Corporation | Blue |
| Government Agency | Red |
| Individual | Green |
| Research Institution | Purple |
| Facility | Amber |
| Program | Pink |
| Organization | Gray |
| Investment Firm | Teal |

### Intel Level Badges
- L1 (Control Group) - Red
- L2 (Administrators) - Orange
- L3 (FFRDCs) - Yellow
- L4 (Prime Contractors) - Green
- L5 (Facilities) - Blue
- L6 (Programs) - Purple

### Score Badges (FOIA)
- High (≥70%) - Green
- Medium (40-70%) - Yellow
- Low (<40%) - Red

---

## 🔄 API Changes

### Modified Endpoints

**`GET /api/data/entities`**
- Added: `intel_stack_level` parameter
- Added: `offset` parameter (alias for skip)
- Enhanced: Search includes entity_id
- Added: Default sorting by display_name

**`GET /api/data/money-flows`**
- Added: `start_date` parameter (YYYY-MM-DD)
- Added: `end_date` parameter (YYYY-MM-DD)
- Added: `offset` parameter
- Enhanced: Search includes source_citation
- Added: Default sorting by amount descending

**`GET /api/data/awards`**
- Added: `start_date` parameter
- Added: `end_date` parameter
- Added: `offset` parameter
- Enhanced: Search includes PIID, awarding_agency
- Added: Default sorting by amount descending

**`GET /api/data/foia-targets`**
- Added: `offset` parameter
- Enhanced: Search includes agency, timeframe
- Added: Default sorting by priority_score descending

---

## 🧪 Testing

### Manual Testing Completed
- [x] Auto-search functionality
- [x] Search highlighting
- [x] Filter chip display/removal
- [x] Column sorting (all tabs)
- [x] Pagination navigation
- [x] Date range filtering
- [x] Entity type filtering
- [x] Intel level filtering
- [x] Agency filtering
- [x] Quick search chips
- [x] Recent searches persistence

---

## 📊 Performance

| Feature | Performance |
|---------|-------------|
| Auto-search | 300ms debounce |
| API Response | < 50ms average |
| Filter Application | Instant |
| Sort Operation | Client-side, instant |
| Page Navigation | Instant |

---

## 🚨 Breaking Changes

**None.** All changes are backward compatible.

The `skip` parameter is still supported as an alias for `offset`.

---

## ⚙️ Technical Details

### New CSS Classes
- `.search-section` - Enhanced search container
- `.search-highlight` - Yellow highlight for matches
- `.filter-chip` / `.quick-chip` - Filter buttons
- `.sortable-header` - Clickable table headers
- `.type-badge.*` - Entity type badges
- `.intel-badge.*` - Intel level badges
- `.score-badge.*` - FOIA score badges

### localStorage Keys
- `recentSearches` - Array of last 5 search terms

---

## 📈 Code Stats

| Category | Lines Changed |
|----------|---------------|
| Frontend (Browse.tsx) | +550 lines |
| Frontend (Browse.css) | +350 lines |
| Backend (data.py) | +80 lines |
| Data (money_flows) | +20 records |
| Documentation | +400 lines |

---

## 🎯 Success Criteria

All criteria met:

- [x] Debounced auto-search works smoothly
- [x] Search highlighting visible
- [x] Filters apply correctly
- [x] Sorting works on all columns
- [x] Pagination navigates properly
- [x] New contract data loads
- [x] No breaking changes
- [x] Fully documented
- [x] ASCII art displays correctly

---

## 🔮 Future Enhancements

Planned for next release:
1. Export filtered results to CSV
2. Saved filter presets
3. Advanced search (AND/OR operators)
4. Entity detail modal/page
5. Relationship explorer from Browse
6. Full-text search with Elasticsearch

---

**Version**: v0.3.1 Beta  
**Ready for**: Pull Request to main branch  
**Branch Name**: PRH_v0.3.1Beta
