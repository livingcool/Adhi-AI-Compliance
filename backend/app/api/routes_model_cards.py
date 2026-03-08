"""
Model Card API routes.
"""
from __future__ import annotations
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.store.models import get_db_session
from app.api.compliance_schemas import ModelCardResponse
from app.services.model_card_generator import generate_model_card, export_model_card_pdf
from app.middleware.auth import CurrentUser, get_current_user
from app.repositories.ai_system_repo import AISystemRepository
from app.repositories.bias_audit_repo import BiasAuditRepository
from app.repositories.compliance_repo import ComplianceRepository
from app.repositories.model_card_repo import ModelCardRepository

router = APIRouter()


def _get_repos(db: Session = Depends(get_db_session)):
    return {
        "ai_system": AISystemRepository(db),
        "bias_audit": BiasAuditRepository(db),
        "compliance": ComplianceRepository(db),
        "model_card": ModelCardRepository(db),
    }


@router.post("/model-cards/{system_id}/generate", response_model=ModelCardResponse, status_code=201)
def generate(
    system_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repos: dict = Depends(_get_repos),
):
    org_id = current_user.org_id
    ai_system = repos["ai_system"].get_by_id(system_id, org_id)
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI system not found")

    bias_audits = repos["bias_audit"].get_by_system(system_id, org_id, limit=10)
    compliance_checks = repos["compliance"].get_by_system(system_id, org_id)

    content: Dict[str, Any] = generate_model_card(ai_system, bias_audits, compliance_checks)
    version_num = repos["model_card"].count_for_system(system_id, org_id) + 1

    return repos["model_card"].create({
        "id": str(uuid.uuid4()),
        "ai_system_id": system_id,
        "org_id": org_id,
        "content": content,
        "version": f"{version_num}.0",
    })


@router.get("/model-cards/{system_id}", response_model=ModelCardResponse)
def get_model_card(
    system_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repos: dict = Depends(_get_repos),
):
    card = repos["model_card"].get_latest_for_system(system_id, current_user.org_id)
    if not card:
        raise HTTPException(status_code=404, detail="No model card found. Generate one first.")
    return card


@router.get("/model-cards/{system_id}/pdf")
def download_pdf(
    system_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repos: dict = Depends(_get_repos),
):
    card = repos["model_card"].get_latest_for_system(system_id, current_user.org_id)
    if not card:
        raise HTTPException(status_code=404, detail="No model card found.")
    file_bytes = export_model_card_pdf(card.content)
    is_pdf = file_bytes[:4] == b"%PDF"
    media_type = "application/pdf" if is_pdf else "text/html"
    ext = "pdf" if is_pdf else "html"
    system_name = (card.content or {}).get("model_details", {}).get("name", system_id)
    filename = f"model_card_{system_name}_v{card.version}.{ext}".replace(" ", "_")
    return Response(content=file_bytes, media_type=media_type,
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
