# Project RawHorse — Developer Guide

**Version:** v0.4.0  
**Last Updated:** February 2026

This guide covers everything you need to set up a development environment, run the application, build for production, and contribute code.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ (LTS) | [nodejs.org](https://nodejs.org/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

Verify your installation:

```bash
python --version   # Python 3.10+
node --version     # v20+
npm --version      # 9+
git --version      # 2.x+
```

---

## Quick Setup

### Clone and Install

```bash
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse
```

**Option A: Automated** (recommended for first-time setup)

```bash
# Windows
START.bat

# macOS/Linux
chmod +x START.sh && ./START.sh
```

This creates a virtual environment, installs all dependencies, builds the frontend, and starts the server.

**Option B: Manual**

```bash
# Create Python virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## Running in Development Mode

You'll need **two terminals** — one for the backend, one for the frontend.

### Terminal 1: Backend

```bash
# From project root, with venv activated
cd backend
uvicorn main:app --reload --port 8000
```

The `--reload` flag enables hot-reload on Python file changes.

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Terminal 2: Frontend

```bash
# From project root
cd frontend
npm run dev
```

- Dev server: http://localhost:5173
- The Vite dev server proxies `/api/*` requests to `localhost:8000` automatically.

### What Happens on First Run

1. The backend reads `config.yaml` for configuration
2. `database.py` creates `data/prh.db` (SQLite) if it doesn't exist
3. `data_loader.py` reads CSV files from `data/` subdirectories and populates the database
4. The API becomes available at `/api/*`
5. The frontend renders and connects to the API

---

## Project Structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full annotated directory tree and system diagrams.

Key directories for development:

| Directory | What You'll Edit | When |
|-----------|-----------------|------|
| `backend/routers/` | API endpoints | Adding/changing API behavior |
| `backend/database.py` | Database models | Adding new data types |
| `backend/data_loader.py` | Data ingestion | Changing how CSVs are loaded |
| `frontend/src/pages/` | Route pages | Adding new pages or changing layout |
| `frontend/src/components/` | UI components | Reusable UI elements |
| `frontend/src/services/api.ts` | API client | Adding new API calls |
| `frontend/src/types/` | TypeScript types | Matching backend response shapes |
| `data/` | CSV data files | Adding research data |
| `data/scripts/` | Enrichment pipeline | Data processing and NLP |

---

## Common Development Tasks

### Adding a New API Endpoint

1. Create or edit a router in `backend/routers/`:

```python
# backend/routers/data.py
@router.get("/my-endpoint")
async def get_my_data(db: Session = Depends(get_db)):
    """Description of what this endpoint does."""
    results = db.query(MyModel).all()
    return results
```

2. If you need a new Pydantic response model, add it to `backend/models/schemas.py`
3. The endpoint is automatically available and documented at `/docs`

### Adding a New Frontend Page

1. Create the page component in `frontend/src/pages/MyPage.tsx`
2. Add the route in `frontend/src/App.tsx`:

```tsx
<Route path="/my-page" element={<MyPage />} />
```

3. Add navigation in the sidebar or header as needed

### Adding a New Data Type

1. Add the SQLAlchemy model in `backend/database.py`
2. Create a Pydantic response schema in `backend/models/schemas.py`
3. Add ingestion logic in `backend/data_loader.py`
4. Create API endpoints in the appropriate router
5. Add frontend types in `frontend/src/types/index.ts`
6. Add API calls in `frontend/src/services/api.ts`

### Modifying the Database

The database is auto-created from the models. To reset:

```bash
# Delete the database (it will be recreated on next startup)
# Windows:
del data\prh.db
# macOS/Linux:
rm data/prh.db
```

Then restart the backend — it will rebuild from CSV files.

---

## Building for Production

### Frontend Build

```bash
cd frontend
npm run build
```

This runs TypeScript compilation (`tsc`) and Vite build. Output goes to `frontend/dist/`.

### Deploy to Backend Static

```bash
# Copy built frontend to backend static directory
# Windows:
xcopy /E /Y frontend\dist\* backend\static\

# macOS/Linux:
mkdir -p backend/static && cp -r frontend/dist/* backend/static/
```

Or use the convenience script:

```bash
# Windows
build-and-deploy-frontend.bat
```

### PyInstaller Executable

```bash
# From project root, with venv activated
python build_executable.py
```

Output: `dist/RawHorse/` — a self-contained directory with the executable.

### Docker

```bash
# Production
docker-compose up -d

# Development (with hot reload)
docker-compose -f docker-compose.dev.yml up
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (none, uses SQLite) | PostgreSQL connection string for production |
| `SECRET_KEY` | auto-generated | JWT signing key |
| `AUTH_ENABLED` | `false` | Enable JWT authentication |
| `GITHUB_TOKEN` | (none) | Default GitHub token for contributions |

Copy `docker/.env.example` to `.env` and customize as needed.

> **Important:** Never commit `.env` files. They are in `.gitignore`.

---

## Code Style

### Python

- PEP 8 compliance
- Type hints on all function signatures
- Docstrings on public functions
- `async def` for I/O-bound operations
- Pydantic models for request/response validation
- Keep functions under 50 lines

### TypeScript/React

- Strict TypeScript (no `any` where avoidable)
- Functional components with hooks
- Interfaces for all props
- CSS files alongside components (e.g., `SearchBar.tsx` + `SearchBar.css`)
- Named exports for components: `export default function MyComponent()`

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add entity timeline visualization
fix: correct pagination offset in Browse
docs: update API reference for search endpoint
refactor: extract search logic into shared utility
ci: upgrade GitHub Actions to v4
```

---

## Troubleshooting

### Port 8000 Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <pid>

# macOS/Linux
lsof -i :8000
kill -9 <pid>
```

### Frontend Build Fails with OOM

```bash
# Increase Node.js memory limit
# Windows (PowerShell):
$env:NODE_OPTIONS="--max-old-space-size=4096"
# macOS/Linux:
export NODE_OPTIONS=--max-old-space-size=4096

cd frontend && npm run build
```

### Virtual Environment Not Found

```bash
# Recreate it
python -m venv venv
# Activate (see instructions above)
pip install -r backend/requirements.txt
```

### Database Errors After Schema Change

```bash
# Delete and rebuild
rm data/prh.db  # or del data\prh.db on Windows
# Restart the backend
```

### npm Install Fails

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Testing

### Backend

```bash
cd backend
pytest  # (when test suite is available)
```

### Frontend

```bash
cd frontend
npm run build  # Type-check + production build (catches TypeScript errors)
```

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Backend starts without errors
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Data loads correctly on startup
- [ ] Search returns results
- [ ] Browse tabs display data
- [ ] Export generates valid files
- [ ] Application runs on your platform

---

## Further Reading

- [Architecture Guide](ARCHITECTURE.md) — System diagrams and design decisions
- [API Reference](API_REFERENCE.md) — All 45 endpoints with parameters and examples
- [Contributing Guide](../CONTRIBUTING.md) — PR process, code style, data guidelines
- [Feature Roadmap](development/FEATURE_ROADMAP.md) — What's planned next
