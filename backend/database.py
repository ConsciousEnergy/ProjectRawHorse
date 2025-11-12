"""
Database initialization and management with SQLAlchemy
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


Base = declarative_base()


class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    normalized_name = Column(String, index=True, nullable=False)
    entity_type = Column(String, index=True)
    
    __table_args__ = (
        Index('idx_entity_display_name', 'display_name'),
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


class FOIATarget(Base):
    __tablename__ = "foia_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    agency = Column(String, index=True, nullable=False)
    record_request = Column(Text, nullable=False)
    timeframe = Column(String)
    relevance = Column(String)
    notes = Column(Text)


class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    target = Column(String, index=True, nullable=False)
    label = Column(String, nullable=False)
    
    __table_args__ = (
        Index('idx_relationship_source_target', 'source', 'target'),
    )


# Database connection and session management
def get_database_url(db_path: str = "data/prh.db") -> str:
    """Get SQLite database URL"""
    return f"sqlite:///{db_path}"


def init_database(db_path: str = "data/prh.db"):
    """Initialize database with tables"""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create engine
    engine = create_engine(
        get_database_url(db_path),
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
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
