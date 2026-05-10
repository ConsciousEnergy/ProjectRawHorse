"""
Database initialization and management with SQLAlchemy
Supports both SQLite (default/local) and PostgreSQL (production)
"""
import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, Index, DateTime, Boolean
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
    # Evidence and temporal provenance for pyramid placements
    evidence_refs = Column(Text, nullable=True)  # JSON array of citation URLs/titles
    effective_start_date = Column(Date, nullable=True)  # When entity entered this level
    effective_end_date = Column(Date, nullable=True)  # When entity left this level (null = current)
    
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
    status = Column(String, index=True, default="draft")  # draft, submitted, acknowledged, responded, closed
    submitted_at = Column(Date)
    response_due_at = Column(Date, index=True)
    responded_at = Column(Date)
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    is_overdue = Column(Boolean, default=False, index=True)
    reference_url = Column(Text)
    archive_url = Column(Text)


class Relationship(Base):
    """Entity-to-entity relationship with optional enrichment.

    Core: source, target, label. Optional: description, relationship_type
    (e.g. affiliation, leadership, funding, technology_transfer, operates_at),
    source_citation, start_date, end_date. CSV loader supports these when present.
    """
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    target = Column(String, index=True, nullable=False)
    label = Column(String, nullable=False)
    description = Column(Text)
    relationship_type = Column(String, index=True)  # affiliation, leadership, funding, technology_transfer, operates_at
    source_citation = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    
    __table_args__ = (
        Index('idx_relationship_source_target', 'source', 'target'),
        Index('idx_relationship_type', 'relationship_type'),
    )


class TimelineEvent(Base):
    """Historical events with tiered confidence and mandatory citations."""
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_date = Column(Date, index=True, nullable=False)
    date_precision = Column(String, default="exact")  # exact, month_only, year_only
    title = Column(String, nullable=False)
    summary = Column(Text)
    category = Column(String, index=True)  # crash_retrieval, legislation, disclosure, military, scientific, whistleblower
    region = Column(String, index=True)
    confidence_tier = Column(String, index=True, nullable=False)  # confirmed, corroborated, contested
    related_entities = Column(Text)  # JSON array of entity display_names

    __table_args__ = (
        Index('idx_timeline_date', 'event_date'),
        Index('idx_timeline_category', 'category'),
        Index('idx_timeline_confidence', 'confidence_tier'),
    )


class TimelineSource(Base):
    """Citation records for timeline events. Every event requires at least one."""
    __tablename__ = "timeline_sources"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True, nullable=False)  # FK to TimelineEvent.event_id
    source_type = Column(String)  # government_record, journalism, academic, testimony, foia
    source_title = Column(String)
    source_url = Column(Text)
    source_date = Column(Date)
    notes = Column(Text)


class ReCrConfidence(Base):
    """Confidence mappings for Reverse Engineering / Crash Retrieval links."""
    __tablename__ = "re_cr_confidence"

    id = Column(Integer, primary_key=True, index=True)
    subject_type = Column(String, index=True, nullable=False)  # entity, money_flow, relationship, event
    subject_id = Column(String, index=True, nullable=False)  # entity_id, edge_id, rel key, or event_id
    confidence_score = Column(Float, index=True, nullable=False)  # 0.0 -> 1.0
    confidence_tier = Column(String, index=True, nullable=False)  # confirmed, corroborated, contested
    evidence_refs = Column(Text)  # JSON array/string of citations
    effective_start_date = Column(Date, index=True)
    effective_end_date = Column(Date, index=True)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('idx_recr_subject', 'subject_type', 'subject_id'),
        Index('idx_recr_tier_score', 'confidence_tier', 'confidence_score'),
    )


class PendingContribution(Base):
    """User-submitted data contributions awaiting admin review."""
    __tablename__ = "pending_contributions"

    id = Column(Integer, primary_key=True, index=True)
    contribution_type = Column(String, index=True, nullable=False)  # entity, money_flow, award, foia_target
    status = Column(String, index=True, default="pending", nullable=False)  # pending, approved, rejected
    data_json = Column(Text, nullable=False)  # JSON-serialized contribution payload
    contributor_name = Column(String)
    contributor_email = Column(String)
    notes = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String)
    review_notes = Column(Text)

    __table_args__ = (
        Index('idx_contribution_status', 'status'),
        Index('idx_contribution_submitted', 'submitted_at'),
    )


class AuditLog(Base):
    """Immutable audit log for sensitive operations (data refresh, admin actions, contributions)."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)  # data_refresh, admin_login, contribution, etc.
    actor = Column(String, default="system")  # username or "system"
    resource = Column(String)  # affected resource identifier
    detail = Column(Text)  # JSON or human-readable detail
    ip_address = Column(String)
    success = Column(Integer, default=1)  # 1=success, 0=failure

    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_action', 'action'),
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

    # SQLite: add new columns if missing (no-op for new DBs); tables auto-created by create_all above
    if db_type == "sqlite":
        _migrate_relationship_columns(engine)
        _migrate_entity_pyramid_columns(engine)
        _migrate_foia_lifecycle_columns(engine)

    return engine


def _migrate_relationship_columns(engine):
    """Add description, relationship_type, source_citation, start_date, end_date to relationships if missing."""
    from sqlalchemy import text
    col_types = {
        "description": "TEXT",
        "relationship_type": "TEXT",
        "source_citation": "TEXT",
        "start_date": "DATE",
        "end_date": "DATE",
    }
    try:
        with engine.connect() as conn:
            r = conn.execute(text("PRAGMA table_info(relationships)"))
            cols = {row[1] for row in r}
            for col, ctype in col_types.items():
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE relationships ADD COLUMN {col} {ctype}"))
                    conn.commit()
                    logger.info(f"Added column relationships.{col}")
    except Exception as e:
        logger.warning(f"Migration of relationships table skipped: {e}")


def _migrate_entity_pyramid_columns(engine):
    """Add evidence_refs, effective_start_date, effective_end_date to entities if missing."""
    from sqlalchemy import text
    col_types = {
        "evidence_refs": "TEXT",
        "effective_start_date": "DATE",
        "effective_end_date": "DATE",
    }
    try:
        with engine.connect() as conn:
            r = conn.execute(text("PRAGMA table_info(entities)"))
            cols = {row[1] for row in r}
            for col, ctype in col_types.items():
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE entities ADD COLUMN {col} {ctype}"))
                    conn.commit()
                    logger.info(f"Added column entities.{col}")
    except Exception as e:
        logger.warning(f"Migration of entities table skipped: {e}")


def _migrate_foia_lifecycle_columns(engine):
    """Add FOIA lifecycle tracking columns if missing."""
    from sqlalchemy import text
    col_types = {
        "status": "TEXT",
        "submitted_at": "DATE",
        "response_due_at": "DATE",
        "responded_at": "DATE",
        "estimated_cost": "REAL",
        "actual_cost": "REAL",
        "is_overdue": "BOOLEAN",
        "reference_url": "TEXT",
        "archive_url": "TEXT",
    }
    try:
        with engine.connect() as conn:
            r = conn.execute(text("PRAGMA table_info(foia_targets)"))
            cols = {row[1] for row in r}
            for col, ctype in col_types.items():
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE foia_targets ADD COLUMN {col} {ctype}"))
                    conn.commit()
                    logger.info(f"Added column foia_targets.{col}")
    except Exception as e:
        logger.warning(f"Migration of foia_targets table skipped: {e}")


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
