# NRO Seeds (Public Sources) — Data & Ingestion

This document explains the schema, provenance, and usage of the **NRO commercial seeds** included in this repository.

## Files
- `data/seeds/nro_public_partners_seeds_v2.csv`
- `data/events/nro_press_and_notice_updates_2023_2025.csv`
- `data/viz/nro_seed_edges_v2.csv`
- `docs/img/nro_seed_network_v2.png`

## Schema
See the PR body for the full schema. All dates are ISO `YYYY-MM-DD`. `priority` is a triage scalar (1=highest).

## Provenance
- Official NRO press releases (EOCL; SCE: Radar, RF, HSI)
- SAM notice for **NRO/CSPO Commercial Foundation** RFI
- Vendor/trade press flagged as such and used as *seeds*

## Ingestion Guidance
1. Use USAspending `/api/v2/search/spending_by_award/` with `recipient_search_text` for each `entity`.
2. Join first-tier subs from **SAM Acquisition Subaward** (public) by Award ID/PIID/FAIN.
3. Enrich with **SAM Contract Awards** (ex-FPDS) and map `GFE/GFP Provided Under This Action` (Data Element 8J) as a **custody proxy**.
4. Add **File E** executive-compensation when available for open, lawful person linkages.

## Caveats
- IC component budgets are opaque; NRO obligations may appear under other awarding offices.  
- **GFP (8J)** is an authorization flag; treat as triage, not proof of specific materials.

## Maintenance
- Append new seeds with clear `source` URLs and minimal `award_type` description.
- Keep the `events` table updated for auditability.
