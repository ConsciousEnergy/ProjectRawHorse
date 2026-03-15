# Changelog - Project RawHorse v0.4.3 Beta

**Release Date:** March 2026

## Summary

v0.4.3 Beta introduces the Simulation Timeline feature with a unified multi-layer temporal view of events, flows, entities, and relationship confidence signals tied to Reverse Engineering / Crash Retrieval analysis.

## Added

- **Simulation API Router**: `/api/simulation/timeline`, `/api/simulation/entities`, `/api/simulation/flows`
- **Simulation schemas** for deterministic paged responses and metadata
- **RE/CR confidence model** with dedicated `re_cr_confidence` table
- **Simulation confidence seed data**: `data/simulation/re_cr_confidence.csv`
- **Simulation schema validation script**: `data/scripts/validate_simulation_schema.py`
- **Simulation Timeline UI page**: `/analysis/simulation`
- **Feature-flag support** for simulation tab visibility (`VITE_ENABLE_SIMULATION_TAB`)
- **Dense-flow canvas fallback** in simulation UI for high-volume flow rendering
- **Simulation contract smoke test**: `tests/simulation_contract_check.py`
- **Simulation implementation guide**: `docs/development/SIMULATION_TIMELINE_GUIDE.md`

## Changed

- **Analysis Overview** now includes a Simulation Timeline navigation card
- **API client and frontend types** expanded to support simulation endpoints and response models
- **Data loading pipeline** now ingests RE/CR confidence mappings from `data/simulation/re_cr_confidence.csv`
- **Confidence governance documentation** updated with simulation mapping rules
- **Operational metrics** now include `re_cr_confidence` table counts

## Performance and UX Guardrails

- Paged simulation endpoints with deterministic ordering
- Confidence threshold and grouping controls (`year` / `decade`)
- Layer toggles and progressive loading/error states
- Bounded payload behavior surfaced via `meta.truncated`

