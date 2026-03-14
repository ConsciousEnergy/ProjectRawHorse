# Release Readiness Checklist

## Pre-Release Go/No-Go Gates

### 1. Environment Parity
- [ ] Staging Compose stack matches production (same images, env config shape)
- [ ] PostgreSQL version matches production (16-alpine)
- [ ] All env vars from `docker/.env.example` are set
- [ ] Domain configured in `.env` DOMAIN variable

### 2. Schema and Migration
- [ ] `docker compose up` creates all tables without errors
- [ ] Data loads successfully via `/api/data/refresh`
- [ ] No pending Alembic migrations (when implemented)
- [ ] Rollback tested: can restore from backup in < 15 minutes

### 3. API Contract Verification
- [ ] `/api/health` returns 200
- [ ] `/api/ready` returns 200 with `entities_present: true`
- [ ] `/api/data/stats` returns valid counts
- [ ] `/api/timeline/events` returns seeded events
- [ ] `/api/analysis/intel-stack/pyramid` returns level data
- [ ] `/api/reconciliation/report` returns without anomalies

### 4. Frontend Build
- [ ] `npm run build` completes without errors
- [ ] No TypeScript errors in `npm run typecheck` (if configured)
- [ ] All analysis sub-pages render (overview, network, sankey, pyramid, FOIA, timeline)
- [ ] Navigation and routing work correctly

### 5. Security
- [ ] SECRET_KEY is a 64+ character random string (not default)
- [ ] DB_PASSWORD is strong and unique
- [ ] AUTH_ENABLED=true (if public write access is unwanted)
- [ ] No secrets in committed code (`git log` check)
- [ ] CORS origins restricted to production domain
- [ ] `security.yml` CI workflow passes

### 6. Performance Baseline
- [ ] p95 latency < 500ms for top 5 read endpoints
- [ ] Database size < 5GB
- [ ] Response caching enabled for heavy endpoints (if needed)
- [ ] No slow query warnings in logs during test run

### 7. Operations
- [ ] Backup script tested (`docker/backup.sh`)
- [ ] Restore script tested (`docker/restore.sh`)
- [ ] Log output is JSON in production mode
- [ ] Health/readiness probes are working
- [ ] Restart policies set (`unless-stopped`)

### 8. Load Testing
- [ ] Baseline test: 10 concurrent users, 5 minutes
- [ ] Expected load: 50 concurrent users, 10 minutes
- [ ] Peak test: 100 concurrent users, 5 minutes
- [ ] All tests pass SLO thresholds

### 9. Documentation
- [ ] README updated with deployment instructions
- [ ] CHANGELOG updated for v0.4.2Beta
- [ ] API docs available at `/docs`

## Release Captain Sign-off

| Gate | Status | Verified By | Date |
|------|--------|-------------|------|
| Environment Parity | | | |
| Schema/Migration | | | |
| API Contracts | | | |
| Frontend Build | | | |
| Security | | | |
| Performance | | | |
| Operations | | | |
| Load Testing | | | |
| Documentation | | | |

**Go/No-Go Decision:** ________

## Post-Launch (First 72 Hours)

- [ ] Monitor error rates every 4 hours
- [ ] Check API latency trends daily
- [ ] Review audit logs for anomalies
- [ ] Address top 3 user-reported issues
- [ ] Conduct post-launch review meeting
