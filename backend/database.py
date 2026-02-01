"""
Database initialization and management with SQLAlchemy
Supports both SQLite (default/local) and PostgreSQL (production)
"""
import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, Index, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

# Database type detection
def get_database_type() -> str:
    """Determine database type from environment"""
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
        return 'postgresql'
    return 'sqlite'


class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    normalized_name = Column(String, index=True, nullable=False)
    entity_type = Column(String, index=True)
    # Intelligence stack level for filtering (1-6 hierarchy)
    # 1=Control Group, 2=Administrators, 3=FFRDCs, 4=Prime Contractors, 5=Facilities, 6=Programs
    intel_stack_level = Column(Integer, index=True, nullable=True)
    
    __table_args__ = (
        Index('idx_entity_display_name', 'display_name'),
        Index('idx_entity_intel_level', 'intel_stack_level'),
    )


class MoneyFlow(Base):
    __tablename__ = "money_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    target = Column(String, index=True, nullable=False)
    relationship = Column(String)
    amount_usd = Column(Float, index=True)
    start_date = Column(Date, index=True)
    end_date = Column(Date)
    source_citation = Column(Text)
    edge_id = Column(String, unique=True)
    source_norm = Column(String, index=True)
    target_norm = Column(String, index=True)
    
    __table_args__ = (
        Index('idx_money_flow_amount', 'amount_usd'),
        Index('idx_money_flow_date', 'start_date'),
    )


class Award(Base):
    __tablename__ = "awards"
    
    id = Column(Integer, primary_key=True, index=True)
    piid = Column(String, index=True)
    recipient_name = Column(String, index=True)
    recipient_uei = Column(String, index=True)
    recipient_duns = Column(String, index=True)
    awarding_agency = Column(String, index=True)
    funding_agency = Column(String, index=True)
    award_amount = Column(Float, index=True)
    action_date = Column(Date, index=True)
    description = Column(Text)
    naics_code = Column(String, index=True)
    psc_code = Column(String, index=True)
    
    __table_args__ = (
        Index('idx_award_agency', 'awarding_agency'),
        Index('idx_award_amount', 'award_amount'),
        Index('idx_award_date', 'action_date'),
    )


class MaterialsFlow(Base):
    """Track non-financial material and technology transfers"""
    __tablename__ = "materials_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    target = Column(String, index=True, nullable=False)
    material_type = Column(String, index=True)  # technology, equipment, IP, etc.
    relationship = Column(String)  # Technology Transfer, Material Supply, IP Licensing, etc.
    description = Column(Text)
    start_date = Column(Date, index=True)
    end_date = Column(Date)
    source_citation = Column(Text)
    edge_id = Column(String, unique=True)
    source_norm = Column(String, index=True)
    target_norm = Column(String, index=True)
    
    __table_args__ = (
        Index('idx_materials_flow_type', 'material_type'),
        Index('idx_materials_flow_date', 'start_date'),
    )


class FOIATarget(Base):
    __tablename__ = "foia_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    agency = Column(String, index=True, nullable=False)
    record_request = Column(Text, nullable=False)
    timeframe = Column(String)
    relevance = Column(String)
    notes = Column(Text)
    # Quality scoring fields
    specificity_score = Column(Float, default=0.0)  # 0-1: How specific is the request?
    likelihood_score = Column(Float, default=0.0)  # 0-1: Likelihood of getting a response
    priority_score = Column(Float, default=0.0)  # 0-1: Overall priority/importance
    quality_notes = Column(Text)  # Notes about quality assessment


class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    target = Column(String, index=True, nullable=False)
    label = Column(String, nullable=False)
    
    __table_args__ = (
        Index('idx_relationship_source_target', 'source', 'target'),
    )


class SearchLog(Base):
    """Track search queries for analytics and improvements"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True, nullable=False)
    results_count = Column(Integer, nullable=False)
    search_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Integer)
    types_searched = Column(String)  # Comma-separated list of types
    
    __table_args__ = (
        Index('idx_search_timestamp', 'search_timestamp'),
        Index('idx_search_query', 'query'),
    )


class DataVersion(Base):
    """Track data version for cache invalidation and refresh detection"""
    __tablename__ = "data_version"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, default=1, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_modified_by = Column(String)  # Optional: track who/what modified data


# Database connection and session management
def get_database_url(db_path: str = "data/prh.db") -> str:
    """Get database URL from environment or default to SQLite
    
    Supports:
    - PostgreSQL: Set DATABASE_URL environment variable
    - SQLite: Default, uses db_path parameter
    """
    # Check for PostgreSQL connection string
    pg_url = os.environ.get('DATABASE_URL', '')
    if pg_url:
        # Handle Heroku-style postgres:// URLs (need postgresql://)
        if pg_url.startswith('postgres://'):
            pg_url = pg_url.replace('postgres://', 'postgresql://', 1)
        logger.info("Using PostgreSQL database")
        return pg_url
    
    # Fall back to SQLite
    sqlite_path = os.environ.get('SQLITE_PATH', db_path)
    logger.info(f"Using SQLite database: {sqlite_path}")
    return f"sqlite:///{sqlite_path}"


def init_database(db_path: str = "data/prh.db"):
    """Initialize database with tables
    
    Automatically detects database type and configures appropriately:
    - SQLite: StaticPool for thread safety in single-file database
    - PostgreSQL: QueuePool for connection pooling in multi-user environment
    """
    db_url = get_database_url(db_path)
    db_type = get_database_type()
    
    if db_type == 'postgresql':
        # PostgreSQL configuration with connection pooling
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        logger.info("PostgreSQL engine initialized with connection pooling")
    else:
        # SQLite configuration
        # Ensure data directory exists
        if 'sqlite:///' in db_url:
            sqlite_path = db_url.replace('sqlite:///', '')
            if os.path.dirname(sqlite_path):
                os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        logger.info("SQLite engine initialized")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    return engine


def get_session_maker(engine):
    """Get session maker for database operations"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI
def get_db(SessionLocal):
    """Get database session for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check function
def check_database_health(engine) -> dict:
    """Check database connectivity and return status"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "database_type": get_database_type(),
            "connection": "ok"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_type": get_database_type(),
            "error": str(e)
        }
