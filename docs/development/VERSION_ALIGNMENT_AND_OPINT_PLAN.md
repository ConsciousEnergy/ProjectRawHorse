# Plan: Version Alignment to v0.4.0 & OPINT Public Development Overhaul

**Created:** February 11, 2026  
**Status:** Draft — awaiting review  
**Goal:** Resolve version number inconsistencies across the codebase, then comprehensively improve Project RawHorse's public-facing documentation, developer experience, and onboarding so that any researcher, developer, or citizen investigator can quickly understand, use, and contribute to the project.

---

## Part 1 — Version Alignment (v0.3.x → v0.4.0)

### 1.1 Problem Statement

The project currently has two version identities running in parallel:

| Source | Version |
|--------|---------|
| `config.yaml` (single source of truth) | **0.4.0** |
| Backend API (`/version`) | 0.4.0 (reads config) |
| `CHANGELOG_v0.4.0.md` | v0.4.0 (Jan 2026) — Gerb's Hidden Wing, Intel Pyramid, Docker |
| `README.md` Version History | v0.4.0 listed |
| Git branch (current) | `PRH_v0.3.2Beta` / `PRH_v0.3.3Beta` |
| `CHANGELOG_v0.3.3Beta.md` | v0.3.3 Beta — Search UX, CI fixes, Uninstall |
| `GIT_PUSH_COMMANDS.md` | v0.3.3 Beta instructions |
| `FEATURE_ROADMAP.md` | Says "v0.3.0-dev" |
| `docs/PROJECT_SUMMARY.md` | Says "v0.2.0-alpha" |
| `frontend/package.json` | "1.0.0" (unrelated) |
| README Version History (bottom) | Lists "v1.0.0 (2025-11-11)" for initial release |

**Decision:** Consolidate all work (v0.3.0 through v0.3.3 Beta) into the existing v0.4.0 release. The v0.4.0 CHANGELOG already exists and documents major features. The 0.3.x Beta releases were incremental development branches leading to this release.

### 1.2 Changes Required

#### A. Update `CHANGELOG_v0.4.0.md`
- Merge the contents of v0.3.1, v0.3.2 Beta, and v0.3.3 Beta CHANGELOGs into the v0.4.0 CHANGELOG as subsections under a new "Development History" or "Incremental Changes" section.
- Add: Search UX Enhancements (4-6), CI/build workflow fixes, One-Click Uninstall feature.
- Update the release date from "January 2026" to "February 2026".

#### B. Update `README.md` Version History
- Fix the initial release entry: change `v1.0.0 (2025-11-11)` to `v0.2.0 (2025-11-11)` (matching the actual release notes).
- Add missing entries for v0.2.1, v0.3.0, v0.3.1.
- Update v0.4.0 entry to include Search UX, CI fixes, Uninstall, and change date to February 2026.
- Fix broken `[PRD.md](PRD.md)` link → `[PRD.md](docs/PRD.md)`.
- Fix clone URL: `cd project-rawhorse` → `cd ProjectRawHorse`.
- Fix support links that use `project-rawhorse` slug.

#### C. Update `GIT_PUSH_COMMANDS.md`
- Add a v0.4.0 section with branch `PRH_v0.4.0`, tag `v0.4.0`, and push commands.
- Mark 0.3.x sections as historical.

#### D. Update `docs/development/FEATURE_ROADMAP.md`
- Change header version from "v0.3.0-dev" to "v0.4.0".
- Move completed features (Advanced Search, Intelligence Stack, Docker, Uninstall) to the "Completed" section.
- Update date from November 2025 to February 2026.

#### E. Update `docs/PROJECT_SUMMARY.md`
- Change version from "v0.2.0-alpha" to "v0.4.0".

#### F. Update `frontend/package.json`
- Change `"version": "1.0.0"` → `"version": "0.4.0"` for consistency.

#### G. Git branch and tag
- Create branch `PRH_v0.4.0` (or rename current branch).
- Create annotated tag `v0.4.0`.
- The 0.3.x Beta CHANGELOGs remain in the repo as historical records (no deletion).

#### H. Fix `build-releases.yml` artifact names
- Rename `UAP-Data-Explorer-*` artifacts to `Project-RawHorse-*`.

---

## Part 2 — OPINT Public Development Overhaul

