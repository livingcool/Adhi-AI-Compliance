from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.store.models import get_db_session
from app.api.compliance_schemas import RegulationCreate, RegulationUpdate, RegulationResponse
from app.middleware.auth import CurrentUser, get_current_user
from app.repositories.regulation_repo import RegulationRepository

router = APIRouter()


def _get_repo(db: Session = Depends(get_db_session)) -> RegulationRepository:
    return RegulationRepository(db)


@router.get("/regulations")
def list_regulations(
    skip: int = 0,
    limit: int = 200,
    jurisdiction: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    repo: RegulationRepository = Depends(_get_repo),
) -> Dict[str, Any]:
    from app.services.web_search import get_live_regulations
    
    items = repo.search(query=search, jurisdiction=jurisdiction, category=category)
    total = len(items)
    page_items = items[skip : skip + limit]
    
    # Execute Live Internet Search
    live_items = []
    if skip == 0 and not search:
        try:
            live_items = get_live_regulations()
        except Exception:
            pass

    db_items = [RegulationResponse.model_validate(i).model_dump() for i in page_items]
    return {"items": live_items + db_items, "total": total + len(live_items), "skip": skip, "limit": limit}


@router.get("/regulations/{regulation_id}", response_model=RegulationResponse)
def get_regulation(
    regulation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: RegulationRepository = Depends(_get_repo),
):
    regulation = repo.get_by_id(regulation_id)
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return regulation


@router.post("/regulations", response_model=RegulationResponse, status_code=201)
def create_regulation(
    payload: RegulationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: RegulationRepository = Depends(_get_repo),
):
    return repo.create(payload.model_dump())


@router.patch("/regulations/{regulation_id}", response_model=RegulationResponse)
def update_regulation(
    regulation_id: str,
    payload: RegulationUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    repo: RegulationRepository = Depends(_get_repo),
):
    regulation = repo.update(regulation_id, payload.model_dump(exclude_unset=True))
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return regulation


@router.delete("/regulations/{regulation_id}", status_code=204)
def delete_regulation(
    regulation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo: RegulationRepository = Depends(_get_repo),
):
    deleted = repo.delete(regulation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Regulation not found")
