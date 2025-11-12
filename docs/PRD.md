# Project RawHorse - Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** 2025-11-11  
**Status:** Active Development  
**License:** GNU AGPL v3

---

## Executive Summary

Project RawHorse is a cross-platform, single-click desktop application for exploring and analyzing publicly available data related to Unidentified Anomalous Phenomena (UAP) research, federal contracting, and related entities. The application provides transparency through open data and reproducible research while maintaining a strong focus on data integrity and legal compliance.

**Mission:** Enable researchers, journalists, and citizens to explore UAP-related federal spending and entity relationships through an accessible, open-source platform.

**Target Users:**
- UAP researchers and enthusiasts
- Investigative journalists
- Federal spending analysts
- Academic researchers
- Transparency advocates
- General public interested in UAP disclosure

---

## Current Implementation State

### Architecture

**Technology Stack:**
- **Backend:** FastAPI (Python 3.10+) with SQLite database
- **Frontend:** React 18+ with TypeScript
- **Data Visualization:** Planned (D3.js, Recharts)
- **GitHub Integration:** PyGithub for automated PR creation
- **Packaging:** PyInstaller for cross-platform executables
- **Styling:** CSS with custom theming (light/dark mode)

**Application Type:**
- Hybrid local web server (FastAPI backend)
- Opens in browser automatically
- Future: Optional hosting for online access

