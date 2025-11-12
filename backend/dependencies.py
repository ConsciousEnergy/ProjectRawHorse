"""
Shared dependencies for FastAPI routes
"""
from typing import Generator
from sqlalchemy.orm import Session

# Global database session maker (will be set by main.py during startup)
SessionLocal = None
_db_initialized = False


def set_session_local(session_maker):
    """Set the global session maker (called from main.py during startup)"""
    global SessionLocal, _db_initialized
    SessionLocal = session_maker
    _db_initialized = True


def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI routes"""
    if not _db_initialized or SessionLocal is None:
        raise RuntimeError("Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

