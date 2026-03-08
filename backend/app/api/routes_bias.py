from __future__ import annotations

import uuid
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.store.models import get_db_session
from app.api.compliance_schemas import BiasAuditCreate, BiasAuditUpdate, BiasAuditResponse, AuditStatus
from app.services.bias_auditor import analyze_bias, BiasAuditResult
from app.middleware.auth import CurrentUser, get_current_user
from app.repositories.bias_audit_repo import BiasAuditRepository

router = APIRouter()


def _get_repo(db: Session = Depends(get_db_session)) -> BiasAuditRepository:
    return BiasAuditRepository(db)


def _result_to_findings(result: BiasAuditResult) -> Dict[str, Any]:
    per_attribute = [asdict(m) for m in result.per_attribute]
    return {
        "summary_findings": result.summary_findings,
        "summary_recommendations": result.summary_recommendations,
        "per_attribute": per_attribute,
        "dataset_row_count": result.dataset_row_count,
        "dataset_column_count": result.dataset_column_count,
        "protected_attributes_analyzed": result.protected_attributes_analyzed,
        "raw_details": result.raw_details,
    }


@router.get("/bias-audits")
def list_bias_audits(
    skip: int = 0,
    limit: int = 50,
    ai_system_id: Optional[str] = None,
    overall_status: Optional[AuditStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    from app.store.models import BiasAudit
    q = db.query(BiasAudit).filter(BiasAudit.org_id == current_user.org_id)
    if ai_system_id:
        q = q.filter(BiasAudit.ai_system_id == ai_system_id)
    if overall_status:
        q = q.filter(BiasAudit.overall_status == overall_status.value)
    q = q.order_by(BiasAudit.audit_date.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"items": [BiasAuditResponse.model_validate(i) for i in items], "total": total, "skip": skip, "limit": limit}


@router.get("/bias-audits/{audit_id}", response_model=BiasAuditResponse)
def get_bias_audit(
    audit_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    audit = repo.get_by_id(audit_id, current_user.org_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Bias audit not found")
    return audit


@router.post("/bias-audits", response_model=BiasAuditResponse, status_code=201)
def create_bias_audit(
    payload: BiasAuditCreate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    data = payload.model_dump()
    data["org_id"] = current_user.org_id
    data["overall_status"] = data["overall_status"].value
    return repo.create(data)


@router.patch("/bias-audits/{audit_id}", response_model=BiasAuditResponse)
def update_bias_audit(
    audit_id: str,
    payload: BiasAuditUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    updates = {}
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "overall_status" and value is not None:
            value = value.value
        updates[field] = value
    audit = repo.update(audit_id, updates, current_user.org_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Bias audit not found")
    return audit


@router.delete("/bias-audits/{audit_id}", status_code=204)
def delete_bias_audit(
    audit_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    deleted = repo.delete(audit_id, current_user.org_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bias audit not found")


@router.post("/bias-audits/upload", response_model=BiasAuditResponse, status_code=201)
async def upload_and_analyze(
    file: UploadFile = File(...),
    ai_system_id: str = Form(...),
    dataset_description: Optional[str] = Form(None),
    protected_attributes: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    content = await file.read()
    filename = file.filename or ""
    file_type = "json" if filename.lower().endswith(".json") else "csv"
    attrs: Optional[List[str]] = None
    if protected_attributes:
        attrs = [a.strip() for a in protected_attributes.split(",") if a.strip()]
    result: BiasAuditResult = analyze_bias(content, file_type, attrs)
    findings = _result_to_findings(result)
    return repo.create({
        "id": str(uuid.uuid4()),
        "ai_system_id": ai_system_id,
        "org_id": current_user.org_id,
        "dataset_description": dataset_description or filename,
        "demographic_parity_score": result.demographic_parity_score,
        "disparate_impact_ratio": result.disparate_impact_ratio,
        "overall_status": result.overall_status,
        "findings": findings,
    })


@router.post("/bias-audits/{system_id}/run", response_model=BiasAuditResponse, status_code=201)
async def run_audit_for_system(
    system_id: str,
    file: UploadFile = File(...),
    dataset_description: Optional[str] = Form(None),
    protected_attributes: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    content = await file.read()
    filename = file.filename or ""
    file_type = "json" if filename.lower().endswith(".json") else "csv"
    attrs: Optional[List[str]] = None
    if protected_attributes:
        attrs = [a.strip() for a in protected_attributes.split(",") if a.strip()]
    result: BiasAuditResult = analyze_bias(content, file_type, attrs)
    findings = _result_to_findings(result)
    return repo.create({
        "id": str(uuid.uuid4()),
        "ai_system_id": system_id,
        "org_id": current_user.org_id,
        "dataset_description": dataset_description or filename,
        "demographic_parity_score": result.demographic_parity_score,
        "disparate_impact_ratio": result.disparate_impact_ratio,
        "overall_status": result.overall_status,
        "findings": findings,
    })


@router.get("/bias-audits/{system_id}/history", response_model=List[BiasAuditResponse])
def audit_history(
    system_id: str,
    limit: int = 20,
    current_user: CurrentUser = Depends(get_current_user),
    repo: BiasAuditRepository = Depends(_get_repo),
):
    return repo.get_by_system(system_id, current_user.org_id, limit=limit)