### 2.1 Onboarding (README + Getting Started)

#### A. README.md Overhaul
**Current issues:** Wrong clone URL, wrong `cd` target, missing version entries, broken PRD link, screenshots from Nov 2025 only.

**Changes:**
1. **Hero section** — Keep badges; add a 1-sentence "What is OPINT?" explanation after the project description:
   > OPINT (Open Intelligence) is the practice of building transparent, publicly-auditable intelligence databases. Project RawHorse is an OPINT tool for UAP research.
2. **Quick Start** — Verify all commands work, fix clone URL to `ConsciousEnergy/ProjectRawHorse.git`, fix `cd` to `ProjectRawHorse`.
3. **Screenshots** — Add updated screenshots showing Pyramid view, Sankey diagram, and Search UX. (These can be GitHub user-attachment URLs or committed to `docs/screenshots/`.)
4. **"What Can I Do With This?"** section — Add a short (5-bullet) "use cases" block aimed at non-developers:
   - Browse UAP-related entities and their connections
   - Explore federal award money flows with interactive Sankey diagrams
   - View the intelligence organizational pyramid
   - Export data for your own research (CSV, JSON, PDF)
   - Contribute new data via the built-in GitHub integration
5. **OPINT Philosophy** section — Short paragraph explaining the open-source intelligence approach, citing transparency, reproducibility, and community verification.
6. **Links section** — Fix all broken links (PRD, DISCLAIMER, support URLs).

#### B. First-Run Experience Documentation
- Add a `docs/FIRST_RUN.md` walkthrough (or section in INSTALL_GUIDE.md) that explains what happens after the user double-clicks `START.bat`:
  - What gets installed (Python venv, npm packages)
  - What the loading screen means
  - Where data lives (`data/prh.db`)
  - How to navigate the Dashboard, Browse, Analysis, and Contribute tabs
  - 3-5 screenshots of each main page with callouts

### 2.2 Contributing Guide Overhaul

#### A. Fix `CONTRIBUTING.md`
**Current issues:** Wrong project name ("UAP Data Explorer"), wrong clone URL (placeholder), wrong data paths (`UAPUFOResearch/`), outdated (Nov 2025).

**Changes:**
1. Rename title to "Contributing to Project RawHorse".
2. Fix all repository URLs to `ConsciousEnergy/ProjectRawHorse.git`.
3. Fix data paths: `UAPUFOResearch/UAPUFOResearch/` → `data/entities/`, `data/financial/`, etc.
4. Fix application name references: "UAP Data Explorer" → "Project RawHorse".
5. Update "last updated" date to February 2026.
6. Add a **"Your First Contribution"** section:
   - Fork the repo
   - Clone and run `START.bat`/`START.sh`
   - Pick a "good first issue" from GitHub Issues
   - Make your change, run tests, submit PR
7. Add **"Data Contribution Workflow"** with clear steps for non-coders:
   - Use the in-app Contribute tab
   - What happens behind the scenes (GitHub PR automation)
   - What reviewers look for (source verification, data format)

#### B. Add `CODE_OF_CONDUCT.md`
- Use [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) as the base.
- Customize contact method (email or GitHub Discussions).
- Link from CONTRIBUTING.md's "Code of Conduct" section.

#### C. Add `SECURITY.md`
- Vulnerability reporting process (email, not public issues).
- Scope: what counts as a security issue (auth bypass, data injection, etc.).
- Response timeline commitment (e.g., "We aim to acknowledge within 48 hours").

#### D. Replace `PULL_REQUEST_TEMPLATE.md`
**Current issue:** The file describes a specific past PR instead of being a generic template.

**Replacement structure:**
```markdown
## Summary
<!-- What does this PR do? 1-3 sentences. -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Data contribution
- [ ] Documentation
- [ ] CI/Build
- [ ] Refactor

## Changes
<!-- Bullet list of key changes -->

## Testing
<!-- How did you verify this works? -->
- [ ] Local dev server tested
- [ ] Frontend builds without errors (`npm run build`)
- [ ] No new linter warnings introduced

## Screenshots (if UI change)
<!-- Before/after screenshots -->

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I've updated relevant documentation
- [ ] I've tested on at least one platform (Windows/Mac/Linux)
```

