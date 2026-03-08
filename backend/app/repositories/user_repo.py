"""Repository for User entities."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import User


class UserRepository(BaseRepository[User]):

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_email(self, email: str) -> Optional[User]:
        """Look up a user by email address (case-sensitive)."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_org(self, org_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users belonging to a specific organisation."""
        return (
            self.db.query(User)
            .filter(User.org_id == org_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_admins(self, org_id: str) -> List[User]:
        """Return all admin users for an organisation."""
        return (
            self.db.query(User)
            .filter(User.org_id == org_id, User.role == "admin")
            .all()
        )


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_user_repo(db) -> UserRepository:
    return UserRepository(db)
