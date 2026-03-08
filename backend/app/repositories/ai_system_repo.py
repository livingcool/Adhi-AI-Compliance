"""Repository for AISystem entities."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import AISystem


class AISystemRepository(BaseRepository[AISystem]):

    def __init__(self, db: Session) -> None:
        super().__init__(AISystem, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_risk_tier(self, tier: str, org_id: str) -> List[AISystem]:
        """Return all AI systems with the given risk classification in the org."""
        return (
            self.db.query(AISystem)
            .filter(AISystem.org_id == org_id, AISystem.risk_classification == tier)
            .all()
        )

    def search_by_name(self, query: str, org_id: str) -> List[AISystem]:
        """Case-insensitive name search within an org."""
        return (
            self.db.query(AISystem)
            .filter(AISystem.org_id == org_id, AISystem.name.ilike(f"%{query}%"))
            .all()
        )

    def get_compliance_score_summary(self, org_id: str) -> dict:
        """
        Return aggregated compliance score statistics for an org.

        Keys: total, avg_score, compliant_count (score >= 70), high_risk_count.
        """
        rows = (
            self.db.query(
                func.count(AISystem.id).label("total"),
                func.avg(AISystem.compliance_score).label("avg_score"),
            )
            .filter(AISystem.org_id == org_id)
            .one()
        )

        compliant_count = (
            self.db.query(func.count(AISystem.id))
            .filter(AISystem.org_id == org_id, AISystem.compliance_score >= 70)
            .scalar()
            or 0
        )

        high_risk_count = (
            self.db.query(func.count(AISystem.id))
            .filter(
                AISystem.org_id == org_id,
                AISystem.risk_classification.in_(["unacceptable", "high"]),
            )
            .scalar()
            or 0
        )

        return {
            "total": rows.total or 0,
            "avg_score": round(float(rows.avg_score or 0), 2),
            "compliant_count": compliant_count,
            "high_risk_count": high_risk_count,
        }


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_ai_system_repo(db) -> AISystemRepository:
    return AISystemRepository(db)
