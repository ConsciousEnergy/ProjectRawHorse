# Changelog - Project RawHorse v0.3.2 Beta

**Release Date:** February 2026  
**Branch:** PRH_v0.3.2Beta  
**Status:** Ready for PR into main  
**Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse

---

## Overview

This release delivers the **Intelligence Stack Pyramid** overhaul: a hierarchical visualization of entities by intel stack level (L1–L6), with chain-of-command tracing, entity detail panels, and full-width layout. It also fixes federal flows loading, expands L6 program data, and adds **backend search enhancements** (multi-word/alias expansion, amount-aware queries, and fuzzy matching with rapidfuzz).

---

## New Features

### Intelligence Stack Pyramid

- **Dedicated Pyramid page** at `/analysis/pyramid` with trapezoid-tier visualization (L1 narrow top → L6 wide bottom).
- **Entity nodes** per tier: top 8 shown with type-colored circles, “+N more” for overflow.
- **Flow lines** between tiers: gradient bands with width proportional to money flow; hover tooltips for breakdown.
- **Search**: Debounced entity search with autocomplete; results link to pyramid and detail.
- **Level filter**: Toggle L1–L6 visibility via Intelligence Stack filter and legend.
- **Help overlay**: “?” button with keyboard shortcuts (e.g. `/` focus search, Escape close).

### Trace Chain of Command

- **Checkbox** “Trace chain of command” to highlight an entity’s hierarchy (up to L1, down to L6, plus lateral).
- **Chain badge**: When tracing, shows “(N)” for number of entities in the chain.
- **Entity-driven**: Chain is computed from the selected entity (pyramid click or search); includes lateral connections from API.
- **Empty-state hint**: When trace is on and no entity selected, placeholder text explains to select an entity.

### Entity Detail (under search)

- **Detail block** moved from right sidebar to **under the “Search entities (/)”** input in the main column.
- **Empty state**: “Select an entity from the pyramid or search to view details and chain of command” (or trace-specific text when chain mode is on).
- **EntityDetailPanel**: Slide-in content with entity info, chain of command (up/down), relationships by type, money/material flows, links to Network Graph and Browse.
- **Expandable height**: When an entity is selected, detail section grows (max 400px / 45vh) for readability.

### Layout

- **No right sidebar**: Removed `aside.pyramid-page-aside`; all content is in a single column.
- **Top block**: Page header (title, subtitle, search, search results dropdown) plus detail/empty section directly below search.
- **Full-width pyramid**: Controls and pyramid visualization use full content width below the top block.

---

## Data & Backend

### Intel Stack & Hierarchy

- **intel_stack_levels.csv**: Expanded so all entities (entities_master, transcript entities, NRO partners, reference) are assigned L1–L6 where applicable.
- **hierarchy_relationships.csv**: New file with org links (reports_to, subordinate_to, part_of, operates_under, etc.); loaded after entity_relationships.
- **entity_descriptions.csv**: Short descriptions for L1–L2 and selected L3–L4 entities; used by pyramid and entity-detail API (not stored in DB).

### L6 Programs

- **intel_stack_levels.csv**: Added/confirmed L6 entries for program datasets, including:
  - X-37B Orbital Test Vehicle, Guardian Angel Program, Yankee Black (display_name variants for correct matching).
  - Existing L6 entries: Immaculate Constellation, Hidden Wing, TR-3B, Kona Blue, B-21 Raider, X-37B, Project Blue Book, (Program) NRO CSPO Commercial Foundation, etc.

### Backend search enhancements (routers/search.py)

- **Multi-word and alias expansion**: `entity_aliases.csv` plus `AGENCY_ACRONYMS` from data_loader; `expand_query()` returns original + alias terms so e.g. "National Geospatial" matches NGA. All search_* endpoints filter on expanded terms (entities, money_flows, awards).
- **Amount-aware search**: `parse_amount_query()` supports "223", "223M", "1.8B"; search_money_flows and search_awards apply numeric range filters when the query is amount-like.
- **Fuzzy matching (rapidfuzz)**: `calculate_relevance()` uses `fuzz.token_sort_ratio` when appropriate (score ≥70). When ilike returns fewer than `limit` results, a second pass uses `rapidfuzz.process.extract` on entity names / flow source–target / award recipient and merges results with dedupe by id.

