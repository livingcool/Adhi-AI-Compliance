"""
Regulation Management API — admin-only endpoints.

POST /regulations/import          — bulk import regulations from JSON/CSV upload
PUT  /regulations/{id}            — edit regulation text/dates (full replace)
DELETE /regulations/{id}          — soft delete a regulation
POST /regulations/{id}/embed      — re-embed a specific regulation into vector index
GET  /regulations/updates/check   — check external feeds for regulatory updates
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.store.models import get_db_session
from app.api.compliance_schemas import RegulationResponse, RegulationUpdate
from app.middleware.auth import CurrentUser, get_current_user, require_admin
from app.repositories.regulation_repo import RegulationRepository
from app.services.regulation_updater import (
    check_for_updates,
    import_regulations_from_bytes,
    update_regulation,
)

router = APIRouter()


def _get_repo(db: Session = Depends(get_db_session)) -> RegulationRepository:
    return RegulationRepository(db)


# ---------------------------------------------------------------------------
# POST /regulations/import
# ---------------------------------------------------------------------------

@router.post(
    "/regulations/import",
    summary="Bulk import regulations from JSON or CSV file (admin only)",
    status_code=201,
)
async def import_regulations(
    file: UploadFile = File(..., description="JSON array or CSV of regulation records"),
    _admin: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Upload a JSON array or CSV file of regulations and persist them to the DB.

    JSON format: `[{"name": "...", "jurisdiction": "EU", "category": "...", ...}]`

    CSV format — required header columns:
      `name, short_name, jurisdiction, category, effective_date, enforcement_date, full_text, url`
    """
    content = await file.read()
    filename = file.filename or ""
    file_type = "json" if filename.lower().endswith(".json") else "csv"

    try:
        created = import_regulations_from_bytes(content, file_type, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "imported": len(created),
        "ids": [r.id for r in created],
    }


# ---------------------------------------------------------------------------
# PUT /regulations/{id}
# ---------------------------------------------------------------------------

@router.put(
    "/regulations/{regulation_id}",
    response_model=RegulationResponse,
    summary="Edit regulation text and/or dates (admin only)",
)
def edit_regulation(
    regulation_id: str,
    payload: RegulationUpdate,
    _admin: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> RegulationResponse:
    """Full-field update for an existing regulation record."""
    updated = update_regulation(
        reg_id=regulation_id,
        updates=payload.model_dump(exclude_unset=True),
        db=db,
        re_embed=False,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return RegulationResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# DELETE /regulations/{id}  — soft delete
# ---------------------------------------------------------------------------

@router.delete(
    "/regulations/{regulation_id}",
    status_code=204,
    summary="Soft-delete a regulation (admin only)",
)
def soft_delete_regulation(
    regulation_id: str,
    _admin: CurrentUser = Depends(require_admin),
    repo: RegulationRepository = Depends(_get_repo),
) -> None:
    deleted = repo.soft_delete(regulation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Regulation not found")


# ---------------------------------------------------------------------------
# POST /regulations/{id}/embed
# ---------------------------------------------------------------------------

@router.post(
    "/regulations/{regulation_id}/embed",
    summary="Re-embed a specific regulation into the vector index (admin only)",
)
def re_embed_regulation(
    regulation_id: str,
    _admin: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> Dict[str, str]:
    """
    Trigger re-embedding of a single regulation's full_text into the FAISS index.
    Useful after editing regulation text via PUT /regulations/{id}.
    """
    updated = update_regulation(
        reg_id=regulation_id,
        updates={},   # no field changes — just re-embed
        db=db,
        re_embed=True,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return {"status": "re-embedding triggered", "regulation_id": regulation_id}


# ---------------------------------------------------------------------------
# GET /regulations/updates/check
# ---------------------------------------------------------------------------

@router.get(
    "/regulations/updates/check",
    summary="Check external regulatory feeds for updates (admin only)",
)
def check_regulation_updates(
    _admin: CurrentUser = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Poll configured external regulatory update feeds.
    Currently returns a placeholder response — integrate external APIs here.
    """
    updates = check_for_updates()
    return {
        "available_updates": len(updates),
        "updates": updates,
        "note": "External feed integration is not yet configured. Implement check_for_updates() in regulation_updater.py.",
    }
