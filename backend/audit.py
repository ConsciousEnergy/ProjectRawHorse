"""
Immutable audit logging for sensitive operations.

Usage:
    from audit import log_audit
    log_audit(db, action="data_refresh", actor="api", detail="Loaded 150 entities")
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database import AuditLog

logger = logging.getLogger(__name__)


def log_audit(
    db: Session,
    action: str,
    actor: str = "system",
    resource: Optional[str] = None,
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
    success: bool = True,
):
    try:
        entry = AuditLog(
            timestamp=datetime.utcnow(),
            action=action,
            actor=actor,
            resource=resource,
            detail=detail,
            ip_address=ip_address,
            success=1 if success else 0,
        )
        db.add(entry)
        db.commit()
    except Exception as exc:
        logger.warning(f"Audit log write failed: {exc}")
        db.rollback()
