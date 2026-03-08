"""
Seed API routes — protected by require_admin.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.store.models import Regulation, get_db_session
from app.services.regulation_loader import seed_regulations, is_seeded
from app.services.regulation_embedder import get_regulation_embedder
from app.middleware.auth import CurrentUser, require_admin

router = APIRouter()


@router.post("/seed/regulations", status_code=200)
def seed_all_regulations(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    """Seed the regulation knowledge base (admin only)."""
    try:
        seed_result = seed_regulations(db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB seed failed: {exc}")
    try:
        embedder = get_regulation_embedder()
        embed_result = embedder.embed_all_regulations(db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}")
    return {"status": "ok", "seed": seed_result, "embed": embed_result}


@router.get("/seed/status")
def seed_status(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    """Check seed status (admin only)."""
    regulation_count = db.query(Regulation).count()
    seeded = is_seeded(db)
    embedder = get_regulation_embedder()
    index_status = embedder.status()
    return {"regulations_in_db": regulation_count, "is_seeded": seeded, "vector_index": index_status}
