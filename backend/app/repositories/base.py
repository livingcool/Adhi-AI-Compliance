"""
Generic BaseRepository[T] providing CRUD operations with built-in org_id scoping
and pagination.

Usage:
    class AISystemRepository(BaseRepository[AISystem]):
        def __init__(self, db: Session):
            super().__init__(AISystem, db)
"""

from __future__ import annotations

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import func
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic repository providing standard CRUD operations.

    All operations that accept org_id will automatically scope queries to that
    organisation — preventing cross-tenant data leakage.
    """

    def __init__(self, model: Type[T], db: Session) -> None:
        self.model = model
        self.db = db

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, entity_id: str, org_id: Optional[str] = None) -> Optional[T]:
        """Fetch a single entity by primary key, optionally scoped to org_id."""
        q = self.db.query(self.model).filter(self.model.id == entity_id)
        if org_id and hasattr(self.model, "org_id"):
            q = q.filter(self.model.org_id == org_id)
        return q.first()

    def get_all(self, org_id: str, skip: int = 0, limit: int = 50) -> List[T]:
        """List all entities for an org with pagination."""
        q = self.db.query(self.model)
        if hasattr(self.model, "org_id"):
            q = q.filter(self.model.org_id == org_id)
        return q.offset(skip).limit(limit).all()

    def count(self, org_id: Optional[str] = None) -> int:
        """Count entities, optionally scoped to org_id."""
        q = self.db.query(func.count(self.model.id))
        if org_id and hasattr(self.model, "org_id"):
            q = q.filter(self.model.org_id == org_id)
        return q.scalar() or 0

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: dict) -> T:
        """Persist a new entity and return the refreshed instance."""
        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, entity_id: str, data: dict, org_id: Optional[str] = None) -> Optional[T]:
        """
        Apply a partial update to an entity.

        Returns the updated instance, or None if not found.
        """
        instance = self.get_by_id(entity_id, org_id)
        if not instance:
            return None
        for field, value in data.items():
            setattr(instance, field, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, entity_id: str, org_id: Optional[str] = None) -> bool:
        """
        Hard-delete an entity.

        Returns True if deleted, False if not found.
        """
        instance = self.get_by_id(entity_id, org_id)
        if not instance:
            return False
        self.db.delete(instance)
        self.db.commit()
        return True
