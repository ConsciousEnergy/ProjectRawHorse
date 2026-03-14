# Orchestration Graduation Plan

## Current State: Docker Compose on Single VPS

Single Hostinger VPS running Docker Compose with:
- FastAPI backend (gunicorn + uvicorn workers)
- PostgreSQL 16
- Redis 7 (caching layer)
- Caddy 2 (reverse proxy, automatic TLS)

## Stage 1: Compose (Current)

**Best for:** 0–10k daily users, single developer/operator, budget-conscious deployment.

**What it gives us:**
- Simple deployment (`docker compose up -d`)
- All services on one machine
- Automatic HTTPS via Caddy + Let's Encrypt
- Backup/restore via `docker/backup.sh`
- Health checks and restart policies

## Stage 2: Docker Swarm

**Graduate when ALL conditions are met:**
- Sustained CPU > 70% or memory > 80% for 7+ consecutive days
- p95 API latency exceeds 500ms under normal load
- Single point of failure is unacceptable (uptime SLA > 99.5%)
- At least one additional VPS node is available

**What Swarm adds:**
- Multi-node clustering (2–5 nodes)
- Rolling updates with zero downtime
- Service replicas (scale backend workers)
- Built-in load balancing
- Shared overlay networking

**Migration path:**
1. `docker swarm init` on primary node
2. `docker swarm join` on secondary nodes
3. Convert `docker-compose.yml` to `docker stack deploy`
4. Add replicas: `deploy.replicas: 2` for backend
5. Add placement constraints for PostgreSQL (pin to primary node)

**Estimated effort:** 1–2 days

## Stage 3: Kubernetes

**Graduate when ALL conditions are met:**
- 3+ nodes consistently required
- Need horizontal pod autoscaling based on request load
- Multi-environment release pipelines (staging, canary, production)
- Team has at least one member with K8s operational experience
- Monthly infrastructure budget > $200/month justified by traffic

**What Kubernetes adds:**
- Horizontal Pod Autoscaler (HPA)
- Ingress controllers with sophisticated routing
- Helm charts for repeatable deployments
- Secret management (sealed secrets, external vaults)
- Namespace isolation for staging vs production
- Persistent volume claims with storage classes

**Migration path:**
1. Set up managed K8s cluster (or self-managed via k3s for cost savings)
2. Create Helm chart from existing Compose definitions
3. Define resource requests/limits per pod
4. Configure HPA for backend deployment
5. Set up CI/CD pipeline (GitHub Actions → kubectl apply)
6. Implement canary/blue-green deployment strategy

**Estimated effort:** 1–2 weeks

## Decision Matrix

| Factor | Compose | Swarm | Kubernetes |
|--------|---------|-------|------------|
| Complexity | Low | Medium | High |
| Nodes | 1 | 2–5 | 3+ |
| HA | No | Basic | Full |
| Auto-scaling | No | Manual | Automatic |
| Cost | $5–20/mo | $20–60/mo | $60–200+/mo |
| Ops overhead | Minimal | Low | Moderate |
| Best for | MVP/Beta | Growing traffic | Scale/Enterprise |

## Monitoring Triggers

Set these alerts to know when graduation is warranted:

```
CPU sustained > 70% for 7 days → Evaluate Swarm
Memory sustained > 80% for 7 days → Evaluate Swarm
p95 latency > 500ms for 3 days → Evaluate Swarm
Node count > 2 needed → Evaluate Kubernetes
HPA events > 5/day → Kubernetes justified
```
