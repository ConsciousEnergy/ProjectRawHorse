# Changelog - Project RawHorse v0.4.2 Beta

**Release Date:** March 2026

## Summary

v0.4.2 Beta delivers the historical timeline MVP, database-first public contributions, Git LFS removal, security and observability hardening, confidence governance, and release-readiness tooling for VPS deployment.

## Added

- **Historical Timeline MVP** with 1933-2026 seeded events, tiered confidence model, and source citations
- **Timeline API Router** (`/api/timeline/events`, `/api/timeline/events/{id}`, `/api/timeline/buckets`)
- **Timeline UI Page** at `/analysis/timeline` with decade buckets, filters, and citation expansion
- **Database-First Contributions** (`/api/contribute/submit`, queue/review flow) with no GitHub token required
- **Operational Metrics Endpoint** (`/api/metrics/summary`) with request counts, latency percentiles, and error rates
- **Readiness Probe** (`/api/ready`) and improved health checks for container orchestration
- **Request Timing Middleware** with slow-request warnings and `X-Response-Time` header
- **Immutable Audit Logging** model and utility for sensitive operations
- **Reconciliation Reporting** endpoint (`/api/reconciliation/report`) for trust/governance checks
- **Pipeline Tooling**:
  - `data/scripts/validate_csv_schema.py`
  - `data/scripts/run_pipeline.py`
  - generated pipeline manifest/checksum support
- **Operational Runbooks/Docs**:
  - `docs/operations/RELEASE_CHECKLIST.md`
  - `docs/operations/PERFORMANCE_GUARDRAILS.md`
  - `docs/operations/ORCHESTRATION_GRADUATION.md`
  - `docs/governance/CONFIDENCE_TIERS.md`
  - `docs/operations/VPS_DEPLOYMENT_CHECKLIST.md`
- **Backup/Restore scripts**:
  - `docker/backup.sh`
  - `docker/restore.sh`
- **PR governance assets**:
  - `.github/pull_request_template.md`
  - `.github/workflows/ci.yml`

## Changed

- **Contribution architecture** changed from user-token GitHub PR flow to pending contribution queue + admin review flow
- **README and docs structure** updated to reflect timeline MVP, v0.4.2 capabilities, and VPS production readiness
- **Docker/Caddy settings** refined for production (`DOMAIN` env support, health probe routes, env guidance)
- **Frontend typing contracts** strengthened for analysis APIs (reduced `any` usage and improved response typing)
- **Pyramid schema** extended with provenance/temporal fields:
  - `evidence_refs`
  - `effective_start_date`
  - `effective_end_date`

## Fixed

- CI/frontend TypeScript failures caused by missing API exports and stale timeline assumptions
- YAML workflow parsing issue in `.github/workflows/ci.yml` by using block scalar for multi-line `run`
- LFS pointer state by fully exporting tracked data objects into regular Git content
- API path/type mismatches across analysis and visualization components

## Security

- Added dependency and image scanning workflow (`pip-audit`, `npm audit`, `Trivy`)
- Added security headers middleware and request size protections
- Added action-level audit log coverage for sensitive data actions

## Accessibility and UX

- Added keyboard-visible focus improvements
- Added reduced motion support (`prefers-reduced-motion`)
- Added skip-link styling and resilient loading/error states

## Infrastructure and Deployment

- Compose stack hardened for Hostinger VPS baseline with PostgreSQL + Redis + Caddy
- Health/readiness checks aligned across backend, compose, and reverse proxy
- Added clear production env template guidance in `docker/.env.example`

## Notes

- This release intentionally prioritizes operational reliability and data trust foundations before major new simulation UX work targeted for v0.4.3 Beta.

