# Performance Guardrails and SLOs

## Service Level Objectives

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| API availability | 99.5% (monthly) | < 99% triggers page |
| p95 latency (read endpoints) | < 300ms | > 500ms |
| p95 latency (graph/analysis) | < 1000ms | > 2000ms |
| Data refresh success rate | 100% | Any failure |
| Data freshness | Updated within 24h of collection | Stale > 48h |
| Error rate | < 1% of requests | > 2% |

## Cost Control KPIs

| KPI | Target |
|-----|--------|
| Monthly infra budget | < $30 (single VPS phase) |
| Cost per 1k API requests | < $0.01 |
| Storage growth rate | < 100MB/month |
| DB size alert | > 5GB triggers capacity review |

## Query Performance Baseline

Capture with `/api/metrics` endpoint (request timing middleware).

### Expensive Paths to Monitor

1. `/api/analysis/graph/entities` — full graph construction with inferred edges
2. `/api/analysis/intel-stack/pyramid` — multi-table join across entities, flows, relationships
3. `/api/analysis/sankey` — flow aggregation with entity type inference
4. `/api/analysis/intel-stack/hierarchy` — recursive parent/child traversal

### Optimization Actions (in priority order)

1. Add DB indexes for common filter combinations (already done for most)
2. Add `LIMIT` clauses to unbounded queries
3. Precompute pyramid/sankey data during refresh jobs (cache table)
4. Add response caching (Redis) for heavy read endpoints
5. Consider read replicas only if #4 is insufficient

## Scaling Thresholds

| Observation | Action |
|------------|--------|
| p95 > 500ms sustained 3 days | Profile and optimize queries |
| p95 > 1s sustained 7 days | Add Redis caching layer |
| CPU > 70% sustained 7 days | Vertical scale (upgrade VPS) |
| CPU > 70% after vertical scale | Evaluate Docker Swarm |
| Monthly infra > $100 | Review cost allocation, optimize |
