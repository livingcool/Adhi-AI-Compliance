"""
Notification API routes.

GET   /notifications           — list current user's notifications (paginated)
PATCH /notifications/{id}/read — mark a single notification as read
PATCH /notifications/read-all  — mark all user notifications as read
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.store.models import get_db_session
from app.middleware.auth import CurrentUser, get_current_user
from app.services.notification_service import NotificationService

router = APIRouter()


def _get_service(db: Session = Depends(get_db_session)) -> NotificationService:
    return NotificationService(db)


# ---------------------------------------------------------------------------
# GET /notifications
# ---------------------------------------------------------------------------

@router.get("/notifications", summary="List notifications for the current user")
def list_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: CurrentUser = Depends(get_current_user),
    svc: NotificationService = Depends(_get_service),
) -> Dict[str, Any]:
    """
    Return paginated in-app notifications for the authenticated user.

    Use `unread_only=true` to filter to unread notifications only.
    """
    items = svc.get_for_user(
        user_id=current_user.id,
        org_id=current_user.org_id,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )
    return {
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "read": n.read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in items
        ],
        "total": len(items),
        "skip": skip,
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# PATCH /notifications/{id}/read
# ---------------------------------------------------------------------------

@router.patch(
    "/notifications/{notification_id}/read",
    summary="Mark a notification as read",
)
def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    svc: NotificationService = Depends(_get_service),
) -> Dict[str, Any]:
    """Mark a single notification as read. Returns the updated record."""
    notif = svc.mark_read(notification_id, current_user.id)
    if not notif:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    return {
        "id": notif.id,
        "read": notif.read,
    }


# ---------------------------------------------------------------------------
# PATCH /notifications/read-all
# ---------------------------------------------------------------------------

@router.patch(
    "/notifications/read-all",
    summary="Mark all notifications as read for the current user",
)
def mark_all_read(
    current_user: CurrentUser = Depends(get_current_user),
    svc: NotificationService = Depends(_get_service),
) -> Dict[str, Any]:
    """Bulk-mark all unread notifications for the authenticated user as read."""
    count = svc.mark_all_read(current_user.id, current_user.org_id)
    return {"marked_read": count}
