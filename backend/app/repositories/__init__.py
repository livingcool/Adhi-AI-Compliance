"""
Repository layer for Adhi Compliance.

Provides generic CRUD and domain-specific query methods for all ORM models,
enforcing org_id scoping throughout.
"""

from app.repositories.base import BaseRepository
from app.repositories.ai_system_repo import AISystemRepository
from app.repositories.regulation_repo import RegulationRepository
from app.repositories.compliance_repo import ComplianceRepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.bias_audit_repo import BiasAuditRepository
from app.repositories.model_card_repo import ModelCardRepository
from app.repositories.user_repo import UserRepository

__all__ = [
    "BaseRepository",
    "AISystemRepository",
    "RegulationRepository",
    "ComplianceRepository",
    "IncidentRepository",
    "BiasAuditRepository",
    "ModelCardRepository",
    "UserRepository",
]
