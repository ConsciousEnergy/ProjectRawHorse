# UAP–Federal Research & Contracting Dataset

_A transparent, auditable, multi-agency research dataset and toolkit for UAP/UFO-adjacent federal activity._

**Last updated:** 2025-11-09

## TL;DR
This repo aggregates authoritative public data (USAspending, SAM.gov, OSTI, SBIR.gov, DOE OSDBU Forecast, FedConnect, AARO.mil, FOIA reading rooms, etc.), normalizes it into canonical CSVs, and applies transparent, keyword‑weighted scoring and link analysis to surface credible leads. A lightweight React dashboard supports exploration; scripts make the pipeline reproducible.

---

## Objectives
- Build an **evidence-first** dataset across **DoD, DOE/NNSA, NASA, DHS, FAA, NOAA, NIST, NSF, ODNI, NRO, NGA**, and others.
- Preserve **provenance** for every row; keep raw pulls immutable.
- Provide **repeatable** fetch → normalize → score/join → explore workflows.
- Enable **compliance-aware outreach** (FSO/ISM/CAS) using only public, lawful data.

---

## Repo Layout
```
/uap_dataset/
  external/                   # API/site pulls with _manifest.json
    usaspending_weighted/
    usaspending_multiagency/
    doe/ {osti/, sbir/, foia/, …}
    sam_bulk/
  processed/                  # canonical CSVs for analysis & UI
    entities.csv
    entities_seeds_extended.csv
    awards_enriched.csv
    awards_from_usaspending_weighted.csv
    awards_multiagency.csv
    solicitations.csv
    solicitations_doe_forecast.csv
    research_outputs.csv
    sbir_awards_doe.csv
    arpae_projects.csv
    integrated/ {sbir_scored.csv, research_outputs_scored.csv, arpae_projects_scored.csv, pipeline_candidates.csv}
  scripts/                    # fetchers, normalizers, scorers, joins, watcher
  lookups/                    # keywords_deduped.txt, keyword_weights.csv, agency_targets.json
  docs/                       # HOWTOs, scoring rubric, scope
  apps/viz/                   # React dashboard + Vite app shell
```

---

## Core Features
- **Multi‑agency intake:** USAspending (weighted + multi‑agency), SAM.gov entity enrichment, FedConnect, DOE OSDBU Forecast, OSTI, SBIR.gov, AARO.mil, FOIA indices, ARPA‑E.
- **Transparent scoring:** keyword‑weighted (configurable), provenance weighting, capped bonuses, entity joins by UEI/DUNS/CAGE.
- **Pipeline linking:** DOE forecast ↔ SBIR titles/abstracts + NAICS hints → `pipeline_candidates.csv`.
- **Dashboard:** drag‑and‑drop CSVs, search, filtering, NAICS summary, quick triage.

---

## Quick Start
**Prereqs:** Python ≥ 3.10, Node ≥ 18. Optional: `SAM_API_KEY` for SAM.gov.

```bash
# 1) Install JS deps for the dashboard (optional but recommended)
cd apps/viz && npm i && cd -

# 2) Pull USAspending (weighted by keywords)
python scripts/fetch_usaspending_weighted.py   --keywords_file lookups/keywords_deduped.txt   --weights_file lookups/keyword_weights.csv   --out_dir external/usaspending_weighted
python scripts/normalize_usaspending_weighted.py   --in_dir external/usaspending_weighted   --out_csv processed/awards_from_usaspending_weighted.csv

# 3) DOE: OSTI + SBIR orchestration
python scripts/run_doe_ingest.py --osti_queries "metamaterials" "sensor fusion" "materials characterization" --sbir_start 2019 --sbir_end 2025

# 4) DOE Acquisition Forecast
python scripts/fetch_doe_acq_forecast.py --url "<DIRECT_XLS_OR_CSV_URL>" --out external/doe/doe_acq_forecast.xlsx
python scripts/normalize_doe_acq_forecast.py --in_xlsx external/doe/doe_acq_forecast.xlsx --out_csv processed/solicitations_doe_forecast.csv

# 5) Multi‑agency awards (beyond DOE)
python scripts/fetch_usaspending_multiagency.py   --endpoint_base https://api.usaspending.gov   --keywords_file lookups/keywords_deduped.txt   --agencies_json lookups/agency_targets.json   --out_dir external/usaspending_multiagency   --min_action_date 2019-01-01 --pages 2
python scripts/normalize_usaspending_multiagency.py   --in_dir external/usaspending_multiagency   --out_csv processed/awards_multiagency.csv

# 6) Integrated scoring & pipeline
python scripts/score_join_integrated.py   --entities processed/entities.csv   --sbir processed/sbir_awards_doe.csv   --research_outputs processed/research_outputs.csv   --arpae_projects processed/arpae_projects.csv   --forecast processed/solicitations_doe_forecast.csv   --out_dir processed/integrated

# 7) Dashboard (and optional live JSON snapshots)
cd apps/viz && npm run dev &
python ../../scripts/watch_processed_to_json.py --processed_dir ../../processed --out_dir public/data --interval 5
```

---

## Configuration
- **Keywords:** `lookups/keywords_deduped.txt` (edit to tune focus). Weights in `lookups/keyword_weights.csv` (e.g., boost DOE/IC terms).
- **Agencies:** `lookups/agency_targets.json` controls non‑DOE award pulls.
- **Env vars:** `SAM_API_KEY` for SAM.gov entity lookups.

---

## Scoring & Linking
- Heuristics are documented and capped to keep scores interpretable.
- See: `docs/CREDIBILITY_SCORING.md`, `docs/INTEGRATED_PIPELINE.md`, `docs/DOE_ARPAE_ENHANCEMENTS.md`.
- Entity joins prefer **UEI ≻ DUNS ≻ CAGE ≻ normalized name**.

---

## Data Provenance & Ethics
- All sources are public/official. Raw pulls live under `external/` with `_manifest.json` timestamps.
- Respect robots/ToS; do **not** ingest classified/PII/export‑controlled content.
- Use public business contacts for outreach; when in doubt, route via small business/procurement.

---

## Contributing
1. Open an issue describing your change (new source, schema, analysis).
2. Add fetchers/normalizers and tests; update manifests and docs.
3. Keep functions small; document assumptions and edge cases.
4. Submit a PR with sample outputs (redacted if needed).

**Definition of Done**
- Reproducible on fixtures; provenance preserved; no ToS violations; no PII/classified.

---

## Roadmap
- Expand IC‑adjacent sources (IARPA/DARPA programs).  
- Harden semantic matching for pipeline candidates (transparent & tunable).  
- Nightly containerized pulls with diffs.

---

## Maintainers & Contact
- Primary maintainer: _TBD_  
- Issues & questions: open an issue or contact the maintainer.

## License
_TBD by maintainers._
