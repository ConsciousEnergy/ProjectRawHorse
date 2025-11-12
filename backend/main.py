"""
Project RawHorse - FastAPI Backend
Main application entry point
"""
import os
import webbrowser
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging

from database import init_database, get_session_maker
from data_loader import load_all_data, is_database_populated
from dependencies import set_session_local, get_db
from routers import data, analysis, export_router, contribute

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(export_router.router, prefix="/api/export", tags=["export"])
app.include_router(contribute.router, prefix="/api/contribute", tags=["contribute"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


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