#### E. Add GitHub Issue Template for "OPINT Data Request"
- New template for requesting enrichment from specific public databases.
- Fields: database name, URL, data type, relevance to UAP research, estimated record count.

### 2.3 Architecture Documentation

#### A. Create `docs/ARCHITECTURE.md`
A single-page developer guide covering:

1. **System Overview Diagram** (text-based Mermaid diagram):
   ```
   User → Browser → React Frontend (Vite) → FastAPI Backend → SQLite/PostgreSQL
                                              ↕
                                    CSV data files (data/)
                                              ↕
                                    GitHub API (contributions)
   ```

2. **Frontend Architecture**:
   - Entry point: `frontend/src/main.tsx`
   - Pages: Dashboard, Browse, Analysis (with sub-pages), Export, Contribute, About
   - Key components: SearchBar, PyramidVisualization, NetworkGraph, SankeyDiagram, IntelStackFilter
   - State management: React Context (`contexts/`)
   - API layer: `services/api.ts`
   - Routing: React Router v6

3. **Backend Architecture**:
   - Entry point: `backend/main.py` (FastAPI)
   - Routers: `data.py`, `search.py`, `analysis.py`, `export_router.py`, `contribute.py`, `auth_router.py`
   - Database: `database.py` (SQLAlchemy 2.0, SQLite default, PostgreSQL optional)
   - Config: `config.yaml` (read at startup)
   - Data ingestion: `data/scripts/` pipeline

4. **Data Flow**:
   - CSV → `data/scripts/` ingestion → SQLite `data/prh.db`
   - User query → FastAPI → SQLAlchemy → JSON response → React renders
   - Contribution → React form → FastAPI → GitHub API → PR created

5. **Key Decisions & Why**:
   - Why local-first (privacy, no server dependency)
   - Why SQLite default (zero-config, portable) with PostgreSQL option (production scale)
   - Why FastAPI (async, auto-docs, Pydantic validation)
   - Why React + Vite (fast HMR, modern tooling)

6. **Directory Structure** (annotated tree):
   ```
   ProjectRawHorse/
   ├── backend/           # FastAPI server
   │   ├── main.py        # App entry, CORS, routers
   │   ├── database.py    # SQLAlchemy models & session
   │   ├── routers/       # API endpoints by domain
   │   └── static/        # Built frontend (production)
   ├── frontend/          # React + Vite
   │   ├── src/pages/     # Route pages
   │   ├── src/components/ # Reusable UI
   │   └── src/services/  # API client
   ├── data/              # Research data (CSV, DB)
   │   ├── entities/      # Entity CSV files
   │   ├── financial/     # Award & money flow CSVs
   │   ├── foia/          # FOIA target CSVs
   │   └── scripts/       # Data ingestion scripts
   ├── docker/            # Docker deployment
   ├── docs/              # All documentation
   ├── config.yaml        # App configuration
   ├── START.bat/.sh      # One-click launcher
   └── UNINSTALL.bat/.sh  # One-click uninstaller
   ```

#### B. Create `docs/API_REFERENCE.md`
- Document all backend API endpoints with request/response examples.
- Can be auto-generated from FastAPI's OpenAPI schema, but a human-readable version is valuable.
- Group by router: Data, Search, Analysis, Export, Contribute, Auth.
- Include example `curl` commands.

#### C. Create `docs/DEVELOPER_GUIDE.md`
- **Prerequisites**: Python 3.10+, Node.js 20+, Git
- **Dev Setup**:
  ```bash
  git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
  cd ProjectRawHorse
  python -m venv venv && source venv/bin/activate  # (or venv\Scripts\activate on Windows)
  pip install -r requirements.txt
  cd frontend && npm install && cd ..
  ```
- **Running in Dev Mode**:
  - Backend: `cd backend && uvicorn main:app --reload --port 8000`
  - Frontend: `cd frontend && npm run dev` (port 5173, proxies to 8000)
- **Running Tests**: (document test structure when tests exist)
- **Building for Production**:
  - `cd frontend && npm run build`
  - Copy `frontend/dist/*` → `backend/static/`
  - Or use `build-and-deploy-frontend.bat`
- **Docker Development**: `docker-compose -f docker-compose.dev.yml up`
- **Common Issues & Solutions**: Port already in use, venv not found, npm build OOM, etc.

### 2.4 Miscellaneous Fixes

