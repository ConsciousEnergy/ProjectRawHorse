# Changelog - Project RawHorse v0.3.3 Beta

**Release Date:** February 2026  
**Branch:** PRH_v0.3.3Beta  
**Tag:** `v0.3.3-beta`  
**Status:** Ready for PR into main  
**Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse

---

## Overview

This release builds on v0.3.2 Beta with **CI/build workflow fixes** (deprecated GitHub Actions upgraded, trigger tightened, caching and concurrency) and **Search UX enhancements 4–6**: search suggestions (recent queries + recent results), visual row highlighting when opening a result from the global SearchBar, and search history (recently clicked results). No new backend APIs; all search UX work is frontend-only.

---

## New Features

### Search UX Enhancements (4–6)

- **6. Search history (recently clicked results)**  
  - The global SearchBar persists the last 8 results the user clicked (localStorage key `searchBarClickedResults`).  
  - When the dropdown is open and the user has typed fewer than 2 characters, a **Recent results** section shows these items; clicking one navigates to Browse with the same tab, search, and highlight as a normal result.

- **4. Search suggestions**  
  - **Recent searches**: Last 10 search queries are stored (`searchBarRecentQueries`). When the dropdown is open with short or empty query, a **Recent searches** section lists them (filtered by current input); clicking one sets the query and runs search.  
  - Suggestions block appears when query length &lt; 2 (Recent results + Recent searches).  
  - **Clear history** link in the suggestions footer clears both recent results and recent queries.  
  - Debounce reduced from 300ms to 200ms for snappier feel.  
  - Keyboard navigation (↑↓ and Enter) works in the suggestions list.

- **5. Visual highlighting in Browse**  
  - When the user lands on Browse from a SearchBar result click, the URL includes `highlight=<id>`.  
  - Browse reads `highlight`, finds the matching table row by stable id (`row-entity-*`, `row-flow-*`, `row-award-*`, `row-foia-*`), scrolls it into view with `scrollIntoView({ behavior: 'smooth', block: 'nearest' })`, and applies a short **flash** animation (`.row-highlight-flash`).  
  - After 2.5s the highlight is removed and `highlight` is cleared from the URL.

### One-Click Uninstall

- **UNINSTALL.bat** (Windows) and **UNINSTALL.sh** (macOS/Linux) remove all install artifacts: venv (or ../venv), frontend/node_modules, backend/static, frontend/dist, dist/, build/, rawhorse.spec, .env, cache, logs, enrichment outputs, and optionally data/prh.db.
- Server detection via port 8000 (netstat / lsof or ss); user can choose to stop the server before removal.
- Optional prompts: keep database, (Linux) remove desktop menu entry.
- **--force** / **-y** (or Windows `/force`) skips all prompts for scripted use.
- Removal summary printed at the end (R=removed, K=kept, N=not found). Windows long-path fallback for node_modules (robocopy) when rmdir fails.

---

## CI / Build

### GitHub Actions (build-releases.yml)

- **Deprecated actions upgraded (critical):**  
  - `actions/upload-artifact`: v3 → v4 (v3 deprecated Jan 2025, causes failure).  
  - `actions/download-artifact`: v3 → v4.  
  - `actions/setup-python`: v4 → v5; added `cache: 'pip'`.  
  - `softprops/action-gh-release`: v1 → v2.  
- **Node.js:** 18 → 20 (LTS); `setup-node` unchanged at v4 with `cache: 'npm'` and `cache-dependency-path: frontend/package-lock.json`.  
- **Trigger:** Added `branches-ignore: ['**']` under `push` so the workflow runs only on `v*` tag pushes and `workflow_dispatch`, not on branch pushes.  
- **Permissions:** Top-level `permissions: contents: write` for release creation.  
- **Concurrency:** `group: release-${{ github.ref }}`, `cancel-in-progress: true` to cancel duplicate runs when a new tag is pushed.

---

## Files Changed (Summary)

### Modified

- **CI:** `.github/workflows/build-releases.yml` (actions upgrades, trigger, permissions, concurrency, caching).  
- **Frontend:** `frontend/src/components/SearchBar.tsx`, `frontend/src/components/SearchBar.css` (suggestions, recent results/queries, storage, keyboard).  
- **Frontend:** `frontend/src/pages/Browse.tsx`, `frontend/src/pages/Browse.css` (read `highlight`, row ids, scroll + flash, `.row-highlight-flash`).  
- **Docs:** `README.md`, `INSTALL_GUIDE.md`, `QUICKSTART.md` (uninstall instructions and links).

### New

- `CHANGELOG_v0.3.3Beta.md` (this file).  
- `UNINSTALL.bat` (Windows one-click uninstaller; port-8000 check, long-path node_modules fix, /force, removal summary).  
- `UNINSTALL.sh` (macOS/Linux uninstaller; venv/../venv, lsof/ss server check, --force/-y, Linux .desktop cleanup, removal summary).

### Docs updated

- `GIT_PUSH_COMMANDS.md` (PRH_v0.3.3Beta branch and tag instructions).  
- `docs/development/SEARCH_UX_ENHANCEMENTS_4_6_PLAN.md` (implementation status for 4–6).  
- `docs/development/UNINSTALL_PLAN.md` (refined to match implemented behavior).

---

## How to Build & Deploy

1. **Frontend:** From project root run `build-and-deploy-frontend.bat` (or `cd frontend && npm run build` then copy `frontend/dist/*` to `backend/static/`).  
2. No backend or data changes; optional hard-refresh (Ctrl+Shift+R) after deploying frontend.

---

## Version Control (Best Practices)

- **Branch:** `PRH_v0.3.3Beta` (create from current branch or main).  
- **Tag:** `v0.3.3-beta` (annotated tag recommended for releases).  
- **Commit message:** Use conventional commits, e.g.  
  `feat(search-ux): suggestions, recent results, Browse row highlight; CI workflow fixes (v0.3.3 Beta)`  
- See `GIT_PUSH_COMMANDS.md` for exact commands to create branch, commit, tag, and push.

---

## Pre-PR Checklist

- [x] Frontend builds without errors (`npm run build` in frontend).
- [ ] SearchBar shows Recent results and Recent searches when dropdown opens with short/empty query.
- [ ] Clicking a SearchBar result navigates to Browse and the matching row scrolls into view and flashes.
- [ ] Clear history clears both recent results and recent queries.
- [ ] CI workflow runs only on tag push or manual dispatch (no run on branch push).
- [ ] CHANGELOG and branch/tag instructions updated.
