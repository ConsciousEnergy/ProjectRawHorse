"""
Project RawHorse - FastAPI Backend
Main application entry point
"""
import os
import time
import webbrowser
import yaml

# Load .env from project root (parent of backend/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_PROJECT_ROOT, ".env")
if os.path.isfile(_env_path):
    from dotenv import load_dotenv
    load_dotenv(_env_path)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import logging

from database import init_database, get_session_maker
from data_loader import load_all_data, is_database_populated
from dependencies import set_session_local, get_db
from routers import data, analysis, export_router, contribute, search, auth_router, timeline, reconciliation, metrics, simulation, import_router

# Rate limiting: global API 100/min; auth 10/min (applied in auth_router via slowapi)
def _rate_limit_per_minute() -> int:
    return int(os.environ.get("RATE_LIMIT_PER_MINUTE", "100"))


try:
    from limiter import limiter as LIMITER, SLOWAPI_AVAILABLE
    if SLOWAPI_AVAILABLE:
        from slowapi import _rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded
except ImportError:
    LIMITER = None
    SLOWAPI_AVAILABLE = False
    RateLimitExceeded = None
    _rate_limit_exceeded_handler = None

_env = os.environ.get("ENVIRONMENT", "development")
if _env == "production":
    import json as _json
    class _JsonFormatter(logging.Formatter):
        def format(self, record):
            return _json.dumps({
                "ts": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            })
    _handler = logging.StreamHandler()
    _handler.setFormatter(_JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[_handler])
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security: max request body size (10MB)
MAX_REQUEST_BODY_BYTES = 10 * 1024 * 1024

# Trusted Hosts (empty = allow any; set via TRUSTED_HOSTS env for production)
def _trusted_hosts():
    raw = os.environ.get("TRUSTED_HOSTS", "").strip()
    if not raw:
        return None  # allow any
    return [h.strip() for h in raw.split(",") if h.strip()]


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log request duration for SLO monitoring. Adds X-Response-Time header and feeds metrics."""
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 1)
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        if request.url.path.startswith("/api/"):
            try:
                from routers.metrics import record_request
                record_request(request.url.path, response.status_code, duration_ms)
            except Exception:
                pass
            if duration_ms > 1000:
                logger.warning(f"Slow request: {request.method} {request.url.path} took {duration_ms}ms")
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related HTTP headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with body larger than MAX_REQUEST_BODY_BYTES."""
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large (max 10MB)"},
            )
        return await call_next(request)


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """Reject requests whose Host header is not in the allowed list (if configured)."""
    async def dispatch(self, request: Request, call_next):
        allowed = _trusted_hosts()
        if not allowed:
            return await call_next(request)
        host = request.headers.get("host", "").split(":")[0]
        if host not in allowed:
            return JSONResponse(status_code=400, content={"detail": "Invalid Host header"})
        return await call_next(request)


# In-memory rate limit: (key -> list of timestamps), prune older than 1 minute
_rate_limit_store: dict = {}
_rate_limit_window_sec = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global API rate limit (e.g. 100 requests per minute per IP). Auth routes use slower limit in auth_router."""
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.rstrip("/").endswith("/api/auth/login") or path.rstrip("/").endswith("/api/auth/refresh"):
            return await call_next(request)  # Auth has its own 10/min via slowapi
        key = request.client.host if request.client else "unknown"
        now = time.time()
        if key not in _rate_limit_store:
            _rate_limit_store[key] = []
        times = _rate_limit_store[key]
        times.append(now)
        # Prune older than 1 minute
        cutoff = now - _rate_limit_window_sec
        _rate_limit_store[key] = [t for t in times if t > cutoff]
        if len(_rate_limit_store[key]) > _rate_limit_per_minute():
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again later."},
            )
        return await call_next(request)

# Get project root directory (parent of backend/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load configuration from project root
config_path = os.path.join(PROJECT_ROOT, "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting Project RawHorse...")
    
    # Initialize database (resolve path relative to project root)
    db_path = os.path.join(PROJECT_ROOT, config['database']['path'])
    engine = init_database(db_path)
    session_maker = get_session_maker(engine)
    
    # Set the session maker in dependencies module
    set_session_local(session_maker)
    
    # Load data if database is empty
    db = session_maker()
    try:
        if not is_database_populated(db):
            logger.info("Database is empty, loading data...")
            load_all_data(db, config, PROJECT_ROOT)
        else:
            logger.info("Database already populated")
    finally:
        db.close()
    
    # Auto-open browser if configured
    if config['server']['auto_open_browser']:
        port = config['server']['port_range'][0]
        url = f"http://{config['server']['host']}:{port}"
        logger.info(f"Opening browser at {url}")
        webbrowser.open(url)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Project RawHorse...")


# Create FastAPI app
app = FastAPI(
    title="Project RawHorse API",
    description="API for exploring UAP/UFO research data",
    version=config['app']['version'],
    lifespan=lifespan
)

# Rate limiting (slowapi) for auth routes
if SLOWAPI_AVAILABLE and LIMITER is not None:
    app.state.limiter = LIMITER
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware (order: first added = outermost)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(TrustedHostMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Include routers
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(export_router.router, prefix="/api/export", tags=["export"])
app.include_router(contribute.router, prefix="/api/contribute", tags=["contribute"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["authentication"])
app.include_router(timeline.router, prefix="/api/timeline", tags=["timeline"])
app.include_router(reconciliation.router, prefix="/api/reconciliation", tags=["reconciliation"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(import_router.router, prefix="/api/import", tags=["import"])

@app.get("/api/health")
async def health_check():
    """Liveness probe — confirms the process is up."""
    return {"status": "healthy", "version": config['app']['version']}


@app.get("/api/ready")
async def readiness_check():
    """Readiness probe — confirms DB is reachable and tables exist."""
    from dependencies import get_db as _get_db_gen
    try:
        db = next(_get_db_gen())
        from database import Entity
        count = db.query(Entity).limit(1).count()
        db.close()
        return {"status": "ready", "entities_present": count > 0}
    except Exception as exc:
        return JSONResponse(status_code=503, content={"status": "not_ready", "detail": str(exc)})


# Mount static files (frontend) if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount static files for assets
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    # Serve logo
    @app.get("/logo.png")
    async def get_logo():
        logo_path = os.path.join(static_dir, "logo.png")
        if os.path.exists(logo_path):
            return FileResponse(logo_path)
        return {"error": "Logo not found"}
    
    # Serve PRH logo
    @app.get("/PRHLogo.png")
    async def get_prh_logo():
        logo_path = os.path.join(static_dir, "PRHLogo.png")
        if os.path.exists(logo_path):
            return FileResponse(logo_path)
        return {"error": "PRH Logo not found"}
    
    # Catch-all route for SPA - must be last!
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes"""
        # If path starts with /api, it's already been handled or is 404
        if full_path.startswith("api/"):
            return {"error": "API endpoint not found"}
        
        # Serve index.html for all other routes (React Router will handle routing)
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend not found"}
else:
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Project RawHorse API",
            "version": config['app']['version'],
            "docs": "/docs"
        }




if __name__ == "__main__":
    import uvicorn
    
    host = config['server']['host']
    port = config['server']['port_range'][0]
    
    logger.info(f"Starting server at {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
