"""
Auth routes — register, login, refresh, and me.
"""
from __future__ import annotations
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.store.models import User, CompanyProfile, get_db_session
from app.store.metadata_store import Organization, ServiceProvider
from app.api.compliance_schemas import UserResponse
from app.middleware.auth import CurrentUser, get_current_user

logger = logging.getLogger("adhi_compliance.auth")
router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    org_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None

def _supabase_admin():
    from supabase import create_client
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=503, detail="Supabase not configured.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def _supabase_anon():
    from supabase import create_client
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503, detail="Supabase not configured.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

def _get_or_create_service_provider(db: Session) -> ServiceProvider:
    sp = db.query(ServiceProvider).first()
    if not sp:
        sp = ServiceProvider(
            id=str(uuid.uuid4()),
            business_name="Adhi Compliance",
            subscription_plan="professional",
            admin_email="admin@adhi-compliance.ai",
        )
        db.add(sp)
        db.flush()
    return sp

@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="A user with this email already exists.")
    supabase_user_id: Optional[str] = None
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            admin = _supabase_admin()
            auth_response = admin.auth.admin.create_user(
                {"email": payload.email, "password": payload.password, "email_confirm": True}
            )
            supabase_user_id = auth_response.user.id
        except Exception as exc:
            logger.warning("Supabase Auth creation failed (fallback): %s", exc)
    user_id = supabase_user_id or str(uuid.uuid4())
    sp = _get_or_create_service_provider(db)
    slug_base = payload.org_name.lower().replace(" ", "-").replace(".", "-")
    slug = slug_base
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1
    org = Organization(id=str(uuid.uuid4()), service_provider_id=sp.id, name=payload.org_name, slug=slug)
    db.add(org)
    db.flush()
    user = User(id=user_id, email=payload.email, name=payload.name, role="admin", org_id=org.id)
    db.add(user)
    db.add(CompanyProfile(id=str(uuid.uuid4()), name=payload.org_name, org_id=org.id))
    db.commit()
    db.refresh(user)
    return user

@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    try:
        anon = _supabase_anon()
        result = anon.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        session = result.session
        if not session:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return TokenResponse(access_token=session.access_token, refresh_token=session.refresh_token, expires_in=session.expires_in)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Login failed for %s: %s", payload.email, exc)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest):
    try:
        anon = _supabase_anon()
        result = anon.auth.refresh_session(payload.refresh_token)
        session = result.session
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")
        return TokenResponse(access_token=session.access_token, refresh_token=session.refresh_token, expires_in=session.expires_in)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Token refresh failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User record not found.")
    return user
