"""Repository for ComplianceCheck entities."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import ComplianceCheck


class ComplianceRepository(BaseRepository[ComplianceCheck]):

    def __init__(self, db: Session) -> None:
        super().__init__(ComplianceCheck, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_system(self, system_id: str, org_id: str) -> List[ComplianceCheck]:
        """Return all compliance checks for a specific AI system in the org."""
        return (
            self.db.query(ComplianceCheck)
            .filter(
                ComplianceCheck.ai_system_id == system_id,
                ComplianceCheck.org_id == org_id,
            )
            .order_by(ComplianceCheck.checked_at.desc())
            .all()
        )

    def get_summary(self, org_id: str) -> Dict[str, Any]:
        """
        Return aggregated compliance statistics for an org using SQL-level counts.

        Returns:
            total, by_status (dict), by_priority (dict)
        """
        total = (
            self.db.query(func.count(ComplianceCheck.id))
            .filter(ComplianceCheck.org_id == org_id)
            .scalar()
            or 0
        )

        status_rows = (
            self.db.query(ComplianceCheck.status, func.count(ComplianceCheck.id))
            .filter(ComplianceCheck.org_id == org_id)
            .group_by(ComplianceCheck.status)
            .all()
        )

        priority_rows = (
            self.db.query(ComplianceCheck.priority, func.count(ComplianceCheck.id))
            .filter(ComplianceCheck.org_id == org_id)
            .group_by(ComplianceCheck.priority)
            .all()
        )

        return {
            "total": total,
            "by_status": {status: count for status, count in status_rows},
            "by_priority": {priority: count for priority, count in priority_rows},
        }

    def get_upcoming_deadlines(self, days: int, org_id: str) -> List[ComplianceCheck]:
        """
        Return non-compliant checks with deadlines within *days* calendar days.
        Results ordered soonest-first.
        """
        cutoff = datetime.utcnow() + timedelta(days=days)
        return (
            self.db.query(ComplianceCheck)
            .filter(
                ComplianceCheck.org_id == org_id,
                ComplianceCheck.deadline != None,
                ComplianceCheck.deadline <= cutoff,
                ComplianceCheck.status != "compliant",
            )
            .order_by(ComplianceCheck.deadline.asc())
            .all()
        )


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_compliance_repo(db) -> ComplianceRepository:
    return ComplianceRepository(db)