| Issue | Fix |
|-------|-----|
| `docs/setup/INSTALLATION.md` mentions Git LFS | Remove Git LFS references (removed in v0.4.0) |
| `docs/README.md` links to `DISCLAIMER.md` but it's in root | Fix link to `../DISCLAIMER.md` |
| `FEATURE_ROADMAP.md` is outdated | Update completed features, version, date |
| `QUICKSTART.md` frontend port inconsistency | Ensure 5173 (Vite dev) is documented consistently |
| `build-releases.yml` artifact names | Change `UAP-Data-Explorer-*` → `Project-RawHorse-*` |
| `docs/screenshots/` referenced but doesn't exist | Create directory, add key screenshots |
| Missing `RELEASE_NOTES_v0.3.0.md` (referenced) | Create a brief one, or fix the broken reference |

---

## Part 3 — Implementation Order

### Phase 1: Version Alignment (can be done in one session)
1. Update `CHANGELOG_v0.4.0.md` with merged 0.3.x content
2. Update `README.md` (version history, broken links, clone URL)
3. Update `config.yaml` version if needed (already 0.4.0 — confirm)
4. Update `frontend/package.json` version to 0.4.0
5. Update `GIT_PUSH_COMMANDS.md` with v0.4.0 instructions
6. Update `FEATURE_ROADMAP.md` version and completed features
7. Update `PROJECT_SUMMARY.md` version
8. Fix `build-releases.yml` artifact names
9. Create branch `PRH_v0.4.0`, tag `v0.4.0`, push

### Phase 2: Critical Documentation Fixes (one session)
10. Rewrite `CONTRIBUTING.md` (fix project name, URLs, paths)
11. Replace `PULL_REQUEST_TEMPLATE.md` with generic template
12. Add `CODE_OF_CONDUCT.md`
13. Add `SECURITY.md`
14. Fix `docs/setup/INSTALLATION.md` (remove Git LFS)
15. Fix `docs/README.md` DISCLAIMER link
16. Fix QUICKSTART.md port consistency

### Phase 3: Architecture & Developer Docs (one session)
17. Create `docs/ARCHITECTURE.md`
18. Create `docs/DEVELOPER_GUIDE.md`
19. Create `docs/API_REFERENCE.md` (can be generated from FastAPI OpenAPI)
20. Add GitHub Issue Template for "OPINT Data Request"

### Phase 4: Onboarding Polish (one session)
21. Add README "What Can I Do?" and "OPINT Philosophy" sections
22. Add updated screenshots (Pyramid, Sankey, Search)
23. Create `docs/FIRST_RUN.md` walkthrough
24. Create `docs/screenshots/` with key images
25. Final cross-link audit across all docs

---

## Estimated Effort

| Phase | Est. Time | Dependencies |
|-------|-----------|-------------|
| Phase 1: Version Alignment | 1-2 hours | None |
| Phase 2: Critical Doc Fixes | 2-3 hours | Phase 1 |
| Phase 3: Architecture Docs | 2-4 hours | Phase 1 |
| Phase 4: Onboarding Polish | 1-2 hours | Phase 2-3 |
| **Total** | **6-11 hours** | Sequential |

---

## Success Criteria

- [ ] A new developer can clone, install, and run the app in under 10 minutes by following README alone
- [ ] All version references across the codebase point to v0.4.0
- [ ] `CONTRIBUTING.md` uses correct project name, URLs, and data paths
- [ ] Architecture diagram exists and is linked from README
- [ ] PR template is generic and useful for any contribution type
- [ ] `CODE_OF_CONDUCT.md` and `SECURITY.md` exist
- [ ] No broken documentation links
- [ ] CI artifact names say "Project-RawHorse" not "UAP-Data-Explorer"
- [ ] A non-technical user can understand what the app does from the README alone

---

## Notes

- The 0.3.x CHANGELOG files are **not deleted** — they serve as historical development records.
- `frontend/package.json` version "1.0.0" is npm's default; changing to "0.4.0" aligns it with the app version.
- The UFO Database Enrichment Plan (`UFO_DATABASE_ENRICHMENT_PLAN.md`) targets v0.4.x and can be implemented after this alignment.
- Screenshots should be committed to `docs/screenshots/` rather than relying solely on GitHub user-attachment URLs (which can break if the issue/PR is deleted).
