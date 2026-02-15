# Release Notes - Project RawHorse v0.4.1

**Release Date:** February 2026  
**Type:** Beta

## Summary

v0.4.1 adds the dedicated FOIA Targets page, UX quick wins (loading states, error boundaries, empty states), a cyberpunk neon UI aesthetic overhaul, and UI bug fixes from a live review.

## Highlights

### For Users

- **FOIA Targets Page** - Browse and prioritize FOIA targets at `/analysis/foia` with quality scoring, filters, and sortable columns
- **Dashboard Stat Cards** - Click Total Entities, Money Flows, Federal Awards, or FOIA Targets to jump to the corresponding Browse tab
- **Export FOIA** - Download FOIA targets as CSV from the Export page
- **Error Handling** - Graceful error boundaries with "Try Again" and "Go Home" when something goes wrong
- **Loading Feedback** - Spinners on Network Graph and Sankey Diagram; skeleton loaders on table pages
- **Light Mode** - Improved contrast for card components (WCAG AA)
- **Search Results** - Wider dropdown and tooltips on truncated names
- **Cyberpunk Neon UI** - Dark mode: deep blue-black backgrounds, neon purple/cyan/gold glows on cards and sidebar, glitch hover on cards, subtle scanline overlay, neon focus outlines. Logo purple and gold retained.

### For Researchers

- **FOIA Quality Scoring** - Priority, Specificity, and Likelihood scores visible in both Browse FOIA tab and dedicated FOIA Targets page
- **Expandable Quality Notes** - Click a row to see full quality notes

### Technical

- **Shared Components** - ScoreBadge, TableSkeleton, EmptyState, ErrorBoundary
- **Screenshot Management** - Version-controlled screenshots in `screenshots/` directory
- **Network Graph** - Center panel min-width to prevent layout squeeze
- **Theme** - `theme.css`: neon variables and dark blue-black palette; `App.css`: card glows, glitch keyframes, sidebar/tabs/buttons neon; `index.css`: neon cyan focus in dark mode
- **Analysis Overview card icons** - Unique gradients per card: Entity Network Graph (purple), Sankey (gold), Intelligence Stack Pyramid (red-orange), FOIA Targets (green-teal)
- **Development Roadmap** - `docs/development/PRH_DEVELOPMENT_ROADMAP.md` with audit findings by priority (P0–P3)

## New Routes

| Route | Description |
|-------|-------------|
| `/analysis/foia` | FOIA Targets page with sortable table and filters |

## Files Added

- `frontend/src/pages/FoiaTargetsPage.tsx`
- `frontend/src/pages/FoiaTargetsPage.css`
- `frontend/src/components/ScoreBadge.tsx`
- `frontend/src/components/ScoreBadge.css`
- `frontend/src/components/TableSkeleton.tsx`
- `frontend/src/components/EmptyState.tsx`
- `frontend/src/components/EmptyState.css`
- `frontend/src/components/ErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary.css`
- `screenshots/*.png` (placeholder screenshots)
- `CHANGELOG_v0.4.1Beta.md`
- `docs/RELEASE_NOTES_v0.4.1.md`
- `docs/development/PRH_DEVELOPMENT_ROADMAP.md`
