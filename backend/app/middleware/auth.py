"""
JWT authentication middleware for Adhi Compliance.

Validates Supabase-issued JWTs using two strategies:
  1. Local HS256 decode via python-jose (fast, requires SUPABASE_JWT_SECRET)
  2. Supabase Auth API call (fallback when JWT secret not configured)

Every protected route declares:
    current_user: CurrentUser = Depends(get_current_user)

Admin-only routes also add:
    _: CurrentUser = Depends(require_admin)
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.store.models import User, get_db_session

logger = logging.getLogger("adhi_compliance.auth")

# ---------------------------------------------------------------------------
# Bearer token extractor
# ---------------------------------------------------------------------------

security = HTTPBearer(auto_error=True)


# ---------------------------------------------------------------------------
# CurrentUser model returned by the dependency
# ---------------------------------------------------------------------------

class CurrentUser(BaseModel):
    id: str
    email: str
    org_id: str
    role: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Lazy Supabase client (avoid import at module level to allow config loading)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_supabase_client():
    """Return a cached Supabase anon client for JWT validation."""
    from app.config import settings
    from supabase import create_client  # type: ignore

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set for JWT validation.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _decode_jwt_local(token: str) -> Optional[dict]:
    """
    Decode and verify the JWT locally using SUPABASE_JWT_SECRET.
    Returns the payload dict, or None if the secret is not configured.
    Raises HTTPException 401 on invalid / expired token.
    """
    from app.config import settings

    if not settings.SUPABASE_JWT_SECRET:
        return None

    try:
        from jose import JWTError, jwt  # type: ignore

        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},  # Supabase sets aud='authenticated'
        )
        return payload
    except JWTError as exc:
        logger.debug("Local JWT decode failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _decode_jwt_supabase(token: str) -> tuple[str, str]:
    """
    Validate JWT via the Supabase Auth API.
    Returns (user_id, email).
    Raises HTTPException 401 on failure.
    """
    try:
        client = _get_supabase_client()
        response = client.auth.get_user(token)
        if not response or not response.user:
            raise ValueError("No user returned from Supabase.")
        return response.user.id, response.user.email or ""
    except Exception as exc:
        logger.debug("Supabase JWT validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Main dependency
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session),
) -> CurrentUser:
    """
    Extract and validate the Supabase JWT from the Authorization header.

    Steps:
      1. Try local HS256 decode (fast path — requires SUPABASE_JWT_SECRET).
      2. Fall back to Supabase Auth API call.
      3. Look up the user in the local DB (for org_id and role).
    """
    token = credentials.credentials
    user_id: Optional[str] = None
    email: Optional[str] = None

    # --- Fast path: local decode ---
    from app.config import settings  # lazy import avoids circular deps

    if settings.SUPABASE_JWT_SECRET:
        payload = _decode_jwt_local(token)
        if payload:
            user_id = payload.get("sub")
            email = payload.get("email")
    else:
        # --- Slow path: Supabase API ---
        user_id, email = _decode_jwt_supabase(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- Look up user in local DB ---
    user = db.query(User).filter(User.id == user_id).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please register via POST /api/v1/auth/register.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no organization assigned. Contact your administrator.",
        )

    return CurrentUser(
        id=user.id,
        email=user.email,
        org_id=user.org_id,
        role=user.role,
    )


# ---------------------------------------------------------------------------
# Admin guard
# ---------------------------------------------------------------------------

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency that enforces admin role. Use alongside get_current_user."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user
