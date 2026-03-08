"""
Reports API Routes — org_id always derived from JWT.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.store.models import get_db_session
from app.services.report_generator import (
    generate_compliance_report, generate_executive_summary,
    generate_gap_analysis_csv, html_to_pdf,
)
from app.middleware.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/reports")


class ScheduleReportRequest(BaseModel):
    report_type: str = "compliance"
    frequency: str = "weekly"
    recipients: List[str] = []
    delivery_channel: str = "email"
    org_name: Optional[str] = None


class ScheduleReportResponse(BaseModel):
    schedule_id: str
    org_id: str
    report_type: str
    frequency: str
    recipients: List[str]
    delivery_channel: str
    next_run: str
    status: str


@router.get("/compliance", summary="Generate compliance audit PDF")
def get_compliance_report(
    format: str = Query("pdf"),
    org_name: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Response:
    org_id = current_user.org_id
    try:
        html = generate_compliance_report(org_id=org_id, db=db, org_name=org_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")
    if format.lower() == "html":
        return HTMLResponse(content=html, status_code=200)
    try:
        pdf_bytes = html_to_pdf(html)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {exc}")
    filename = f"compliance_report_{org_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/gap-analysis", summary="Generate gap analysis CSV")
def get_gap_analysis(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Response:
    org_id = current_user.org_id
    try:
        csv_bytes = generate_gap_analysis_csv(org_id=org_id, db=db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gap analysis generation failed: {exc}")
    filename = f"gap_analysis_{org_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return Response(content=csv_bytes, media_type="text/csv; charset=utf-8-sig",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/executive-summary", summary="Generate executive summary")
def get_executive_summary(
    format: str = Query("html"),
    org_name: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Response:
    org_id = current_user.org_id
    try:
        html = generate_executive_summary(org_id=org_id, db=db, org_name=org_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Executive summary generation failed: {exc}")
    if format.lower() == "pdf":
        try:
            pdf_bytes = html_to_pdf(html)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"PDF conversion failed: {exc}")
        filename = f"executive_summary_{org_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    return HTMLResponse(content=html, status_code=200)


@router.post("/schedule", summary="Schedule recurring reports", response_model=ScheduleReportResponse)
def schedule_report(
    payload: ScheduleReportRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ScheduleReportResponse:
    valid_types = {"compliance", "gap_analysis", "executive_summary"}
    valid_frequencies = {"daily", "weekly", "monthly"}
    valid_channels = {"email", "slack", "teams"}
    if payload.report_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid report_type.")
    if payload.frequency not in valid_frequencies:
        raise HTTPException(status_code=400, detail=f"Invalid frequency.")
    if payload.delivery_channel not in valid_channels:
        raise HTTPException(status_code=400, detail=f"Invalid delivery_channel.")
    from datetime import timedelta
    freq_delta = {"daily": 1, "weekly": 7, "monthly": 30}
    next_run = datetime.utcnow() + timedelta(days=freq_delta[payload.frequency])
    return ScheduleReportResponse(
        schedule_id=str(uuid.uuid4()), org_id=current_user.org_id,
        report_type=payload.report_type, frequency=payload.frequency,
        recipients=payload.recipients, delivery_channel=payload.delivery_channel,
        next_run=next_run.isoformat(), status="scheduled",
    )
