from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.store.models import get_db_session
from app.api.compliance_schemas import (
    ComplianceCheckCreate, ComplianceCheckUpdate, ComplianceCheckResponse,
    ComplianceStatus, Priority,
)
from app.services.compliance_checker import check_compliance
from app.middleware.auth import CurrentUser, get_current_user
from app.repositories.compliance_repo import ComplianceRepository

router = APIRouter()


def _get_repo(db: Session = Depends(get_db_session)) -> ComplianceRepository:
    return ComplianceRepository(db)


@router.get("/compliance-checks")
def list_compliance_checks(
    skip: int = 0,
    limit: int = 50,
    ai_system_id: Optional[str] = None,
    regulation_id: Optional[str] = None,
    status: Optional[ComplianceStatus] = None,
    priority: Optional[Priority] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: ComplianceRepository = Depends(_get_repo),
) -> Dict[str, Any]:
    from app.store.models import ComplianceCheck
    q = db.query(ComplianceCheck).filter(ComplianceCheck.org_id == current_user.org_id)
    if ai_system_id:
        q = q.filter(ComplianceCheck.ai_system_id == ai_system_id)
    if regulation_id:
        q = q.filter(ComplianceCheck.regulation_id == regulation_id)
    if status:
        q = q.filter(ComplianceCheck.status == status.value)
    if priority:
        q = q.filter(ComplianceCheck.priority == priority.value)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"items": [ComplianceCheckResponse.model_validate(i) for i in items], "total": total, "skip": skip, "limit": limit}


@router.get("/compliance-checks/{check_id}", response_model=ComplianceCheckResponse)
def get_compliance_check(
    check_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: ComplianceRepository = Depends(_get_repo),
):
    check = repo.get_by_id(check_id, current_user.org_id)
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    return check


@router.post("/compliance-checks", response_model=ComplianceCheckResponse, status_code=201)
def create_compliance_check(
    payload: ComplianceCheckCreate,
    use_rag: bool = Query(default=True),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: ComplianceRepository = Depends(_get_repo),
):
    if use_rag:
        try:
            check = check_compliance(
                ai_system_id=payload.ai_system_id,
                regulation_id=payload.regulation_id,
                org_id=current_user.org_id,
                db=db,
            )
            return check
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    data = payload.model_dump()
    data["org_id"] = current_user.org_id
    data["status"] = data["status"].value
    data["priority"] = data["priority"].value
    return repo.create(data)


@router.patch("/compliance-checks/{check_id}", response_model=ComplianceCheckResponse)
def update_compliance_check(
    check_id: str,
    payload: ComplianceCheckUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: ComplianceRepository = Depends(_get_repo),
):
    updates = {}
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in ("status", "priority") and value is not None:
            value = value.value
        updates[field] = value
    check = repo.update(check_id, updates, current_user.org_id)
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    return check


@router.delete("/compliance-checks/{check_id}", status_code=204)
def delete_compliance_check(
    check_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: ComplianceRepository = Depends(_get_repo),
):
    deleted = repo.delete(check_id, current_user.org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Compliance check not found")


@router.get("/compliance-summary")
def compliance_summary(
    current_user: CurrentUser = Depends(get_current_user),
    repo: ComplianceRepository = Depends(_get_repo),
):
    """Returns SQL-aggregated count breakdown of compliance checks by status/priority."""
    return repo.get_summary(current_user.org_id)
