"""Repository for BiasAudit entities."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import BiasAudit


class BiasAuditRepository(BaseRepository[BiasAudit]):

    def __init__(self, db: Session) -> None:
        super().__init__(BiasAudit, db)

    def get_by_system(self, system_id: str, org_id: str, limit: int = 20) -> List[BiasAudit]:
        """Return audit history for a specific AI system, newest first."""
        return (
            self.db.query(BiasAudit)
            .filter(BiasAudit.ai_system_id == system_id, BiasAudit.org_id == org_id)
            .order_by(BiasAudit.audit_date.desc())
            .limit(limit)
            .all()
        )

    def get_latest_for_system(self, system_id: str, org_id: str) -> Optional[BiasAudit]:
        """Return the most recent audit for an AI system."""
        return (
            self.db.query(BiasAudit)
            .filter(BiasAudit.ai_system_id == system_id, BiasAudit.org_id == org_id)
            .order_by(BiasAudit.audit_date.desc())
            .first()
        )


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_bias_audit_repo(db) -> BiasAuditRepository:
    return BiasAuditRepository(db)
