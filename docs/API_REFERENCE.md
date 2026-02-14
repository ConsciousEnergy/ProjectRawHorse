# Project RawHorse — API Reference

**Version:** v0.4.0  
**Last Updated:** February 2026  
**Base URL:** `http://localhost:8000`  
**Interactive docs:** `http://localhost:8000/docs` (Swagger UI) or `/redoc` (ReDoc)

All API endpoints are prefixed with `/api/` unless otherwise noted. The backend also serves the built frontend as static files at the root path.

---

## Table of Contents

- [Health & System](#health--system)
- [Data — Entities, Flows, Awards, FOIA](#data)
- [Search](#search)
- [Analysis & Visualization](#analysis--visualization)
- [Export](#export)
- [Contribute](#contribute)
- [Authentication](#authentication)

---

## Health & System

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{ "status": "healthy" }
```

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

## Data

**Prefix:** `/api/data`

All data endpoints support pagination via `offset` (or `skip`) and `limit` query parameters.

### `GET /api/data/entities`

List entities with optional filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Filter by name (case-insensitive) |
| `entity_type` | string | — | Filter by type (e.g., "contractor", "agency") |
| `intel_stack_level` | string | — | Filter by hierarchy level (L1–L6) |
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results per page |

**Example:**
```bash
curl "http://localhost:8000/api/data/entities?search=lockheed&limit=10"
```

### `GET /api/data/entities/{entity_id}`

Get a single entity by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_id` | string (path) | Entity identifier |

### `GET /api/data/money-flows`

List money flows with optional filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Filter by source or target name |
| `min_amount` | float | — | Minimum USD amount |
| `max_amount` | float | — | Maximum USD amount |
| `start_date` | string | — | Filter by date (YYYY-MM-DD) |
| `end_date` | string | — | Filter by date (YYYY-MM-DD) |
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results |

### `GET /api/data/awards`

List federal awards with optional filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Filter by recipient or description |
| `agency` | string | — | Filter by awarding agency |
| `min_amount` | float | — | Minimum award amount |
| `max_amount` | float | — | Maximum award amount |
| `start_date` | string | — | Filter by action date |
| `end_date` | string | — | Filter by action date |
| `naics_code` | string | — | Filter by NAICS industry code |
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results |

### `GET /api/data/foia-targets`

List FOIA targets with optional filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Filter by name or agency |
| `agency` | string | — | Filter by agency |
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results |

### `GET /api/data/materials-flows`

List materials and technology transfer flows.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Filter by entity or material |
| `material_type` | string | — | Filter by type |
| `start_date` | string | — | Filter by date |
| `end_date` | string | — | Filter by date |
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results |

### `GET /api/data/connections`

Get all relationships and flows for a single entity.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_id` | string | Entity ID (provide one) |
| `entity_name` | string | Entity name (provide one) |

**Response:**
```json
{
  "entity": { ... },
  "relationships": [ ... ],
  "money_flows": [ ... ],
  "materials_flows": [ ... ]
}
```

### `GET /api/data/stats`

Overall database statistics.

**Response:**
```json
{
  "entity_count": 150,
  "money_flow_count": 200,
  "award_count": 50,
  "foia_target_count": 30
}
```

### `GET /api/data/version`

Current data version and last update timestamp.

**Response:**
```json
{
  "version": 5,
  "last_updated": "2026-02-10T12:00:00",
  "last_modified_by": "system"
}
```

### `POST /api/data/refresh`

Reload all data from CSV files and increment the data version.

**Response:**
```json
{
  "success": true,
  "message": "Data refreshed successfully",
  "version": 6,
  "last_updated": "2026-02-11T14:30:00"
}
```

---

## Search

**Prefix:** `/api`

### `GET /api/search`

Global search across all data types.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | **(required)** | Search query |
| `types` | string | — | Comma-separated types to search (entity, award, money_flow, foia_target) |
| `limit` | int | 20 | Max results per type |

**Response:**
```json
{
  "query": "lockheed",
  "total_results": 5,
  "results": [
    {
      "id": "ent_001",
      "type": "entity",
      "title": "Lockheed Martin",
      "description": "Prime contractor, L4",
      "relevance": 0.95
    }
  ],
  "response_time_ms": 2.3
}
```

**Example:**
```bash
curl "http://localhost:8000/api/search?q=air+force&limit=10"
```

### `GET /api/search/analytics`

Search usage analytics.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Top N results |

**Response:**
```json
{
  "total_searches": 150,
  "searches_last_24h": 12,
  "popular_searches": ["lockheed", "DARPA", "SAP"],
  "no_result_searches": ["xyzfoo"],
  "performance": { "avg_ms": 3.1 }
}
```

---

## Analysis & Visualization

**Prefix:** `/api/analysis`

### `GET /api/analysis/graph/entities`

Entity relationship graph data (nodes and edges) for the Network Graph visualization.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Max entities |

### `GET /api/analysis/graph/money-flows`

Money flow graph data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_amount` | float | — | Minimum flow amount |
| `limit` | int | 100 | Max flows |

### `GET /api/analysis/relationships/{entity_name}`

All relationships and money flows for a specific entity.

### `GET /api/analysis/financial/flows`

Financial flow summary grouped by entity (inflows and outflows).

### `GET /api/analysis/financial/totals`

Aggregate financial totals and top recipients.

### `GET /api/analysis/timeline`

Money flows aggregated by year.

**Response:**
```json
{
  "timeline": [
    { "year": 2020, "count": 15, "total_amount": 5000000 },
    { "year": 2021, "count": 22, "total_amount": 8500000 }
  ]
}
```

### `GET /api/analysis/sankey`

Sankey diagram data (nodes, links, values).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_amount` | float | — | Minimum flow to include |
| `include_relationships` | bool | false | Include non-financial relationships |
| `limit` | int | 50 | Max flows |

### `GET /api/analysis/entity/{entity_id}/flows`

All flows (money + materials + relationships) for a single entity.

### `GET /api/analysis/intel-stack/summary`

Entities grouped by intel stack level with aggregate flow totals.

### `GET /api/analysis/intel-stack/pyramid`

Full pyramid visualization data with cross-level flows.

### `GET /api/analysis/intel-stack/hierarchy`

Chain-of-command hierarchy for an entity.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_id` | string (query) | Entity to trace |

### `GET /api/analysis/intel-stack/entity/{entity_id}/detail`

Detailed entity information for pyramid drill-down.

### `GET /api/analysis/intel-stack/search`

Search entities with intel stack level context.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | **(required)** | Search query |
| `limit` | int | 20 | Max results |

---

## Export

**Prefix:** `/api/export`

All export endpoints return file downloads.

### `GET /api/export/csv/entities`

Download all entities as CSV.

**Content-Type:** `text/csv`

### `GET /api/export/csv/money-flows`

Download all money flows as CSV.

### `GET /api/export/csv/awards`

Download all awards as CSV.

### `GET /api/export/json/entities`

Download all entities as JSON.

**Content-Type:** `application/json`

### `GET /api/export/json/money-flows`

Download all money flows as JSON.

### `GET /api/export/pdf/summary`

Download a formatted PDF summary report.

**Content-Type:** `application/pdf`

**Example:**
```bash
curl -o entities.csv http://localhost:8000/api/export/csv/entities
```

---

## Contribute

**Prefix:** `/api/contribute`

All contribution endpoints require a GitHub personal access token in the `X-GitHub-Token` header.

### `POST /api/contribute/entity`

Submit a new entity via automated GitHub PR.

**Headers:**
- `X-GitHub-Token: ghp_your_token_here`

**Body (JSON):**
```json
{
  "entity_id": "org_new_entity",
  "display_name": "New Organization",
  "normalized_name": "NEW ORGANIZATION",
  "entity_type": "agency",
  "contributor_name": "Your Name",
  "contributor_email": "you@example.com",
  "notes": "Found in public FOIA release XYZ"
}
```

### `POST /api/contribute/money-flow`

Submit a new money flow.

### `POST /api/contribute/award`

Submit a new federal award.

### `POST /api/contribute/foia-target`

Submit a new FOIA target.

### `GET /api/contribute/validate-token`

Validate a GitHub personal access token.

**Headers:**
- `X-GitHub-Token: ghp_your_token_here`

**Response:**
```json
{ "valid": true, "message": "Token is valid" }
```

---

## Authentication

**Prefix:** `/api/auth`

Authentication is **optional** and **disabled by default** for local use. Enable by setting `AUTH_ENABLED=true` in your environment.

### `POST /api/auth/login`

Login and receive JWT tokens. Rate limited to 10 requests per minute.

**Body:**
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### `POST /api/auth/refresh`

Refresh an expired access token. Rate limited to 10 requests per minute.

**Body:**
```json
{ "refresh_token": "eyJ..." }
```

### `GET /api/auth/me`

Get current authenticated user information.

**Headers:**
- `Authorization: Bearer eyJ...`

### `GET /api/auth/status`

Check whether the auth system is enabled.

**Response:**
```json
{ "auth_enabled": false }
```

---

## Error Responses

All endpoints return standard HTTP error responses:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited |
| 500 | Internal server error |

**Error format:**
```json
{
  "detail": "Entity not found"
}
```

---

## Rate Limiting

- Auth endpoints: 10 requests/minute per IP
- Search: No hard limit, but debounced at 200ms on the frontend
- All other endpoints: No rate limiting for local use

---

## Further Reading

- [Architecture Guide](ARCHITECTURE.md) — System overview and design decisions
- [Developer Guide](DEVELOPER_GUIDE.md) — Setup, build, and contribute
- [Swagger UI](http://localhost:8000/docs) — Interactive API explorer (when server is running)
