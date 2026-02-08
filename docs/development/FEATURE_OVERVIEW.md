# Feature overview (post–Enrich / Pyramid / Security)

Short reference for where new and existing features live. For full implementation status, see [ENRICH_PYRAMID_SECURITY_STATUS.md](./ENRICH_PYRAMID_SECURITY_STATUS.md).

## Backend

- **Data loading**  
  `backend/data_loader.py` — Module docstring describes loader categories and `load_all_data()` order. All CSV paths come from `config['data_sources']`.

- **Models**  
  `backend/database.py` — Entity (with `intel_stack_level`), MoneyFlow, Award, MaterialsFlow, Relationship (with description, relationship_type, source_citation, dates), FOIATarget, etc.

- **Data API** (`/api/data/`)  
  `backend/routers/data.py` — Entities, money-flows, awards, **materials-flows**, **connections** (unified view per entity), foia-targets, stats, version, refresh.

- **Analysis API** (`/api/analysis/`)  
  `backend/routers/analysis.py` — Graph, relationships, **entity/{id}/flows**, **intel-stack/summary**, **intel-stack/pyramid**, financial/timeline/sankey.

- **Schemas**  
  `backend/models/schemas.py` — Pydantic models for all endpoints; Pyramid response types at end.

- **Validation**  
  `backend/validation.py` — sanitize_search, validate_entity_id, validate_date, validate_amount; used in data and analysis routers.

## Frontend

- **Pyramid**  
  Route: `/analysis/pyramid`.  
  `frontend/src/pages/PyramidPage.tsx` (page), `frontend/src/components/PyramidVisualization.tsx` (6-tier SVG + sidebar).  
  API: `getPyramidData()` in `services/api.ts`; types in `types/index.ts` (PyramidData, PyramidLevelSummary, etc.).

- **Browse → Pyramid**  
  Entities with `intel_stack_level` show a pyramid icon linking to `/analysis/pyramid?entity_id=...` (`frontend/src/pages/Browse.tsx`).

- **Analysis hub**  
  `frontend/src/pages/AnalysisOverview.tsx` — Card for “Intelligence Stack Pyramid” links to `/analysis/pyramid`.

## Data

- **Financial CSVs**  
  `data/financial/` — money_flows, awards_master, awards_usaspending, money_flows_veritas_peraton, federal_flows_by_recipient, advisors_fees (optional), solicitations, materials_flows, researched_contracts_ffrdc_primes.  
  See `data/financial/README_researched_contracts.md` for the researched contracts file.

- **Entities and levels**  
  `data/entities/` — entities_master, entity_type_overrides, intel_stack_levels (backfill for pyramid), NRO and transcript/Hidden Wing CSVs.

## Config and install

- `.env.example` at project root; `backend/main.py` loads `.env` via python-dotenv.
- `install.sh` / `install.bat`: version checks, retries, .env generation, optional pip-audit / npm audit.
- `START.sh` / `START.bat`: pre-flight checks, optional frontend rebuild, `--dev` for hot reload.
