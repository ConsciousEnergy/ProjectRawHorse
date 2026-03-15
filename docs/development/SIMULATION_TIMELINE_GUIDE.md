# Simulation Timeline Guide (v0.4.3Beta)

## Purpose

The Simulation Timeline unifies four layers in a single temporal view:

1. Historical events
2. Money flows
3. Entities
4. Relationship connections

Each layer can be filtered by confidence and grouped by temporal granularity (year/decade).

## API Contract

### `GET /api/simulation/timeline`

Query params:
- `start_year`, `end_year`
- `confidence_min` (`0.0` to `1.0`)
- `category[]`, `entity_id[]`
- `page`, `page_size`
- `group_by` (`year` or `decade`)

Response:
- `time_range`
- `events`
- `money_flows`
- `entities`
- `connections`
- `meta` (counts + truncation + available filters)

### `GET /api/simulation/entities`
- Supports confidence + active-year + entity type filtering
- Returns paged `items`

### `GET /api/simulation/flows`
- Supports confidence + amount + date-range filtering
- Returns paged `items`

## Confidence Data Model

Source dataset:
- `data/simulation/re_cr_confidence.csv`

Backed by table:
- `re_cr_confidence`

Fields:
- `subject_type`, `subject_id`
- `confidence_score`, `confidence_tier`
- `evidence_refs`
- `effective_start_date`, `effective_end_date`
- `notes`, `updated_at`

Validation script:
- `python data/scripts/validate_simulation_schema.py`

## Rendering Strategy

Primary view:
- SVG multi-lane timeline for events, flows, and entities.

Dense flow fallback:
- Canvas line rendering activates for dense flow sets.

Level of detail:
- Year and decade grouping available.
- Paged API payloads bound response size for UI responsiveness.

## UX Guardrails

- Feature-flagged route visibility via `VITE_ENABLE_SIMULATION_TAB` (set to `false` to hide).
- Progressive loading states (loading, retry, empty/truncated states).
- Layer toggles for events/flows/entities/connections.
- Confidence threshold slider for transparent filtering behavior.

## Observability

- Simulation endpoints are tracked by existing request timing middleware.
- `GET /api/metrics/summary` includes endpoint traffic and latency impact.

## Smoke Test

With backend running:

```bash
python tests/simulation_contract_check.py --base-url http://127.0.0.1:8000
```

This validates contract keys and endpoint availability.
