"""
Pagination utilities for Adhi Compliance API.

Usage:
    from app.core.pagination import PaginatedResponse, paginate

    result = paginate(db.query(AISystem).filter(...), skip=0, limit=50)
    return PaginatedResponse[AISystemResponse](**result)
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool

    class Config:
        from_attributes = True


def paginate(query: Query, skip: int = 0, limit: int = 50) -> Dict[str, Any]:
    """
    Apply pagination to any SQLAlchemy query.

    Args:
        query:  An active SQLAlchemy Query (filters already applied).
        skip:   Number of rows to skip (offset).
        limit:  Maximum number of rows to return.

    Returns:
        A dict with keys: items, total, skip, limit, has_more.
        Pass this directly to PaginatedResponse(**result).
    """
    total: int = query.count()
    items: list = query.offset(skip).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }
