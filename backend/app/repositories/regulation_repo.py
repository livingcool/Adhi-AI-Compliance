"""Repository for Regulation entities."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import Regulation


class RegulationRepository(BaseRepository[Regulation]):

    def __init__(self, db: Session) -> None:
        super().__init__(Regulation, db)

    # ------------------------------------------------------------------
    # Overrides — Regulation has no org_id; exclude soft-deleted rows
    # ------------------------------------------------------------------

    def _base_query(self):
        """Return a base query that always excludes soft-deleted regulations."""
        return self.db.query(Regulation).filter(Regulation.is_deleted == False)

    def get_by_id(self, entity_id: str, org_id: Optional[str] = None) -> Optional[Regulation]:
        return self._base_query().filter(Regulation.id == entity_id).first()

    def get_all(self, org_id: str = None, skip: int = 0, limit: int = 200) -> List[Regulation]:
        return self._base_query().offset(skip).limit(limit).all()

    def count(self, org_id: Optional[str] = None) -> int:
        from sqlalchemy import func
        return self.db.query(func.count(Regulation.id)).filter(Regulation.is_deleted == False).scalar() or 0

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_jurisdiction(self, jurisdiction: str) -> List[Regulation]:
        """Return all active regulations for a given jurisdiction."""
        return (
            self._base_query()
            .filter(Regulation.jurisdiction == jurisdiction)
            .order_by(Regulation.created_at.desc())
            .all()
        )

    def get_by_category(self, category: str) -> List[Regulation]:
        """Return all active regulations for a given category."""
        return (
            self._base_query()
            .filter(Regulation.category == category)
            .order_by(Regulation.created_at.desc())
            .all()
        )

    def search(
        self,
        query: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Regulation]:
        """
        Filtered search across name/short_name.
        All parameters are optional and cumulative.
        """
        q = self._base_query()
        if jurisdiction:
            q = q.filter(Regulation.jurisdiction == jurisdiction)
        if category:
            q = q.filter(Regulation.category == category)
        if query:
            q = q.filter(Regulation.name.ilike(f"%{query}%"))
        return q.order_by(Regulation.created_at.desc()).all()

    def soft_delete(self, regulation_id: str) -> bool:
        """Mark a regulation as deleted without removing the row."""
        reg = self.db.query(Regulation).filter(Regulation.id == regulation_id).first()
        if not reg:
            return False
        reg.is_deleted = True
        self.db.commit()
        return True


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_regulation_repo(db) -> RegulationRepository:
    return RegulationRepository(db)
