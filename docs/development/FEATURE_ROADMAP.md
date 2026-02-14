# Project RawHorse - Feature Roadmap & Next Steps

**Last Updated**: February 2026  
**Current Version**: v0.4.0  
**Status**: Active Development

---

## ✅ Completed (v0.2.0 – v0.4.0)

### v0.4.0 (February 2026)
1. **Data Enrichment** - 26 new entities from UAPGerb's "The Hidden Wing" transcript
2. **Intelligence Stack Pyramid** - Hierarchical L1–L6 visualization with chain-of-command tracing
3. **Advanced Search & Suggestions** - Global SearchBar with debounced results, recent queries/results, row highlighting
4. **Network Graph Overhaul** - 3-panel layout (GraphSidebar, force graph, RelationshipTimeline), proximity color mode, radial force layout
5. **Search Quality Fixes** - Multi-word tokenization, multi-scale amounts, always-on fuzzy, "Did you mean?" suggestions
6. **CI Pipeline** - `ci-check.yml` for PR status checks, `build-releases.yml` indentation fix
7. **One-Click Uninstall** - `UNINSTALL.bat` / `UNINSTALL.sh` with server detection and removal summary
8. **CI/CD Improvements** - GitHub Actions v4 upgrades, caching, concurrency, build hardening
9. **Docker Support** - Full Docker Compose configuration for VPS deployment
10. **PostgreSQL Support** - Alongside SQLite fallback
11. **JWT Authentication** - Token-based auth with role-based access control
12. **Git LFS Removal** - Simplified cloning and contributions
13. **OPINT Documentation Overhaul** - Architecture, developer guide, API reference, contributing rewrite

### v0.3.0 (December 2025)
1. **Enhanced Search** - Backend search with FOIA quality scoring
2. **Data Versioning** - Data refresh and version tracking

### v0.2.0 (November 2025)
1. **Donation/Support Section** - Dashboard integration with Conscious Energy links
2. **GitHub Issue #6 Resolution** - Color consistency, acronym expansion, entity classification fixes
3. **Logo Integration** - PRHLogo.png in sidebar with proper backend routing
4. **Network Visualization** - Interactive entity relationship graph with react-force-graph-2d

---

## 🎯 High Priority Features (Ready to Implement)

### 0. **Dedicated FOIA Targets Page** (v0.4.1) 📋 PLANNED NEXT
**Goal**: Browse and manage FOIA targets in a dedicated Analysis sub-page

**Features to Add**:
- **Route**: `/analysis/foia` — linked from Analysis sidebar
- **Browse-style table** with sorting and pagination
- **Filters**: agency, priority score, specificity score
- **Integration** with existing FOIA quality scoring system

**Implementation Complexity**: Low-Medium  
**User Impact**: Medium-High  
**Estimated Time**: 1-2 days

---

### 1. **Enhanced Financial Visualizations** ⭐ RECOMMENDED AFTER v0.4.1
**Goal**: Make money flows visual and intuitive

**Features to Add**:
- **Money Flow Graph with Weighted Edges**
  - Edge thickness based on transaction amount
  - Color gradient for flow values (green = high, blue = low)
  - Animated flow particles showing direction
  - Hover tooltips showing exact amounts and dates
  
- **Timeline Charts**
  - Awards over time (line/bar chart)
  - Spending trends by agency
  - Year-over-year comparison
  - Interactive date range filters

- **Statistical Dashboards**
  - Top 10 recipients by amount (bar chart)
  - Spending distribution pie chart
  - Agency breakdown donut chart
  - Total spending metrics with trends

**Implementation Complexity**: Medium  
**User Impact**: High  
**Tools**: Recharts, D3.js, or Victory Charts  
**Estimated Time**: 3-5 days

---

### ~~2. **Advanced Search & Full-Text Search**~~ ✅ COMPLETED in v0.4.0
> Global SearchBar with real-time debounced results, fuzzy matching (rapidfuzz), suggestions, recent results/queries, visual row highlighting, keyboard navigation, and `/` shortcut.

---

### 3. **Export Enhancements** ⭐ VALUABLE
**Goal**: Enable users to save and share insights

**Features to Add**:
- **Export Network Graph**
  - Save as PNG/SVG
  - High-resolution options
  - Include legend and metadata
  
- **Enhanced PDF Reports**
  - Include charts and graphs
  - Custom report templates
  - Formatted tables
  - Cover page with date/summary
  
- **Excel Export with Formatting**
  - Styled headers
  - Color-coded amounts
  - Auto-width columns
  - Multiple sheets for different data types

**Implementation Complexity**: Medium  
**User Impact**: High  
**Tools**: html2canvas, jsPDF with charts, ExcelJS  
**Estimated Time**: 3-4 days

---

### 4. **Performance Optimizations** 🚀 FOUNDATION
**Goal**: Keep application fast as data grows

**Improvements**:
- **Virtual Scrolling**
  - Handle 10,000+ rows without lag
  - Smooth scrolling experience
  - Reduced memory usage
  
- **Query Caching**
  - Cache API responses
  - Smart invalidation
  - Reduce server load
  
- **Code Splitting**
  - Lazy load heavy components
  - Faster initial load
  - Reduced bundle size

**Implementation Complexity**: Medium  
**User Impact**: High (especially for large datasets)  
**Tools**: React Window, React Query, Dynamic imports  
**Estimated Time**: 2-3 days