### API

- **GET /analysis/intel-stack/pyramid**: Enriched with per-entity `description`, `relationship_count`, `money_flow_total_usd`, `key_connections`, `hierarchy_parent`; single-pass aggregation.
- **GET /analysis/intel-stack/hierarchy?entity_id=**: Returns chain of command (target, chain_up, chain_down, lateral).
- **GET /analysis/intel-stack/entity/{id}/detail**: Full entity detail for drill-down panel.
- **GET /analysis/intel-stack/search?q=**: In-pyramid entity search for the search bar.

---

## Bug Fixes

### Federal Flows Loader (data_loader.py)

- **UNIQUE constraint on money_flows.edge_id**: Multiple rows (e.g. different HHS agencies) truncated to the same `agency[:15]` and produced duplicate `edge_id`s.
- **Fix**: Deduplicate in memory by `(agency, recipient, fiscal_year)`; build unique `edge_id` with row index: `ffr_{idx}_{agency[:20]}_{recipient[:20]}_{fy}` (sanitized). Cap length to 255 chars; fallback to `ffr_{idx}` if needed.

### Frontend

- **PyramidTooltip.tsx**: Removed unused `PADDING` constant to fix TypeScript build.

### Runtime / dependencies

- **ModuleNotFoundError: rapidfuzz**: RUN.bat now runs `pip install -r backend\requirements.txt` (quiet) after activating the venv and before starting the server, so new backend dependencies (e.g. rapidfuzz) are installed automatically when launching via the batch script.

---

## Files Changed (Summary)

### New

- `data/entities/entity_descriptions.csv`
- `data/entities/entity_aliases.csv` (canonical/alias pairs for search expansion)
- `data/entities/hierarchy_relationships.csv` (if not already present)
- `frontend/src/components/PyramidTooltip.tsx`, `PyramidTooltip.css`
- `frontend/src/components/EntityDetailPanel.tsx`, `EntityDetailPanel.css`
- `docs/development/SEARCH_UX_ENHANCEMENTS_4_6_PLAN.md` (frontend search UX plan; not implemented in this release)
- `test_search_enhancements.py` (manual test script for backend search; run from project root)

### Modified

- **Backend:** `data_loader.py` (federal flows edge_id, hierarchy load), `routers/analysis.py` (pyramid, hierarchy, entity detail, search, entity descriptions), `routers/search.py` (alias expansion, amount parsing, rapidfuzz fuzzy fallback), `models/schemas.py` (pyramid/hierarchy schemas), `requirements.txt` (rapidfuzz>=3.0.0).
- **Frontend:** `PyramidPage.tsx`, `PyramidPage.css`, `PyramidVisualization.tsx`, `PyramidVisualization.css`, `About.tsx` (GitHub repo link).
- **Data:** `data/entities/intel_stack_levels.csv` (L6 program display_name variants and coverage).
- **Root:** `RUN.bat` (ensure backend deps installed before start).
- **Docs:** `CHANGELOG_v0.3.2Beta.md`, `GIT_PUSH_COMMANDS.md` (branch/PR steps for PRH_v0.3.2Beta).

---

## How to Build & Deploy

1. **Frontend:** From project root run `build-and-deploy-frontend.bat` (or `cd frontend && npm run build` then copy `frontend/dist/*` to `backend/static/`).
2. **Data reload** (optional, for latest L6/hierarchy): Stop backend, run `python reload_database.py`, answer `yes`. Restart backend.
3. **Hard-refresh** the Pyramid page (Ctrl+Shift+R) after deploying frontend.

---

## Pre-PR Checklist

- [ ] Frontend builds without errors (`npm run build` in frontend).
- [ ] Backend starts and serves `/analysis/pyramid`.
- [ ] Pyramid shows tiers; search and entity click open detail under search.
- [ ] Trace chain of command highlights chain and shows count.
- [ ] About page shows GitHub repo link.
- [ ] Backend search: "National Geospatial" → NGA, "223" → amount flows, "Pereton" → Peraton (optional: run `python test_search_enhancements.py`).
- [ ] RUN.bat starts server without ModuleNotFoundError (rapidfuzz installed via pip install -r backend\requirements.txt).
- [ ] CHANGELOG and branch instructions updated.
