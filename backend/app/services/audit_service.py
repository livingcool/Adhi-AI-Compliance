"""
Audit Service.

Persists structured audit log entries for all create/update/delete operations
across compliance-related routes.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger("adhi.audit")


def log_action(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> "AuditLog":  # noqa: F821  (forward ref resolved at runtime)
    """
    Persist a structured audit log entry.

    Args:
        db:          SQLAlchemy session.
        action:      Verb describing the action — e.g. 'create', 'update',
                     'delete', 'scan', 'generate_report'.
        entity_type: Model name — e.g. 'ComplianceCheck', 'AISystem'.
        entity_id:   Primary key of the affected row.
        user_id:     Acting user (optional; from auth context).
        org_id:      Organisation context (optional).
        details:     Arbitrary JSON dict with extra context.
        ip_address:  Client IP address (optional).

    Returns:
        Persisted AuditLog ORM instance.
    """
    from app.store.models import AuditLog  # avoid circular import at module load

    entry = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        org_id=org_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    logger.info(
        "audit_log",
        extra={
            "audit_id": entry.id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "org_id": org_id,
        },
    )
    return entry
