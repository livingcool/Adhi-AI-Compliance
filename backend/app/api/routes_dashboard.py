from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.store.models import AISystem, Incident, ComplianceCheck, get_db_session
from app.middleware.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    org_id = current_user.org_id
    total_systems = db.query(func.count(AISystem.id)).filter(AISystem.org_id == org_id).scalar()
    compliant_count = (
        db.query(func.count(AISystem.id))
        .filter(AISystem.org_id == org_id, AISystem.compliance_score >= 70)
        .scalar()
    )
    incidents_open = (
        db.query(func.count(Incident.id))
        .filter(Incident.org_id == org_id, Incident.status.in_(["investigating", "mitigating"]))
        .scalar()
    )
    cutoff = datetime.utcnow() + timedelta(days=30)
    upcoming_deadlines_count = (
        db.query(func.count(ComplianceCheck.id))
        .filter(
            ComplianceCheck.org_id == org_id,
            ComplianceCheck.deadline != None,
            ComplianceCheck.deadline <= cutoff,
            ComplianceCheck.status != "compliant",
        )
        .scalar()
    )
    overall_score = round((compliant_count / max(total_systems, 1)) * 100) if total_systems else 0
    return {
        # camelCase keys match the frontend DashboardStats interface
        "totalSystems": total_systems or 0,
        "compliantSystems": compliant_count or 0,
        "openIncidents": incidents_open or 0,
        "upcomingDeadlines": upcoming_deadlines_count or 0,
        "overallScore": overall_score,
        "complianceByCategory": [],
    }


@router.get("/dashboard/risk-distribution")
def get_risk_distribution(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    org_id = current_user.org_id
    rows = (
        db.query(AISystem.risk_classification, func.count(AISystem.id))
        .filter(AISystem.org_id == org_id)
        .group_by(AISystem.risk_classification)
        .all()
    )
    # Map backend tier names → frontend display names + colors
    TIER_MAP = {
        "unacceptable": {"name": "Critical", "color": "#ef4444"},
        "high":         {"name": "High",     "color": "#f97316"},
        "limited":      {"name": "Medium",   "color": "#eab308"},
        "minimal":      {"name": "Low",      "color": "#22c55e"},
        "unclassified": {"name": "Unknown",  "color": "#6b7280"},
    }
    counts = {tier: 0 for tier in TIER_MAP}
    for risk_tier, count in rows:
        if risk_tier in counts:
            counts[risk_tier] = count
    # Return as list of {name, value, color} — matches RiskDistributionItem[]
    return [
        {"name": meta["name"], "value": counts[tier], "color": meta["color"]}
        for tier, meta in TIER_MAP.items()
        if counts[tier] > 0
    ]


@router.get("/dashboard/recent-activity")
def get_recent_activity(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    org_id = current_user.org_id
    checks = (
        db.query(ComplianceCheck)
        .filter(ComplianceCheck.org_id == org_id)
        .order_by(ComplianceCheck.checked_at.desc())
        .limit(10)
        .all()
    )
    incidents = (
        db.query(Incident)
        .filter(Incident.org_id == org_id)
        .order_by(Incident.detected_at.desc())
        .limit(10)
        .all()
    )
    STATUS_TYPE = {"compliant": "success", "non_compliant": "error", "partial": "warning"}
    SEVERITY_TYPE = {"critical": "error", "high": "warning", "medium": "info", "low": "info"}

    activity: list = []
    for c in checks:
        ts = c.checked_at.isoformat() if c.checked_at else ""
        activity.append({
            "id": c.id,
            "type": STATUS_TYPE.get(c.status, "info"),
            "event": f"Compliance check — {c.status.replace('_', ' ').title()} (priority: {c.priority})",
            "system": c.ai_system_id,
            "time": ts,
            "_sort": ts,
        })
    for i in incidents:
        ts = i.detected_at.isoformat() if i.detected_at else ""
        activity.append({
            "id": i.id,
            "type": SEVERITY_TYPE.get(i.severity, "info"),
            "event": f"Incident — {i.incident_type or 'unknown'} ({i.severity})",
            "system": i.ai_system_id,
            "time": ts,
            "_sort": ts,
        })
    activity.sort(key=lambda x: x["_sort"] or "", reverse=True)
    # Strip internal sort key before returning
    return [
        {k: v for k, v in item.items() if k != "_sort"}
        for item in activity[:10]
    ]
