# PR #11 Update: Ready-to-Paste Description for Project RawHorse v0.4.0

**Copy the content below the horizontal rule and paste into the PR description at:**
https://github.com/ConsciousEnergy/ProjectRawHorse/pull/11

---

## Overview

This PR merges `PRH_v0.4.0` into main, consolidating v0.4.0 Beta features: the **Network Graph 3-panel overhaul**, **search quality fixes**, **CI pipeline** improvements, **privacy compliance** updates, and existing v0.3.x enhancements (data enrichment, Intelligence Stack Pyramid, one-click install/uninstall).

---

## Features

### Network Graph Overhaul (v0.4.0 Beta)

- **3-panel Epstein Doc Explorer-style layout**: GraphSidebar (left), force graph (center), RelationshipTimeline (right)
- **GraphSidebar**: Stats, entity search with autocomplete, color mode toggle, Intel Stack filter, collapsible legend
- **RelationshipTimeline**: Selected actor timeline with relationship badges, entity filter, browse link
- Square-root node sizing (connection count, 4–40px), radial force model, edge deduplication
- Proximity color mode (red=selected, orange=direct, green=distant), cyan selection highlighting with edge dimming
- Instructions banner ("Click nodes… Scroll to zoom… Drag to pan"), full-bleed dark background (#030712)

### Search Quality Fixes (v0.4.0 Beta)

- **Multi-word tokenized AND**: e.g., "National Geospatial" finds NGA across all four search functions
- **Multi-scale amount parsing**: $223, $223K, $223M supported in search
- **Always-on fuzzy matching**: WRatio scorer with TTL-cached name lists; lower score cutoff (55) for short queries
- **"Did you mean?" suggestions**: Zero-result searches return clickable suggestion pills
- **Multi-token highlighting**: Browse page highlights all matched tokens

### CI Pipeline (v0.4.0 Beta)

- New `ci-check.yml` for PR status checks (tsc --noEmit, pip install, npm run build)
- Fixed `build-releases.yml` shell indentation (fi alignment)
- Regenerated `package-lock.json` to fix npm ci failure (vite version sync)

### Privacy & Accessibility

- Public-handle-only attribution in CONTRIBUTING.md, CODE_OF_CONDUCT.md, UAPGerb transcript
- Search dropdown ARIA roles for accessibility

### Prior Features (v0.3.x)

- Data enrichment pipeline (entity/flow extraction, Hidden Wing transcript)
- Intelligence Stack Pyramid and dedicated visualization pages
- One-click install/uninstall (START.bat/sh, UNINSTALL.bat/sh)
- Docker deployment, PostgreSQL support

---

## Test Plan

### Network Graph

1. Go to `/analysis/network` and verify 3-panel layout (sidebar left, graph center, timeline right)
2. Search for an entity in GraphSidebar; verify autocomplete and graph selection
3. Toggle color mode (Entity Type vs Proximity); verify node colors update
4. Toggle Intel Stack filter; verify graph filters correctly
5. Click a node; verify cyan highlighting and RelationshipTimeline population
6. Verify instructions banner at bottom

### Search Quality

1. Search "National Geospatial"; verify NGA appears (multi-word tokenized AND)
2. Search "Pereton"; verify "Peraton" suggestion (fuzzy match)
3. Search amount "223K"; verify results include $223K range
4. Run a query that returns zero results; verify "Did you mean?" suggestion pills appear and are clickable
5. In Browse, search multi-word; verify both tokens highlighted

### CI

1. Confirm `ci-check.yml` runs on PR (tsc, pip install, npm run build)
2. Confirm `build-releases.yml` runs on tag push (no shell indentation errors)

---

## Performance Metrics (Expected)

| Metric               | Before | After   | Target |
|----------------------|--------|---------|--------|
| Search Success Rate  | ~50%   | Improved| > 80%  |
| Zero-Result Rate     | ~50%   | Reduced | < 20%  |
| Graph Load Time      | —      | < 2s    | < 3s   |

---

## Files Changed

### New Files

- `frontend/src/components/GraphSidebar.tsx` + `.css`
- `frontend/src/components/RelationshipTimeline.tsx` + `.css`
- `.github/workflows/ci-check.yml`

### Modified Files

- `frontend/src/pages/NetworkGraphPage.tsx` — 3-panel layout rewrite
- `frontend/src/pages/Analysis.tsx` — Replaced embedded NetworkGraph with link to dedicated page
- `frontend/src/components/SearchBar.tsx` — "Did you mean?" suggestions
- `frontend/src/types/index.ts` — suggestions field on SearchResponse
- `backend/routers/search.py` — Multi-word, multi-scale, always-on fuzzy, suggestions
- `.github/workflows/build-releases.yml` — Shell indentation fix
- `package-lock.json` — Regenerated for npm ci
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` — Public-handle-only attribution

---

## What's Next (v0.4.1)

- **Dedicated FOIA Targets page** under `/analysis/foia` (planned)

---

## Checklist

- [x] CI passes
- [x] Release notes and changelog updated
- [x] Documentation updated
- [ ] Ready for review (mark PR ready once CI green)
