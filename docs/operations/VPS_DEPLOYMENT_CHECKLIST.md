# Hostinger VPS Deployment Checklist

Step-by-step guide for deploying Project RawHorse to a Hostinger VPS after local review via `START.bat` / `RUN.bat`.

---

## Phase 0: Local Verification (Before Touching VPS)

- [ ] **Run `START.bat`** on local machine, confirm the app launches at `http://127.0.0.1:8000`
- [ ] **Verify all pages load**: Dashboard, Browse (entities/awards/money-flows/FOIA), Analysis (network/sankey/pyramid), Timeline, Contribute, Export
- [ ] **Test contribution flow**: submit a test entity via the Contribute page, confirm "submitted for review" response
- [ ] **Verify API docs**: open `http://127.0.0.1:8000/docs` and confirm all endpoints are listed
- [ ] **Run frontend build locally**: `cd frontend && npm install && npm run build` — confirm no build errors
- [ ] **Check data loads**: confirm Dashboard shows non-zero stats for entities, money flows, awards
- [ ] **Run load test** (optional): `python tests/load_test.py --base-url http://127.0.0.1:8000 --users 10 --duration 30`

---

## Phase 1: VPS Provisioning (Hostinger)

### 1.1 Server Setup
- [ ] Order a Hostinger VPS (minimum: 2 vCPU, 4GB RAM, 80GB SSD — **KVM 2** tier or higher recommended)
- [ ] Select **Ubuntu 22.04 LTS** as the OS
- [ ] Note the server IP address and root SSH credentials from Hostinger panel
- [ ] SSH into the server: `ssh root@YOUR_VPS_IP`

### 1.2 System Hardening
- [ ] Update packages: `apt update && apt upgrade -y`
- [ ] Create non-root deploy user:
  ```bash
  adduser deploy
  usermod -aG sudo deploy
  ```
- [ ] Copy SSH key for passwordless login:
  ```bash
  ssh-copy-id deploy@YOUR_VPS_IP
  ```
- [ ] Disable root SSH login and password auth in `/etc/ssh/sshd_config`:
  ```
  PermitRootLogin no
  PasswordAuthentication no
  ```
- [ ] Restart SSH: `sudo systemctl restart sshd`
- [ ] Set up UFW firewall:
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```
- [ ] Set timezone: `sudo timedatectl set-timezone UTC`
- [ ] Enable automatic security updates: `sudo apt install unattended-upgrades -y`

### 1.3 Install Docker
- [ ] Install Docker Engine:
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker deploy
  ```
- [ ] Install Docker Compose plugin:
  ```bash
  sudo apt install docker-compose-plugin -y
  ```
- [ ] Verify: `docker compose version`
- [ ] Log out and back in as `deploy` to pick up docker group

---

## Phase 2: Domain & DNS

- [ ] Register or point a domain/subdomain to VPS IP (e.g., `rawhorse.yourdomain.com`)
- [ ] Create A record: `rawhorse.yourdomain.com → YOUR_VPS_IP`
- [ ] Wait for DNS propagation (check with `dig rawhorse.yourdomain.com`)
- [ ] Caddy will auto-provision HTTPS via Let's Encrypt once the domain resolves

---

## Phase 3: Deploy Application

### 3.1 Clone and Configure
- [ ] Clone the repo on VPS:
  ```bash
  cd /home/deploy
  git clone -b PRH_v0.4.2Beta https://github.com/ConsciousEnergy/ProjectRawHorse.git
  cd ProjectRawHorse
  ```
- [ ] Create production `.env` from template:
  ```bash
  cp docker/.env.example .env
  ```
- [ ] **Edit `.env`** with production values:
  ```env
  DOMAIN=rawhorse.yourdomain.com
  DB_PASSWORD=<generate with: openssl rand -base64 32>
  DATABASE_URL=postgresql://prh:${DB_PASSWORD}@db:5432/rawhorse
  REDIS_URL=redis://cache:6379/0
  SECRET_KEY=<generate with: openssl rand -base64 48>
  ENVIRONMENT=production
  DEBUG=false
  RATE_LIMIT_REQUESTS=100
  RATE_LIMIT_PERIOD=60
  ```
- [ ] **IMPORTANT**: Never commit `.env` to Git — verify it's in `.gitignore`

### 3.2 Build and Launch
- [ ] Build and start all services:
  ```bash
  docker compose up -d --build
  ```
- [ ] Monitor startup logs:
  ```bash
  docker compose logs -f --tail=50
  ```
- [ ] Wait for health checks to pass (typically 60-90 seconds):
  ```bash
  docker compose ps
  ```
  All services should show `healthy` or `running`.

