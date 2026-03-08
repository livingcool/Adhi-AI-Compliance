"""Repository for ModelCard entities."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import ModelCard


class ModelCardRepository(BaseRepository[ModelCard]):

    def __init__(self, db: Session) -> None:
        super().__init__(ModelCard, db)

    def get_latest_for_system(self, system_id: str, org_id: str) -> Optional[ModelCard]:
        """Return the most recently generated model card for an AI system."""
        return (
            self.db.query(ModelCard)
            .filter(ModelCard.ai_system_id == system_id, ModelCard.org_id == org_id)
            .order_by(ModelCard.generated_at.desc())
            .first()
        )

    def count_for_system(self, system_id: str, org_id: str) -> int:
        """Count how many model cards exist for a system (used for versioning)."""
        return (
            self.db.query(func.count(ModelCard.id))
            .filter(ModelCard.ai_system_id == system_id, ModelCard.org_id == org_id)
            .scalar()
            or 0
        )

    def get_history(self, system_id: str, org_id: str) -> List[ModelCard]:
        """Return all model cards for a system, newest first."""
        return (
            self.db.query(ModelCard)
            .filter(ModelCard.ai_system_id == system_id, ModelCard.org_id == org_id)
            .order_by(ModelCard.generated_at.desc())
            .all()
        )


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_model_card_repo(db) -> ModelCardRepository:
    return ModelCardRepository(db)
