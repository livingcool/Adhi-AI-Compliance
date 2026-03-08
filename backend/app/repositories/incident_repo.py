"""Repository for Incident entities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.store.models import Incident


class IncidentRepository(BaseRepository[Incident]):

    def __init__(self, db: Session) -> None:
        super().__init__(Incident, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_severity(self, severity: str, org_id: str) -> List[Incident]:
        """Return all incidents with the given severity for the org."""
        return (
            self.db.query(Incident)
            .filter(Incident.org_id == org_id, Incident.severity == severity)
            .order_by(Incident.detected_at.desc())
            .all()
        )

    def get_open_incidents(self, org_id: str) -> List[Incident]:
        """Return incidents that are still being actively worked on."""
        return (
            self.db.query(Incident)
            .filter(
                Incident.org_id == org_id,
                Incident.status.in_(["investigating", "mitigating"]),
            )
            .order_by(Incident.detected_at.desc())
            .all()
        )

    def append_timeline(self, incident_id: str, event: Dict[str, Any], org_id: Optional[str] = None) -> Optional[Incident]:
        """
        Append *event* to an incident's timeline JSON array.

        Returns the updated Incident, or None if not found.
        """
        incident = self.get_by_id(incident_id, org_id)
        if not incident:
            return None
        timeline = list(incident.timeline or [])
        timeline.append(event)
        incident.timeline = timeline
        self.db.commit()
        self.db.refresh(incident)
        return incident


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def get_incident_repo(db) -> IncidentRepository:
    return IncidentRepository(db)