**Deployment:**
- Cross-platform: Windows, macOS, Linux
- 1-click installation for non-technical users
- Local-first architecture (all processing on user's machine)

### Database Schema

**SQLite Database with 5 Main Tables:**

1. **Entity**
   - entity_id (Primary Key)
   - display_name
   - normalized_name
   - entity_type

2. **Award**
   - id (Primary Key)
   - piid
   - recipient_name
   - recipient_uei, recipient_duns
   - awarding_agency, funding_agency
   - award_amount
   - action_date
   - description
   - naics_code, psc_code

3. **MoneyFlow**
   - id (Primary Key)
   - source, target
   - relationship
   - amount_usd
   - start_date, end_date
   - source_citation
   - edge_id
   - source_norm, target_norm

4. **Relationship**
   - id (Primary Key)
   - source, target
   - label

5. **FOIATarget**
   - id (Primary Key)
   - agency
   - record_request
   - timeframe
   - relevance
   - notes

### Data Organization

**Refactored Structure (Nov 2025):**
- **Before:** 74 files with inconsistent naming, date stamps, version suffixes
- **After:** 48 organized files (35% reduction)
- **Archive:** 26 original files preserved in `data/_archive/`

**Current Structure:**
```
data/
├── entities/          [5 files]  - Entity master data, identifiers, relationships
├── financial/         [9 files]  - Awards, money flows, federal spending
├── foia/             [3 files + 15 templates]  - FOIA requests and targets
├── reference/        [7 files]  - Lookup tables, keywords, mission data
├── evidence/         [1 file]   - Evidence bundles
├── visualizations/   [8 files]  - Network graphs and charts (PNG)
├── scripts/          [11 files] - Data processing Python scripts
└── docs/             [5 files]  - Methodology documentation
```

**Naming Convention:**
- No date stamps (Git handles versioning)
- No version suffixes (v1, v2, v3)
- Clear, descriptive names: `entities_master.csv`, `money_flows.csv`
- CSV primary format (Excel files archived)

### Data Sources

All data sourced from official public databases:
- **USAspending.gov** - Federal spending and awards
- **SAM.gov** - System for Award Management
- **OSTI** - Office of Scientific and Technical Information
- **SBIR.gov** - Small Business Innovation Research
- **DOE OSDBU** - Department of Energy forecasts
- **FedConnect** - Federal procurement opportunities
- **AARO.mil** - All-domain Anomaly Resolution Office
- **FOIA Reading Rooms** - Various agency databases
- **ARPA-E** - Advanced Research Projects Agency-Energy

**Data Integrity:**
- Provenance tracked for every data point
- No classified, PII, or export-controlled content
- Transparent scoring methodology documented
- Reproducible pipeline with public sources only

### Completed Features

#### ✅ Backend (FastAPI)
- SQLite database initialization and schema
- Data loader for CSV files into database
- API endpoints:
  - `/api/data/entities` - Entity listing
  - `/api/data/awards` - Award data
  - `/api/data/money-flows` - Money flow analysis
  - `/api/data/relationships` - Entity relationships
  - `/api/data/foia-targets` - FOIA targets
  - `/api/analysis/network` - Network analysis data
  - `/api/analysis/flows` - Financial flow data
  - `/api/export/csv` - CSV export
  - `/api/export/json` - JSON export
  - `/api/export/pdf` - PDF report generation
  - `/api/contribute/submit` - Data contribution submission
- GitHub service for automated PR creation
- CORS configuration for frontend
- Static file serving
- Configuration via `config.yaml`

#### ✅ Frontend (React + TypeScript)
- **Pages:**
  - Dashboard - Welcome and overview
  - Browse - Data tables with filters
  - Analysis - Visualization placeholder
  - Export - Data export in multiple formats
  - Contribute - Data submission form
  - About - Project information
- **Components:**
  - LegalDisclaimer - Modal with GNU AGPL v3 license and disclaimer
  - ThemeToggle - Light/dark mode switcher
- **Features:**
  - Responsive layout with sidebar navigation
  - Purple and gold color scheme (from PRH logo)
  - Light and dark mode theming
  - Logo favicon
  - TypeScript type definitions

#### ✅ Installation & Distribution
- **1-Click Installation:**
  - `install.bat` (Windows)
  - `install.sh` (macOS/Linux)
  - Automated Python/Node.js checks
  - Virtual environment setup
  - Dependency installation
  - Frontend build
  - Backend launch
- **Quick Launch:**
  - `RUN.bat` (Windows)
  - `RUN.sh` (macOS/Linux)
- **Cross-Platform Packaging:**
  - PyInstaller configuration
  - GitHub Actions workflow for automated builds
  - `build_executable.py` script

#### ✅ Documentation
- README.md - Project overview and setup
- DISCLAIMER.md - Legal disclaimer for data use
- LICENSE - GNU AGPL v3
- CONTRIBUTING.md - Contribution guidelines
- QUICKSTART.md - Quick start guide
- INSTALL_GUIDE.md - Detailed installation instructions
- COLOR_REFERENCE.md - Design system documentation
- Data folder README - Comprehensive data guide
- Refactoring documentation - Data organization changes

#### ✅ Data Management
- Data refactoring (74 → 48 files)
- Unified naming convention
- Archive system for old files
- Git-based versioning (no date stamps in filenames)
- Data integrity profiles
- Credibility scoring methodology documentation

---

## ✅ Completed Features (v0.2.0-alpha)

### Core Application Features
1. **✅ Data Loader** - Complete
   - Refactored to use new file structure
   - Entity type inference from names
   - Handles all 5 data types (entities, awards, money flows, relationships, FOIA)
   - Robust error handling

2. **✅ Complete Contribution System** - Complete
   - Entity contributions with GitHub PR automation
   - Money Flow contributions
   - Award contributions
   - FOIA Target contributions
   - All 4 types fully functional

3. **✅ Network Visualization** - Complete
   - Interactive entity relationship graph using react-force-graph-2d
   - Color-coded by entity type (Corporation, Government Agency, etc.)
   - Dynamic legend showing only existing types
   - Zoom controls (Fit to View, Center, Zoom In, Zoom Out)
   - Node sizing by connection count
   - Smart entity type inference
   - Collision detection and optimal spacing
   - Click-to-zoom node interaction

4. **✅ Advanced Search & Filtering** - Complete
   - Entity type filters
   - Amount range filters (min/max)
   - Date range filters
   - Real-time filter application
   - Filter UI integrated into Browse page

5. **✅ Export Functionality** - Complete
   - Export entities to CSV/JSON
   - Export money flows to CSV/JSON
   - Export awards to CSV/JSON
   - Export all data types

6. **✅ Bug Fixes Resolved** - Complete
   - Database dependency injection
   - Circular import issues
   - SPA routing for React Router
   - Entity name loading (CSV column mapping)
   - Network graph node/edge mismatch
   - Entity type inference

7. **✅ UI/UX Enhancements** - Complete
   - Light/dark mode theming
   - Purple & gold color scheme
   - Custom favicon (PRHLogo.png)
   - Professional dashboard with stats cards
   - Responsive design
   - Loading states and error handling

---

## Roadmap - Remaining Features

### Priority 2: Enhanced Visualization & Analysis

#### Additional Visualizations (Planned)
- **Financial Flow Graph:**
  - Money flow visualization with edge weights (transaction amounts)
  - Time-based animation showing flow evolution
  - Filter by amount and date range
- **Timeline Charts:**
  - Award trends over time
  - Spending patterns by agency
  - Historical analysis views
- **Statistical Dashboards:**
  - Spending trends charts
  - Top recipients by amount
  - Agency spending breakdowns
  - Distribution analysis

#### Advanced Analysis Enhancements (Planned)
- **Full-text Search:**
  - Search across all entity fields
  - Fuzzy matching for similar names
  - Search result highlighting
- **Credibility Scoring Display:**
  - Show scoring methodology
  - Display scores in tables
  - Sort/filter by score
- **Export Graph Visualizations:**
  - Save network graph as PNG/SVG
  - Export filtered datasets
  - Generate PDF reports

#### Data Tables Enhancement (Planned)
- **Advanced Pagination:** Virtual scrolling for large datasets
- **Multi-column Sorting:** Complex sort combinations
- **Column Customization:** Show/hide, reorder columns
- **Bulk Operations:** Select multiple rows for batch export

### Priority 3: Polish & Quality

#### Testing
- **Unit Tests:**
  - Backend API endpoints
  - Data loader functions
  - Database operations
- **Integration Tests:**
  - End-to-end data flow
  - Frontend-backend integration
  - GitHub PR creation workflow
- **E2E Tests:**
  - User workflows (browse → filter → export)
  - Installation process testing
  - Cross-platform compatibility

#### Documentation
- **API Documentation:**
  - OpenAPI/Swagger UI
  - Endpoint descriptions
  - Request/response examples
- **User Guide:**
  - How to navigate the application
  - Understanding data sources
  - Interpreting credibility scores
  - Contributing data
- **Developer Guide:**
  - Architecture overview
  - Setup for development
  - Contributing code
  - Data update process

#### Performance Optimization
- **Caching:**
  - Redis for API responses (optional)
  - In-memory caching for repeated queries
- **Query Optimization:**
  - Database indexes
  - Efficient joins
  - Pagination at database level
- **Frontend Optimization:**
  - Code splitting
  - Lazy loading
  - Memoization
  - Virtual scrolling for large tables

### Priority 4: Deployment & Distribution

#### Export Enhancements
- **PDF Improvements:**
  - Better formatting
  - Include charts/graphs
  - Custom report templates
- **Additional Formats:**
  - Excel with formatting
  - Markdown reports

#### GitHub Integration Testing
- **Contribution Workflow:**
  - Test PR creation end-to-end
  - Validate data submission format
  - Review process documentation
- **Data Validation:**
  - Schema validation on submission
  - Duplicate detection
  - Source verification

#### Data Refresh Pipeline
- **Automated Updates:**
  - Scripts to fetch latest data from sources
  - Scheduled runs (monthly/quarterly)
  - Incremental updates vs full refresh
- **Data Validation:**
  - Integrity checks
  - Deduplication
  - Format normalization

#### Hosting & Deployment
- **Docker Support:**
  - Dockerfile for backend
  - Docker Compose for full stack
  - Environment configuration
- **Hosting Options:**
  - Self-hosted instructions
  - Cloud deployment (AWS, Azure, GCP)
  - Heroku/Render for easy hosting
- **CI/CD:**
  - GitHub Actions workflows
  - Automated testing
  - Release automation

---

## Technical Specifications

### API Endpoints

**Base URL:** `http://localhost:8000` (default)

#### Data Endpoints
- `GET /api/data/entities` - List all entities
  - Response: `[{entity_id, display_name, normalized_name, entity_type}]`
- `GET /api/data/awards` - List all awards
  - Query params: `?limit=100&offset=0&agency=...`
- `GET /api/data/money-flows` - List money flows
  - Query params: `?min_amount=0&source=...&target=...`
- `GET /api/data/relationships` - List entity relationships
- `GET /api/data/foia-targets` - List FOIA targets

#### Analysis Endpoints
- `GET /api/analysis/network` - Network graph data
  - Response: `{nodes: [], edges: []}`
- `GET /api/analysis/flows` - Financial flow analysis
  - Response: `{flows: [], summary: {}}`

#### Export Endpoints
- `POST /api/export/csv` - Export data as CSV
  - Body: `{entity_type: "entities"|"awards"|..., filters: {}}`
- `POST /api/export/json` - Export as JSON
- `POST /api/export/pdf` - Generate PDF report
  - Body: `{title, sections: [], include_charts: bool}`

#### Contribution Endpoints
- `POST /api/contribute/submit` - Submit new data
  - Body: `{data_type, data, source, contributor_info}`
  - Creates GitHub PR automatically

### Frontend Component Architecture

```
src/
├── main.tsx              - Entry point
├── App.tsx               - Main layout, routing, theme
├── components/
│   ├── LegalDisclaimer   - Disclaimer modal
│   └── ThemeToggle       - Light/dark mode toggle
├── pages/
│   ├── Dashboard         - Home page
│   ├── Browse            - Data tables
│   ├── Analysis          - Visualizations
│   ├── Export            - Export interface
│   ├── Contribute        - Data submission
│   └── About             - Project info
├── services/
│   └── api.ts            - API client
├── types/
│   └── index.ts          - TypeScript types
└── styles/
    └── theme.css         - CSS variables
```

### Configuration

**config.yaml:**
```yaml
app:
  name: "Project RawHorse"
  version: "1.0.0"

server:
  host: "127.0.0.1"
  port_range: [8000, 8100]
  auto_open_browser: true

database:
  path: "data/prh.db"

data_sources:
  entities_dir: "data/entities"
  financial_dir: "data/financial"
  foia_dir: "data/foia"
  reference_dir: "data/reference"
  evidence_dir: "data/evidence"
  visualizations_dir: "data/visualizations"
  scripts_dir: "data/scripts"
  docs_dir: "data/docs"

github:
  repository_url: "https://github.com/consciousenergy/UAPUFOData"
  branch_prefix: "contribution"
  enabled: true

features:
  github_integration: true
  advanced_analysis: true
  export_pdf: true
```

---

## Development Roadmap

### Phase 1: Stabilization (Current)
**Timeline:** 1-2 weeks  
**Goals:**
- Fix data loader for new structure ✓
- Test database loading ✓
- Verify all API endpoints ✓
- Test frontend integration ✓
- Prepare for GitHub push ✓

### Phase 2: Core Features
**Timeline:** 4-6 weeks  
**Goals:**
- Implement network visualization (D3.js)
- Add advanced filtering and search
- Display credibility scoring
- Enhance data tables (pagination, sorting)
- Add statistical charts

### Phase 3: Quality & Testing
**Timeline:** 2-3 weeks  
**Goals:**
- Write unit tests (>80% coverage)
- Integration testing
- E2E testing
- Performance optimization
- Documentation completion

### Phase 4: Distribution
**Timeline:** 2-3 weeks  
**Goals:**
- Finalize cross-platform builds
- Test installation on all platforms
- Create release packages
- Setup hosting options
- Launch public release

---

## Success Metrics

### Technical
- [ ] Backend starts without errors
- [ ] Database loads all data successfully
- [ ] All API endpoints return valid data
- [ ] Frontend builds without errors
- [ ] Application runs on Windows, macOS, Linux
- [ ] Installation completes in < 10 minutes

### User Experience
- [ ] Non-technical users can install in 1-click
- [ ] Data browsing is intuitive
- [ ] Export works reliably
- [ ] Visualizations are informative
- [ ] Dark mode works properly

### Data Quality
- [ ] All data traceable to public sources
- [ ] No PII or classified content
- [ ] Credibility scores documented
- [ ] Data integrity profiles maintained
- [ ] Regular updates possible

### Community
- [ ] GitHub repository active
- [ ] Clear contribution guidelines
- [ ] Responsive to issues/PRs
- [ ] Growing user base
- [ ] Active discussions

---

## Constraints & Requirements

### Legal
- **License:** GNU AGPL v3 (copyleft, network use covered)
- **Data:** Public sources only, no classified/PII
- **Disclaimer:** Strong user responsibility clause
- **Attribution:** Cite all data sources

### Technical
- **Python:** 3.10+ required
- **Node.js:** 18+ required
- **Database:** SQLite (local, portable)
- **Browser:** Modern browsers (Chrome, Firefox, Edge, Safari)

### Performance
- **Startup:** < 10 seconds
- **Data Load:** < 30 seconds for full dataset
- **API Response:** < 1 second for most queries
- **Frontend:** < 3 seconds initial load

### Accessibility
- **Installation:** 1-click for non-technical users
- **UI:** Keyboard navigation
- **Contrast:** WCAG AA compliant
- **Documentation:** Clear, non-technical language

---

## Risk Assessment

### Technical Risks
- **Data Loader:** May fail with schema changes
  - Mitigation: Comprehensive testing, schema validation
- **Cross-Platform:** Different behaviors on OS
  - Mitigation: Test on all platforms, use CI/CD
- **Performance:** Large datasets may slow UI
  - Mitigation: Pagination, virtualization, caching

### Legal Risks
- **Data Misuse:** Users may misinterpret data
  - Mitigation: Strong disclaimer, clear attribution
- **Copyright:** Third-party data use
  - Mitigation: Public domain sources only
- **Privacy:** Accidental PII inclusion
  - Mitigation: Data review process, no manual PII entry

### Community Risks
- **Low Adoption:** Users don't find it useful
  - Mitigation: User feedback, feature requests
- **Maintenance:** Becomes too complex to maintain
  - Mitigation: Clean architecture, documentation
- **Data Quality:** Contributions are low quality
  - Mitigation: Review process, validation

---

## Appendix

### Key Entities Tracked
- Peraton (and 5 subsidiaries)
- Veritas Capital (private equity)
- Lockheed Martin
- Huntington Ingalls Industries (HII)
- NGA (National Geospatial-Intelligence Agency)
- DCSA (Defense Counterintelligence and Security Agency)
- 30+ additional entities

### File Structure Reference
See `data/README.md` for comprehensive data organization documentation.

### Changelog
- **2025-11-11:** Data refactoring (74 → 48 files)
- **2025-11-11:** Initial data organization from UAPUFOData folder
- **2025-11-11:** Theming and branding implementation
- **2025-11-11:** PRD creation

---

**Document Owner:** Project RawHorse Core Team  
**Next Review:** After Phase 1 completion  
**Questions:** Open GitHub issue or discussion