### 3.3 Verify Deployment
- [ ] Test health endpoint: `curl http://localhost:8000/api/health`
- [ ] Test readiness: `curl http://localhost:8000/api/ready`
- [ ] Test from browser: open `https://rawhorse.yourdomain.com`
- [ ] Verify HTTPS certificate (Caddy auto-provisions from Let's Encrypt)
- [ ] Test API docs: `https://rawhorse.yourdomain.com/api/docs`
- [ ] Verify data loaded: `curl https://rawhorse.yourdomain.com/api/data/stats`

---

## Phase 4: Operations Setup

### 4.1 Backups
- [ ] Create backup directory: `sudo mkdir -p /home/deploy/backups`
- [ ] Copy backup script: `cp docker/backup.sh /home/deploy/backups/`
- [ ] Make executable: `chmod +x /home/deploy/backups/backup.sh`
- [ ] Schedule daily backup via cron:
  ```bash
  crontab -e
  # Add: 0 3 * * * /home/deploy/backups/backup.sh >> /home/deploy/backups/backup.log 2>&1
  ```
- [ ] Test backup: `./backups/backup.sh`
- [ ] Test restore (on a test DB): verify `docker/restore.sh` works

### 4.2 Monitoring
- [ ] Verify metrics endpoint: `curl https://rawhorse.yourdomain.com/api/metrics/summary`
- [ ] Set up uptime monitoring (e.g., UptimeRobot, Hetrix) pointing to `/api/health`
- [ ] Set up log rotation for Docker:
  ```json
  # /etc/docker/daemon.json
  {
    "log-driver": "json-file",
    "log-opts": { "max-size": "50m", "max-file": "3" }
  }
  ```
- [ ] Restart Docker: `sudo systemctl restart docker`

### 4.3 Traffic Monitoring
- [ ] Monitor real-time traffic via metrics endpoint (request counts, latency percentiles, error rates)
- [ ] Review Caddy access logs: `docker compose logs caddy --tail=100`
- [ ] Check resource usage: `docker stats`

---

## Phase 5: CORS & Security for Public Access

- [ ] Update `backend/main.py` CORS origins to include your production domain:
  ```python
  allow_origins=["https://rawhorse.yourdomain.com"]
  ```
  Or set via environment variable for flexibility.
- [ ] Set `TRUSTED_HOSTS=rawhorse.yourdomain.com` in `.env`
- [ ] Verify rate limiting works: rapid-fire requests should get 429 responses
- [ ] Verify security headers: `curl -I https://rawhorse.yourdomain.com`

---

## Phase 6: Post-Launch Verification

- [ ] Browse all pages on production URL
- [ ] Submit a test contribution and verify it appears in the queue
- [ ] Export data (CSV, JSON) and verify downloads work
- [ ] Run load test against production (low intensity):
  ```bash
  python tests/load_test.py --base-url https://rawhorse.yourdomain.com --users 5 --duration 20
  ```
- [ ] Check error budget: `curl https://rawhorse.yourdomain.com/api/metrics/summary | python -m json.tool`
- [ ] Share the public URL with testers

---

## Phase 7: Ongoing Maintenance

### Updating the Application
```bash
cd /home/deploy/ProjectRawHorse
git pull origin PRH_v0.4.2Beta
docker compose up -d --build
docker compose logs -f --tail=50   # watch for errors
```

### Viewing Logs
```bash
docker compose logs backend --tail=100 -f    # API logs
docker compose logs caddy --tail=100 -f      # Access logs
docker compose logs db --tail=50             # PostgreSQL logs
```

### Database Management
```bash
docker compose exec db psql -U prh -d rawhorse   # SQL shell
```

### Restarting Services
```bash
docker compose restart backend   # Restart API only
docker compose down && docker compose up -d   # Full restart
```

### Scaling (Future)
When traffic exceeds single-server capacity, refer to `docs/operations/ORCHESTRATION_GRADUATION.md` for Docker Swarm and Kubernetes migration criteria.

---

## Appendix: Minimum VPS Sizing

| Load Level | vCPU | RAM | Disk | Hostinger Tier |
|------------|------|-----|------|----------------|
| Dev/Preview | 1 | 2GB | 40GB | KVM 1 |
| Low Traffic (<100 users/day) | 2 | 4GB | 80GB | KVM 2 |
| Medium Traffic (<1000/day) | 4 | 8GB | 160GB | KVM 4 |
| High Traffic (1000+/day) | 8 | 16GB | 200GB | KVM 8 |

## Appendix: Quick Commands Reference

```bash
# Status check
docker compose ps && docker compose logs --tail=5

# Emergency stop
docker compose down

# Full rebuild (after code changes)
docker compose up -d --build --force-recreate

# Backup now
/home/deploy/backups/backup.sh

# Check disk usage
df -h && docker system df
```