---

### 5. **Data Table Enhancements** 📊 POLISH
**Goal**: Professional data browsing experience

**Features to Add**:
- **Advanced Table Features**
  - Column reordering (drag-and-drop)
  - Show/hide columns
  - Column width resize
  - Pin columns (freeze left)
  
- **Multi-column Sorting**
  - Sort by multiple fields
  - Visual sort indicators
  - Persistent sort preferences
  
- **Bulk Operations**
  - Select multiple rows (checkboxes)
  - Bulk export selected
  - Bulk delete/edit (admin)
  
- **Enhanced Pagination**
  - Page size selector (10/25/50/100)
  - Jump to page
  - Total count display

**Implementation Complexity**: Medium  
**User Impact**: High  
**Tools**: TanStack Table (React Table v8)  
**Estimated Time**: 2-3 days

---

### 6. **Credibility Scoring Display** 📈 TRANSPARENCY
**Goal**: Show data quality and confidence levels

**Features to Add**:
- **Score Visualization**
  - Color-coded badges (High/Medium/Low)
  - Score breakdown tooltips
  - Methodology link
  
- **Filtering by Score**
  - Only show high-confidence data
  - Score range sliders
  
- **Score Details Modal**
  - Explain scoring methodology
  - Show component scores
  - Source quality indicators

**Implementation Complexity**: Low-Medium  
**User Impact**: Medium-High (builds trust)  
**Tools**: React components, existing backend data  
**Estimated Time**: 1-2 days

---

## 🔮 Future Features (Lower Priority)

### 7. **Interactive Timeline View**
- Slider to "play" through time
- Watch network evolve
- Key events highlighted

### 8. **Comparison Tool**
- Side-by-side entity comparison
- Metric differences highlighted
- Visual comparison charts

### 9. **Saved Views & Bookmarks**
- Save filter combinations
- Bookmark interesting entities
- Share view URLs

### 10. **API Documentation (Swagger UI)**
- Interactive API docs
- Try endpoints in browser
- Request/response examples

### 11. **User Preferences**
- Remember theme choice
- Save table layouts
- Customize dashboard

### 12. **Notification System**
- New data alerts
- Update notifications
- Contribution status updates

---

## 🎬 Recommended Implementation Order

Based on user impact and complexity, here's the recommended order:

**Next:**
1. **UFO Database Enrichment** (NUFORC, MUFON, GEIPAN — see `UFO_DATABASE_ENRICHMENT_PLAN.md`)
2. **Enhanced Financial Visualizations** (biggest feature, high impact)
3. **Data Table Enhancements** (improves daily use)

**Following:**
4. **Performance Optimizations** (foundation for scale)
5. **Export Enhancements** (polish existing feature)
6. **Credibility Scoring Display** (builds trust)

---

## 💡 Quick Wins (Can Do Today)

These are small features that provide immediate value:

### A. **Keyboard Shortcuts** ⚡ (1-2 hours)
- `/` to focus search
- `Esc` to close modals
- Arrow keys for navigation
- `?` to show shortcuts help

### B. **Loading States** ⏳ (1-2 hours)
- Skeleton screens for tables
- Spinner for graphs
- Progress bars for exports

### C. **Error Boundaries** 🛡️ (1-2 hours)
- Graceful error handling
- User-friendly error messages
- Retry buttons

### D. **Tooltips Everywhere** 💬 (2-3 hours)
- Explain all buttons
- Data field descriptions
- Acronym expansions

### E. **Empty States** 🎨 (1-2 hours)
- Helpful messages when no data
- Suggested actions
- Illustrations/icons

---

## 📊 Feature Comparison Matrix

| Feature | Impact | Complexity | Time | Priority |
|---------|--------|------------|------|----------|
| Financial Visualizations | ⭐⭐⭐⭐⭐ | Medium | 3-5d | P1 |
| ~~Advanced Search~~ | ~~⭐⭐⭐⭐⭐~~ | ~~Medium~~ | ~~2-4d~~ | ✅ Done |
| Export Enhancements | ⭐⭐⭐⭐ | Medium | 3-4d | P2 |
| Performance Opts | ⭐⭐⭐⭐ | Medium | 2-3d | P2 |
| Table Enhancements | ⭐⭐⭐⭐ | Medium | 2-3d | P1 |
| Credibility Display | ⭐⭐⭐ | Low | 1-2d | P2 |
| Quick Wins | ⭐⭐⭐ | Low | 6-10h | Now |

---

## 🚀 Next Session Suggestions

**Option 1: Data Enrichment** 📊
Start **UFO Database Enrichment** - NUFORC, MUFON, GEIPAN (see plan)

**Option 2: Go Big** 🎨
Start **Enhanced Financial Visualizations** - most impactful visual feature

**Option 3: Polish** ✨
Add **Quick Wins** + **Table Enhancements** - many small improvements

**Option 4: Foundation** 🏗️
Focus on **Performance Optimizations** - prepare for growth

---

## 📝 Notes

- All features maintain GNU AGPL v3 compliance
- Public data sources only (no classified/PII)
- Accessibility and keyboard navigation considered
- Dark mode support for all new features
- Mobile responsive where applicable

---

**Which feature would you like to tackle next?** 🎯

Let me know and I'll break it down into actionable implementation steps!

