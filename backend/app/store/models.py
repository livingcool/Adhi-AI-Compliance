"""
Compliance platform SQLAlchemy models.
Imports Base/engine/SessionLocal from metadata_store (same DB, same Base = all tables created together).
"""

from sqlalchemy import (
    Column, String, Float, Text, Boolean, DateTime,
    ForeignKey, Enum as SqlEnum, JSON, Index
)
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Generator
import uuid

# Import shared DB setup from metadata_store.
# NOTE: metadata_store.py imports this module at its bottom to register these
# models with Base before create_all() runs. The circular import is safe because
# Base/engine/SessionLocal are defined at the TOP of metadata_store.py.
from app.store.metadata_store import Base, SessionLocal


# ---------------------------------------------------------------------------
# Dependency for FastAPI routes
# ---------------------------------------------------------------------------

def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(SqlEnum("admin", "member", "viewer", name="user_role_enum"), default="member")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_users_org_id", "org_id"),
    )


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    size = Column(String, nullable=True)            # startup / sme / enterprise
    website = Column(String, nullable=True)
    jurisdictions = Column(JSON, default=list)      # e.g. ["EU", "US", "IN"]
    risk_appetite = Column(String, default="medium")  # low / medium / high
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AISystem(Base):
    __tablename__ = "ai_systems"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    purpose = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    model_provider = Column(String, nullable=True)
    data_types = Column(JSON, default=list)           # ["PII", "biometric", ...]
    deployment_regions = Column(JSON, default=list)   # ["EU", "US", ...]
    risk_classification = Column(
        SqlEnum(
            "unacceptable", "high", "limited", "minimal", "unclassified",
            name="risk_classification_enum"
        ),
        default="unclassified"
    )
    is_high_risk = Column(Boolean, default=False)
    compliance_score = Column(Float, nullable=True)   # 0.0 – 100.0
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Composite index for org + risk tier lookups (dashboard, filtering)
        Index("ix_ai_systems_org_risk", "org_id", "risk_classification"),
    )


class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=True)        # e.g. "EU AI Act"
    jurisdiction = Column(String, nullable=True, index=True)  # e.g. "EU"
    effective_date = Column(DateTime, nullable=True)
    enforcement_date = Column(DateTime, nullable=True)
    full_text = Column(Text, nullable=True)
    category = Column(String, nullable=True)          # e.g. "AI Governance"
    url = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)  # soft delete
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        # Composite index for jurisdiction + category filtering
        Index("ix_regulations_jurisdiction_category", "jurisdiction", "category"),
    )


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_system_id = Column(String, ForeignKey("ai_systems.id"), nullable=False, index=True)
    regulation_id = Column(String, ForeignKey("regulations.id"), nullable=False, index=True)
    status = Column(
        SqlEnum("compliant", "non_compliant", "partial", "pending", name="compliance_status_enum"),
        default="pending"
    )
    gap_description = Column(Text, nullable=True)
    remediation_steps = Column(Text, nullable=True)
    priority = Column(
        SqlEnum("critical", "high", "medium", "low", name="check_priority_enum"),
        default="medium"
    )
    deadline = Column(DateTime, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    __table_args__ = (
        # Composite index: most queries filter by system + org + status together
        Index("ix_compliance_checks_system_org_status", "ai_system_id", "org_id", "status"),
    )


class BiasAudit(Base):
    __tablename__ = "bias_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_system_id = Column(String, ForeignKey("ai_systems.id"), nullable=False, index=True)
    audit_date = Column(DateTime, default=datetime.utcnow)
    dataset_description = Column(Text, nullable=True)
    demographic_parity_score = Column(Float, nullable=True)
    disparate_impact_ratio = Column(Float, nullable=True)
    overall_status = Column(
        SqlEnum("pass", "fail", "conditional", name="audit_status_enum"),
        default="conditional"
    )
    findings = Column(JSON, default=dict)   # arbitrary structured findings
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    __table_args__ = (
        Index("ix_bias_audits_system_org", "ai_system_id", "org_id"),
    )


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_system_id = Column(String, ForeignKey("ai_systems.id"), nullable=False, index=True)
    severity = Column(
        SqlEnum("critical", "high", "medium", "low", name="incident_severity_enum"),
        default="medium"
    )
    incident_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(
        SqlEnum("investigating", "mitigating", "resolved", "closed", name="incident_status_enum"),
        default="investigating"
    )
    timeline = Column(JSON, default=list)    # list of {timestamp, event} dicts
    filing_status = Column(String, nullable=True)
    filing_deadline = Column(DateTime, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    __table_args__ = (
        # Composite index: incident queries always filter org + severity + status
        Index("ix_incidents_org_severity_status", "org_id", "severity", "status"),
    )


class ModelCard(Base):
    __tablename__ = "model_cards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_system_id = Column(String, ForeignKey("ai_systems.id"), nullable=False, index=True)
    content = Column(JSON, default=dict)     # full model card JSON
    version = Column(String, default="1.0")
    generated_at = Column(DateTime, default=datetime.utcnow)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    __table_args__ = (
        Index("ix_model_cards_system_org", "ai_system_id", "org_id"),
    )


class TaskRecord(Base):
    """
    Database-backed task status store.
    Replaces the in-memory TASK_STORE in routes_ingest.py so that task
    status survives process restarts and is visible across all workers.
    """
    __tablename__ = "task_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="pending")   # pending | processing | success | failure | unknown
    details = Column(Text, nullable=True)
    progress_percent = Column(Float, default=0.0)
    artifacts = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    org_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """
    In-app notification records.
    Created by NotificationService and surfaced via GET /notifications.
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    type = Column(String, nullable=True)   # 'compliance' | 'incident' | 'system' | 'alert'
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_notifications_user_org", "user_id", "org_id"),
        Index("ix_notifications_user_read", "user_id", "read"),
    )


class AuditLog(Base):
    """
    Structured audit trail for all create/update/delete operations.
    Written by audit_service.log_action() and kept for compliance reporting.
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)
    action = Column(String, nullable=False)          # 'create' | 'update' | 'delete' | ...
    entity_type = Column(String, nullable=False)     # 'AISystem' | 'ComplianceCheck' | ...
    entity_id = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_logs_org_entity", "org_id", "entity_type"),
        Index("ix_audit_logs_user", "user_id"),
    )
