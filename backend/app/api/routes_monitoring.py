"""
Monitoring API Routes — protected by require_admin.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.store.models import get_db_session
from app.services.compliance_monitor import compliance_monitor
from app.services.alert_service import VALID_ALERT_TYPES, VALID_CHANNELS, format_alert, send_alert
from app.middleware.auth import CurrentUser, get_current_user, require_admin

router = APIRouter(prefix="/monitoring")


class ScanRequest(BaseModel):
    pass  # org_id always from JWT


class ScanResponse(BaseModel):
    scanned_systems: int
    checks_created: int
    errors: List[Dict[str, Any]]
    scan_timestamp: str


class DeadlineItem(BaseModel):
    check_id: str
    ai_system_id: str
    regulation_id: str
    status: str
    priority: str
    deadline: str
    days_remaining: int
    gap_description: Optional[str]
    org_id: str


class DriftResponse(BaseModel):
    system_id: str
    drift_detected: bool
    drifted_regulations: List[Dict[str, Any]]
    stable_regulations: List[Dict[str, Any]]
    checked_at: str


class TestAlertRequest(BaseModel):
    alert_type: str = "compliance_drift"
    channel: str = "slack"
    recipients: List[str] = []
    message: Optional[str] = None


class TestAlertResponse(BaseModel):
    success: bool
    channel: str
    alert_type: str
    sent_at: str
    formatted_message: str


@router.post("/scan", summary="Trigger full compliance scan", response_model=ScanResponse)
def trigger_scan(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> ScanResponse:
    try:
        result = compliance_monitor.scan_all_systems(db=db, org_id=current_user.org_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Compliance scan failed: {exc}")
    return ScanResponse(
        scanned_systems=result["scanned_systems"],
        checks_created=result["checks_created"],
        errors=result["errors"],
        scan_timestamp=result["scan_timestamp"],
    )


@router.get("/deadlines", summary="Get upcoming compliance deadlines", response_model=List[DeadlineItem])
def get_deadlines(
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> List[DeadlineItem]:
    try:
        items = compliance_monitor.get_upcoming_deadlines(db=db, days=days, org_id=current_user.org_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Deadline query failed: {exc}")
    return [DeadlineItem(**item) for item in items]


@router.get("/drift/{system_id}", summary="Check compliance drift for a system", response_model=DriftResponse)
def check_drift(
    system_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> DriftResponse:
    try:
        result = compliance_monitor.detect_compliance_drift(system_id=system_id, db=db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Drift detection failed: {exc}")
    return DriftResponse(**result)


@router.get("/regulation-updates", summary="Check for regulation updates")
def check_regulation_updates(current_user: CurrentUser = Depends(get_current_user)) -> Dict[str, Any]:
    return compliance_monitor.check_regulation_updates()


@router.post("/alerts/test", summary="Send a test alert", response_model=TestAlertResponse)
def send_test_alert(
    payload: TestAlertRequest,
    current_user: CurrentUser = Depends(require_admin),
) -> TestAlertResponse:
    if payload.alert_type not in VALID_ALERT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid alert_type. Must be one of: {', '.join(VALID_ALERT_TYPES)}")
    if payload.channel not in VALID_CHANNELS:
        raise HTTPException(status_code=400, detail=f"Invalid channel. Must be one of: {', '.join(VALID_CHANNELS)}")
    test_data = {"test": "true", "system": "Test AI System",
                 "message": payload.message or "This is a test alert from Adhi Compliance.",
                 "triggered_by": "manual test"}
    formatted = format_alert(payload.alert_type, test_data)
    message = payload.message or formatted
    result = send_alert(alert_type=payload.alert_type, message=message, channel=payload.channel,
                        recipients=payload.recipients, data=test_data)
    return TestAlertResponse(success=result["success"], channel=result["channel"],
                             alert_type=result["alert_type"], sent_at=result["sent_at"],
                             formatted_message=formatted)
