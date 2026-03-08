from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.store.models import get_db_session
from app.api.compliance_schemas import AISystemCreate, AISystemUpdate, AISystemResponse, RiskClassification
from app.middleware.auth import CurrentUser, get_current_user
from app.repositories.ai_system_repo import AISystemRepository

router = APIRouter()


def _get_repo(db: Session = Depends(get_db_session)) -> AISystemRepository:
    return AISystemRepository(db)


@router.get("/ai-systems")
def list_ai_systems(
    skip: int = 0,
    limit: int = 50,
    risk_classification: Optional[RiskClassification] = None,
    is_high_risk: Optional[bool] = None,
    current_user: CurrentUser = Depends(get_current_user),
    repo: AISystemRepository = Depends(_get_repo),
) -> Dict[str, Any]:
    org_id = current_user.org_id
    if risk_classification is not None:
        items = repo.get_by_risk_tier(risk_classification.value, org_id)
        if is_high_risk is not None:
            items = [s for s in items if s.is_high_risk == is_high_risk]
        return {"items": [AISystemResponse.model_validate(i) for i in items], "total": len(items), "skip": 0, "limit": limit}

    items = repo.get_all(org_id=org_id, skip=skip, limit=limit)
    if is_high_risk is not None:
        items = [s for s in items if s.is_high_risk == is_high_risk]
    total = repo.count(org_id)
    return {"items": [AISystemResponse.model_validate(i) for i in items], "total": total, "skip": skip, "limit": limit}


@router.get("/ai-systems/{system_id}", response_model=AISystemResponse)
def get_ai_system(
    system_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: AISystemRepository = Depends(_get_repo),
):
    system = repo.get_by_id(system_id, current_user.org_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


@router.post("/ai-systems", response_model=AISystemResponse, status_code=201)
def create_ai_system(
    payload: AISystemCreate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: AISystemRepository = Depends(_get_repo),
):
    data = payload.model_dump()
    data["org_id"] = current_user.org_id  # always use JWT-derived org_id
    data["risk_classification"] = data["risk_classification"].value
    return repo.create(data)


@router.patch("/ai-systems/{system_id}", response_model=AISystemResponse)
def update_ai_system(
    system_id: str,
    payload: AISystemUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: AISystemRepository = Depends(_get_repo),
):
    updates = {}
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "risk_classification" and value is not None:
            value = value.value
        updates[field] = value
    system = repo.update(system_id, updates, current_user.org_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


@router.delete("/ai-systems/{system_id}", status_code=204)
def delete_ai_system(
    system_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: AISystemRepository = Depends(_get_repo),
):
    deleted = repo.delete(system_id, current_user.org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="AI system not found")
