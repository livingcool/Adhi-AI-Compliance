from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.store.models import Incident, get_db_session
from app.api.compliance_schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, IncidentSeverity, IncidentStatus,
)
from app.middleware.auth import CurrentUser, get_current_user
from app.repositories.incident_repo import IncidentRepository

router = APIRouter()


def _get_repo(db: Session = Depends(get_db_session)) -> IncidentRepository:
    return IncidentRepository(db)


@router.get("/incidents")
def list_incidents(
    skip: int = 0,
    limit: int = 50,
    ai_system_id: Optional[str] = None,
    severity: Optional[IncidentSeverity] = None,
    status: Optional[IncidentStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    q = db.query(Incident).filter(Incident.org_id == current_user.org_id)
    if ai_system_id:
        q = q.filter(Incident.ai_system_id == ai_system_id)
    if severity:
        q = q.filter(Incident.severity == severity.value)
    if status:
        q = q.filter(Incident.status == status.value)
    q = q.order_by(Incident.detected_at.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"items": [IncidentResponse.model_validate(i) for i in items], "total": total, "skip": skip, "limit": limit}


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: IncidentRepository = Depends(_get_repo),
):
    incident = repo.get_by_id(incident_id, current_user.org_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/incidents", response_model=IncidentResponse, status_code=201)
def create_incident(
    payload: IncidentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: IncidentRepository = Depends(_get_repo),
):
    data = payload.model_dump()
    data["org_id"] = current_user.org_id
    data["severity"] = data["severity"].value
    data["status"] = data["status"].value
    return repo.create(data)


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: IncidentRepository = Depends(_get_repo),
):
    updates = {}
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in ("severity", "status") and value is not None:
            value = value.value
        updates[field] = value
    incident = repo.update(incident_id, updates, current_user.org_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.delete("/incidents/{incident_id}", status_code=204)
def delete_incident(
    incident_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: IncidentRepository = Depends(_get_repo),
):
    deleted = repo.delete(incident_id, current_user.org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("/incidents/{incident_id}/timeline", response_model=IncidentResponse)
def append_timeline_event(
    incident_id: str,
    event: dict,
    current_user: CurrentUser = Depends(get_current_user),
    repo: IncidentRepository = Depends(_get_repo),
):
    incident = repo.append_timeline(incident_id, event, current_user.org_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
