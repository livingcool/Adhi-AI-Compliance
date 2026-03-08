"""
Pydantic request/response schemas for the Adhi Compliance platform.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared enums (mirror SQLAlchemy SqlEnum values)
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"


class RiskClassification(str, Enum):
    unacceptable = "unacceptable"
    high = "high"
    limited = "limited"
    minimal = "minimal"
    unclassified = "unclassified"


class ComplianceStatus(str, Enum):
    compliant = "compliant"
    non_compliant = "non_compliant"
    partial = "partial"
    pending = "pending"


class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class AuditStatus(str, Enum):
    pass_ = "pass"
    fail = "fail"
    conditional = "conditional"


class IncidentSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class IncidentStatus(str, Enum):
    investigating = "investigating"
    mitigating = "mitigating"
    resolved = "resolved"
    closed = "closed"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.member
    org_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    org_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    org_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# CompanyProfile
# ---------------------------------------------------------------------------

class CompanyProfileCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    jurisdictions: List[str] = Field(default_factory=list)
    risk_appetite: str = "medium"
    org_id: str


class CompanyProfileUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    jurisdictions: Optional[List[str]] = None
    risk_appetite: Optional[str] = None


class CompanyProfileResponse(BaseModel):
    id: str
    name: str
    industry: Optional[str]
    size: Optional[str]
    website: Optional[str]
    jurisdictions: List[str]
    risk_appetite: str
    org_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# AISystem
# ---------------------------------------------------------------------------

class AISystemCreate(BaseModel):
    name: str
    purpose: Optional[str] = None
    description: Optional[str] = None
    model_provider: Optional[str] = None
    data_types: List[str] = Field(default_factory=list)
    deployment_regions: List[str] = Field(default_factory=list)
    risk_classification: RiskClassification = RiskClassification.unclassified
    is_high_risk: bool = False
    compliance_score: Optional[float] = None
    org_id: str


class AISystemUpdate(BaseModel):
    name: Optional[str] = None
    purpose: Optional[str] = None
    description: Optional[str] = None
    model_provider: Optional[str] = None
    data_types: Optional[List[str]] = None
    deployment_regions: Optional[List[str]] = None
    risk_classification: Optional[RiskClassification] = None
    is_high_risk: Optional[bool] = None
    compliance_score: Optional[float] = None


class AISystemResponse(BaseModel):
    id: str
    name: str
    purpose: Optional[str]
    description: Optional[str]
    model_provider: Optional[str]
    data_types: List[str]
    deployment_regions: List[str]
    risk_classification: RiskClassification
    is_high_risk: bool
    compliance_score: Optional[float]
    org_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Regulation
# ---------------------------------------------------------------------------

class RegulationCreate(BaseModel):
    name: str
    short_name: Optional[str] = None
    jurisdiction: Optional[str] = None
    effective_date: Optional[datetime] = None
    enforcement_date: Optional[datetime] = None
    full_text: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None


class RegulationUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    jurisdiction: Optional[str] = None
    effective_date: Optional[datetime] = None
    enforcement_date: Optional[datetime] = None
    full_text: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None


class RegulationResponse(BaseModel):
    id: str
    name: str
    short_name: Optional[str]
    jurisdiction: Optional[str]
    effective_date: Optional[datetime]
    enforcement_date: Optional[datetime]
    full_text: Optional[str]
    category: Optional[str]
    url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# ComplianceCheck
# ---------------------------------------------------------------------------

class ComplianceCheckCreate(BaseModel):
    ai_system_id: str
    regulation_id: str
    status: ComplianceStatus = ComplianceStatus.pending
    gap_description: Optional[str] = None
    remediation_steps: Optional[str] = None
    priority: Priority = Priority.medium
    deadline: Optional[datetime] = None
    org_id: str


class ComplianceCheckUpdate(BaseModel):
    status: Optional[ComplianceStatus] = None
    gap_description: Optional[str] = None
    remediation_steps: Optional[str] = None
    priority: Optional[Priority] = None
    deadline: Optional[datetime] = None


class ComplianceCheckResponse(BaseModel):
    id: str
    ai_system_id: str
    regulation_id: str
    status: ComplianceStatus
    gap_description: Optional[str]
    remediation_steps: Optional[str]
    priority: Priority
    deadline: Optional[datetime]
    checked_at: datetime
    org_id: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# BiasAudit
# ---------------------------------------------------------------------------

class BiasAuditCreate(BaseModel):
    ai_system_id: str
    dataset_description: Optional[str] = None
    demographic_parity_score: Optional[float] = None
    disparate_impact_ratio: Optional[float] = None
    overall_status: AuditStatus = AuditStatus.conditional
    findings: Dict[str, Any] = Field(default_factory=dict)
    org_id: str


class BiasAuditUpdate(BaseModel):
    dataset_description: Optional[str] = None
    demographic_parity_score: Optional[float] = None
    disparate_impact_ratio: Optional[float] = None
    overall_status: Optional[AuditStatus] = None
    findings: Optional[Dict[str, Any]] = None


class BiasAuditResponse(BaseModel):
    id: str
    ai_system_id: str
    audit_date: datetime
    dataset_description: Optional[str]
    demographic_parity_score: Optional[float]
    disparate_impact_ratio: Optional[float]
    overall_status: AuditStatus
    findings: Dict[str, Any]
    org_id: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Incident
# ---------------------------------------------------------------------------

class IncidentCreate(BaseModel):
    ai_system_id: str
    severity: IncidentSeverity = IncidentSeverity.medium
    incident_type: Optional[str] = None
    description: Optional[str] = None
    status: IncidentStatus = IncidentStatus.investigating
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    filing_status: Optional[str] = None
    filing_deadline: Optional[datetime] = None
    org_id: str


class IncidentUpdate(BaseModel):
    severity: Optional[IncidentSeverity] = None
    incident_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    filing_status: Optional[str] = None
    filing_deadline: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: str
    ai_system_id: str
    severity: IncidentSeverity
    incident_type: Optional[str]
    description: Optional[str]
    detected_at: datetime
    status: IncidentStatus
    timeline: List[Dict[str, Any]]
    filing_status: Optional[str]
    filing_deadline: Optional[datetime]
    org_id: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# ModelCard
# ---------------------------------------------------------------------------

class ModelCardCreate(BaseModel):
    ai_system_id: str
    content: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"
    org_id: str


class ModelCardUpdate(BaseModel):
    content: Optional[Dict[str, Any]] = None
    version: Optional[str] = None


class ModelCardResponse(BaseModel):
    id: str
    ai_system_id: str
    content: Dict[str, Any]
    version: str
    generated_at: datetime
    org_id: str

    class Config:
        from_attributes = True
