# Project RawHorse — Architecture Guide

**Version:** v0.4.0  
**Last Updated:** February 2026

This document describes the high-level architecture, data flow, and key design decisions of Project RawHorse. It is intended for developers who want to contribute code, understand how the system works, or adapt it for their own research.

---

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                        User                             │
│                     (Browser)                           │
└───────────────┬─────────────────────────┬───────────────┘
                │ Production (port 8000)  │ Dev (port 5173)
                ▼                         ▼
┌───────────────────────┐   ┌───────────────────────────┐
│   FastAPI Backend      │   │   Vite Dev Server          │
│   (Python 3.10+)       │◄──│   (React + TypeScript)     │
│                        │   │   Proxies /api → :8000     │
│   Serves:              │   └───────────────────────────┘
│   - REST API (/api/*)  │
│   - Static frontend    │
│   - Logo assets        │
└──────────┬─────────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌──────────┐ ┌──────────────┐
│ SQLite   │ │ PostgreSQL   │
│ (default)│ │ (production) │
│ data/    │ │ via Docker   │
│ prh.db   │ └──────────────┘
└──────────┘
     ▲
     │ Ingestion
┌────┴─────────────┐      ┌──────────────────┐
│ CSV Data Files   │      │ GitHub API       │
│ data/entities/   │      │ (Contributions)  │
│ data/financial/  │      └──────────────────┘
│ data/foia/       │
│ data/reference/  │
└──────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Local-first** | All processing on user's machine | Privacy, no server dependency, works offline |
| **Default database** | SQLite | Zero-config, portable, single-file backup |
| **Production database** | PostgreSQL (optional) | Connection pooling, concurrent access, VPS scale |
| **Backend framework** | FastAPI | Async, auto-generated OpenAPI docs, Pydantic validation |
| **Frontend framework** | React 18 + TypeScript + Vite | Fast HMR, type safety, modern tooling |
| **Packaging** | PyInstaller | Cross-platform executables for non-technical users |
| **Auth** | JWT (optional, disabled by default) | Secure write operations without requiring auth for local read-only use |
| **Contributions** | GitHub PR automation (PyGithub) | Leverages existing code review workflow |

---

## Frontend Architecture

### Entry Point

`frontend/src/main.tsx` → renders `<App />` wrapped in React Router.

### Pages (Route → Component)

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Dashboard` | Overview statistics, quick-access cards |
| `/browse` | `Browse` | Tabbed data tables (Entities, Money Flows, Awards, FOIA) |
| `/analysis` | `AnalysisOverview` | Visualization cards linking to sub-pages |
| `/analysis/network` | `NetworkGraphPage` | Force-directed entity relationship graph |
| `/analysis/sankey` | `SankeyDiagramPage` | Financial flow Sankey diagram |
| `/analysis/pyramid` | `PyramidPage` | Intelligence Stack pyramid (L1–L6) |
| `/analysis/foia` | `FoiaTargetsPage` | FOIA targets with quality scoring and filters |
| `/export` | `Export` | CSV, JSON, PDF download |
| `/contribute` | `Contribute` | GitHub PR contribution form |
| `/about` | `About` | Project info, attribution, data sources |

### Key Components

| Component | Purpose |
|-----------|---------|
| `SearchBar` | Global search with debounced API calls, suggestions, recent history |
| `NetworkGraph` | Interactive force-directed graph (react-force-graph-2d) |
| `SankeyDiagram` | D3-based Sankey flow visualization |
| `PyramidVisualization` | L1–L6 trapezoid hierarchy with drill-down |
| `IntelStackFilter` | Toggle filter for entity hierarchy levels |

### State Management

- **React Context** (`contexts/`) for global state (theme, auth)
- **URL search params** for Browse tab state, search terms, highlighted rows
- **localStorage** for user preferences (recent searches, recent clicked results)
- **Component-local state** for most UI state (via `useState`, `useReducer`)

### API Layer

`frontend/src/services/api.ts` — centralized Axios client with base URL detection:
- Development: proxied via Vite (`vite.config.ts` proxy to `:8000`)
- Production: same origin (backend serves the built frontend from `backend/static/`)

---

## Backend Architecture

### Entry Point

`backend/main.py` — FastAPI application with CORS, static files, rate limiting, and router registration.

### Routers

| Router File | Prefix | Endpoints | Purpose |
|------------|--------|-----------|---------|
| `data.py` | `/api/data` | 10 | CRUD operations for entities, flows, awards, FOIA |
| `search.py` | `/api` | 2 | Global search with fuzzy matching and analytics |
| `analysis.py` | `/api/analysis` | 13 | Graph data, Sankey, pyramid, timeline, financial summaries |
| `export_router.py` | `/api/export` | 6 | CSV, JSON, PDF exports |
| `contribute.py` | `/api/contribute` | 5 | GitHub PR creation for data contributions |
| `auth_router.py` | `/api/auth` | 4 | JWT login, refresh, status |

**Total: ~45 API endpoints.** See [API_REFERENCE.md](API_REFERENCE.md) for full documentation.

### Database Layer

`backend/database.py` — SQLAlchemy 2.0 with dual-engine support:

```
config.yaml → database.path
                   │
          ┌────────┴─────────┐
          │ DATABASE_URL env? │
          │     (check)       │
          └─┬──────────┬─────┘
     PostgreSQL     SQLite
     (if set)     (default)
```

**Models:**
- `Entity` — organizations, agencies, contractors (with `intel_stack_level`)
- `MoneyFlow` — financial transactions between entities
- `Award` — federal contracts and grants
- `FOIATarget` — suggested FOIA requests with quality scoring
- `Relationship` — entity-to-entity connections
- `MaterialsFlow` — technology/materials transfer tracking
- `DataVersion` — data version tracking for refresh operations
- `SearchLog` — search analytics

### Configuration

`config.yaml` (project root) — single source of truth for:
- App name and version
- Server host and port range
- Database path
- Data source directories
- GitHub integration settings
- Feature flags

---

## Data Flow

### 1. Data Ingestion (Startup)

```
CSV files (data/entities/, data/financial/, data/foia/)
    │
    ▼
backend/data_loader.py
    │ Reads CSVs, normalizes, deduplicates
    ▼
SQLAlchemy ORM
    │ Inserts into SQLite/PostgreSQL
    ▼
data/prh.db (or PostgreSQL)
```

### 2. User Query Flow

```
User types in SearchBar
    │
    ▼ (debounced 200ms)
GET /api/search?q=...
    │
    ▼
backend/routers/search.py
    │ Multi-word search, alias expansion,
    │ fuzzy matching (rapidfuzz), amount parsing
    ▼
SQLAlchemy query across Entity, Award, MoneyFlow, FOIATarget
    │
    ▼
JSON response → React renders results
    │
    ▼ (user clicks result)
Navigate to /browse?tab=entities&search=...&highlight=123
    │
    ▼
Browse component scrolls to row, applies flash animation
```

### 3. Contribution Flow

```
User fills form on /contribute
    │
    ▼
POST /api/contribute/entity (+ X-GitHub-Token header)
    │
    ▼
backend/routers/contribute.py
    │ Validates data via Pydantic model
    │ Creates branch on GitHub fork
    │ Adds CSV entry
    │ Opens pull request
    ▼
GitHub PR created for review
```

### 4. Data Enrichment Pipeline

```
data/scripts/
    │
    ├── entity_recognition.py    (spaCy NER)
    ├── amount_extraction.py     (financial parsing)
    ├── date_extraction.py       (date normalization)
    ├── validate_flows.py        (quality gates)
    ├── enrich_entity_flows.py   (main enrichment)
    ├── extract_materials_flows.py
    ├── combine_all_data.py      (unified loading)
    └── compliance_filter.py     (sensitive data filtering)
```

---

## Directory Structure

```
ProjectRawHorse/
├── backend/                  # FastAPI server
│   ├── main.py               # App entry, CORS, middleware, routers
│   ├── database.py           # SQLAlchemy models, engine, session
│   ├── data_loader.py        # CSV → database ingestion
│   ├── auth.py               # JWT authentication module
│   ├── routers/              # API endpoint handlers
│   │   ├── data.py           # Entity, flow, award, FOIA CRUD
│   │   ├── search.py         # Global search + analytics
│   │   ├── analysis.py       # Graph, Sankey, pyramid, timeline
│   │   ├── export_router.py  # CSV, JSON, PDF exports
│   │   ├── contribute.py     # GitHub PR automation
│   │   └── auth_router.py    # Login, refresh, status
│   ├── models/
│   │   └── schemas.py        # Pydantic response models
│   ├── services/
│   │   └── github_service.py # PyGithub integration
│   ├── static/               # Built frontend (production only)
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── main.tsx          # Entry point
│   │   ├── App.tsx           # Router + layout
│   │   ├── pages/            # Route pages
│   │   ├── components/       # Reusable UI (SearchBar, Pyramid, etc.)
│   │   ├── services/         # API client (api.ts)
│   │   ├── contexts/         # React Context providers
│   │   ├── types/            # TypeScript interfaces
│   │   └── styles/           # Global styles
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts        # Dev server proxy config
├── data/                     # Research data
│   ├── entities/             # Entity CSV files
│   ├── financial/            # Award and money flow CSVs
│   ├── foia/                 # FOIA target CSVs
│   ├── reference/            # Reference data (hierarchy, aliases)
│   ├── evidence/             # Supporting evidence
│   ├── scripts/              # Data ingestion and enrichment
│   └── prh.db                # SQLite database (generated)
├── docker/                   # Docker deployment
│   ├── Caddyfile             # Reverse proxy config
│   ├── init-db.sql           # PostgreSQL init
│   └── .env.example          # Docker environment template
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # This file
│   ├── DEVELOPER_GUIDE.md    # Dev setup and workflow
│   ├── API_REFERENCE.md      # All API endpoints
│   ├── development/          # Plans, roadmaps, changelogs
│   ├── setup/                # Installation guides
│   └── design/               # UI/UX design docs
├── .github/
│   ├── workflows/
│   │   └── build-releases.yml  # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/       # Bug, feature, data contribution templates
│   └── FUNDING.yml           # Sponsorship links
├── config.yaml               # Application configuration
├── START.bat / START.sh      # One-click launchers
├── UNINSTALL.bat / .sh       # One-click uninstallers
├── docker-compose.yml        # Production Docker
├── docker-compose.dev.yml    # Development Docker
└── build_executable.py       # PyInstaller build script
```

---

## Deployment Modes

### 1. Local Development

```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev  # Port 5173, proxies /api → 8000
```

### 2. Local Production (One-Click)

```bash
# Windows
START.bat

# macOS/Linux
./START.sh
```

Backend serves built frontend from `backend/static/` at port 8000.

### 3. Docker Production

```bash
docker-compose up -d
```

Services: Backend, Frontend (Nginx), PostgreSQL, Redis, Caddy (HTTPS).

### 4. Executable (PyInstaller)

```bash
python build_executable.py
# Output: dist/RawHorse/RawHorse.exe
```

Self-contained executable with embedded backend, frontend, and data.

---

## Security Model

- **Local-first**: No external server communication except GitHub (contributions only)
- **No telemetry**: Zero analytics, tracking, or data collection
- **Optional JWT auth**: Disabled by default; enable for multi-user deployments
- **Encrypted token storage**: GitHub tokens encrypted at rest
- **CORS**: Configured for same-origin in production, localhost in development
- **Rate limiting**: Applied to auth and search endpoints
- **Input validation**: Pydantic models on all API inputs
- **Compliance filtering**: Automatic filtering of potentially sensitive data in enrichment pipeline

---

## Further Reading

- [Developer Guide](DEVELOPER_GUIDE.md) — Setup, run, build, test
- [API Reference](API_REFERENCE.md) — All 45 endpoints documented
- [Contributing](../CONTRIBUTING.md) — How to contribute code and data
- [PRD](PRD.md) — Product Requirements Document
