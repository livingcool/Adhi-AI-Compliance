from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.store.metadata_store import get_db, Organization, ServiceProvider, ensure_default_provider

router = APIRouter()

class OrganizationSchema(BaseModel):
    id: str
    name: str
    slug: str
    
    class Config:
        from_attributes = True

@router.get("/organizations", response_model=List[OrganizationSchema])
async def list_organizations(db: Session = Depends(get_db)):
    """
    Returns a list of all client organizations for the service provider.
    For the POC, we assume a single service provider.
    """
    provider = ensure_default_provider(db)
    orgs = db.query(Organization).filter(Organization.service_provider_id == provider.id).all()
    return orgs

@router.post("/organizations", response_model=OrganizationSchema)
async def create_new_organization(name: str, slug: str, db: Session = Depends(get_db)):
    """
    Creates a new client organization.
    """
    provider = ensure_default_provider(db)
    
    # Check if slug exists
    existing = db.query(Organization).filter(Organization.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this slug already exists.")
        
    org = Organization(name=name, slug=slug, service_provider_id=provider.id)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org
