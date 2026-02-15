# Changelog - Project RawHorse v0.4.1 Beta

**Release Date:** February 2026

## Summary

v0.4.1 Beta adds the dedicated FOIA Targets page, UX quick wins (ErrorBoundary, TableSkeleton, EmptyState), a cyberpunk neon UI aesthetic overhaul, UI bug fixes, and screenshot management.

## Added

- **FOIA Targets Page** at `/analysis/foia` with sortable table, filters, pagination, expandable quality notes
- **ScoreBadge** shared component
- **TableSkeleton** shared component for table pages
- **EmptyState** shared component
- **ErrorBoundary** wrapping all route pages
- Loading spinners on NetworkGraph and SankeyDiagram
- Export FOIA Targets (CSV) button
- Dashboard stat cards click-through to Browse tabs
- Screenshots directory with placeholder images
- README updated to use relative screenshot paths
- **Cyberpunk Neon UI Overhaul** (dark mode): deep blue-black backgrounds; neon purple/cyan/gold accents; neon border glow on cards and stat-card values; glitch/retro hover effect on cards; sidebar and tab/button neon treatments; subtle CRT scanline overlay; neon cyan focus outlines. Primary colors (logo purple/gold) unchanged.
- **Analysis Overview card icons** — Distinct gradients per card: Entity Network Graph (purple), Sankey Flow Diagram (gold), Intelligence Stack Pyramid (red-orange), FOIA Targets (green-teal).
- **PRH Development Roadmap** — `docs/development/PRH_DEVELOPMENT_ROADMAP.md`: codebase audit findings organized by priority (P0–P3); immediate fixes, refactoring, TypeScript/React, security, testing, performance, infrastructure.

## Fixed

- Browse FOIA tab: added score columns
- Browse Entities: View Network column width
- Light mode contrast on cards
- Search dropdown truncation (min-width, title tooltips)
- Network Graph center panel squeeze (min-width)
- Browse tab not syncing from URL on load (activeTab initialized from searchParams)
- FOIA Targets page table columns overflow (table-layout: fixed, column widths)
