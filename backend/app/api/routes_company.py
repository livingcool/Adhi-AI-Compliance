from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.store.models import CompanyProfile, get_db_session
from app.api.compliance_schemas import CompanyProfileCreate, CompanyProfileUpdate, CompanyProfileResponse
from app.middleware.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/company-profiles", response_model=List[CompanyProfileResponse])
def list_company_profiles(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    return db.query(CompanyProfile).filter(CompanyProfile.org_id == current_user.org_id).all()


@router.get("/company-profiles/{profile_id}", response_model=CompanyProfileResponse)
def get_company_profile(
    profile_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.id == profile_id, CompanyProfile.org_id == current_user.org_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    return profile


@router.post("/company-profiles", response_model=CompanyProfileResponse, status_code=201)
def create_company_profile(
    payload: CompanyProfileCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    data = payload.model_dump()
    data["org_id"] = current_user.org_id
    profile = CompanyProfile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/company-profiles/{profile_id}", response_model=CompanyProfileResponse)
def update_company_profile(
    profile_id: str,
    payload: CompanyProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.id == profile_id, CompanyProfile.org_id == current_user.org_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/company-profiles/{profile_id}", status_code=204)
def delete_company_profile(
    profile_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.id == profile_id, CompanyProfile.org_id == current_user.org_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    db.delete(profile)
    db.commit()
