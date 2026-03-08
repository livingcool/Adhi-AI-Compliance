"""
Task Status Routes.

Endpoints for polling Celery background-task status and retrieving results.
All compliance-heavy operations (compliance checks, reports, bias audits, scans,
model cards) return a task_id immediately; clients poll these endpoints.
"""

from typing import Any, Optional

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.workers.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str         # PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED
    ready: bool
    successful: Optional[bool] = None


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}/status
# ---------------------------------------------------------------------------

@router.get("/{task_id}/status", response_model=TaskStatusResponse)
def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Check the current status of a background Celery task.

    Possible statuses:
    - PENDING  — task not yet received by a worker
    - STARTED  — task is running
    - SUCCESS  — task completed successfully
    - FAILURE  — task failed (call /result for the error)
    - RETRY    — task is being retried
    - REVOKED  — task was cancelled
    """
    result: AsyncResult = celery_app.AsyncResult(task_id)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        ready=result.ready(),
        successful=result.successful() if result.ready() else None,
    )


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}/result
# ---------------------------------------------------------------------------

@router.get("/{task_id}/result", response_model=TaskResultResponse)
def get_task_result(task_id: str) -> TaskResultResponse:
    """
    Retrieve the result payload of a completed Celery task.

    Returns the task output on success, or the error string on failure.
    Returns status with null result if the task is still running.
    """
    result: AsyncResult = celery_app.AsyncResult(task_id)

    if not result.ready():
        return TaskResultResponse(task_id=task_id, status=result.status)

    if result.successful():
        return TaskResultResponse(
            task_id=task_id,
            status=result.status,
            result=result.result,
        )

    # Task failed — surface the error
    error_str = str(result.result) if result.result else "Unknown error"
    return TaskResultResponse(
        task_id=task_id,
        status=result.status,
        error=error_str,
    )
