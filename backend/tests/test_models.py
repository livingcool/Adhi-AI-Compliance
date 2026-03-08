"""
Tests for SQLAlchemy model creation, relationships, enums, UUID generation,
and timestamp auto-population.
"""

import uuid
import pytest
from datetime import datetime

from app.store.models import (
    User, AISystem, Regulation, ComplianceCheck,
    BiasAudit, Incident, ModelCard, TaskRecord,
)
from app.store.metadata_store import Organization, ServiceProvider


# ---------------------------------------------------------------------------
# ServiceProvider model
# ---------------------------------------------------------------------------

class TestServiceProviderModel:
    def test_create_service_provider(self, db):
        provider = ServiceProvider(
            id=str(uuid.uuid4()),
            business_name="Acme AI Corp",
            admin_email="admin@acme.ai",
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)

        assert provider.id is not None
        assert provider.business_name == "Acme AI Corp"
        assert provider.admin_email == "admin@acme.ai"
        assert isinstance(provider.created_at, datetime)

    def test_uuid_generation(self, db):
        p1 = ServiceProvider(
            id=str(uuid.uuid4()),
            business_name="P1",
            admin_email="p1@test.com",
        )
        p2 = ServiceProvider(
            id=str(uuid.uuid4()),
            business_name="P2",
            admin_email="p2@test.com",
        )
        db.add_all([p1, p2])
        db.commit()
        assert p1.id != p2.id


# ---------------------------------------------------------------------------
# Organization model
# ---------------------------------------------------------------------------

class TestOrganizationModel:
    def test_create_organization(self, db, service_provider):
        org = Organization(
            id=str(uuid.uuid4()),
            service_provider_id=service_provider.id,
            name="Test Org",
            slug="test-org-unique",
        )
        db.add(org)
        db.commit()
        db.refresh(org)

        assert org.id is not None
        assert org.name == "Test Org"
        assert org.slug == "test-org-unique"
        assert org.service_provider_id == service_provider.id
        assert isinstance(org.created_at, datetime)


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------

class TestUserModel:
    def test_create_user_defaults(self, db, org_id):
        user = User(
            id=str(uuid.uuid4()),
            email="new@example.com",
            name="New User",
            org_id=org_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.role == "member"  # default
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_roles(self, db, org_id):
        for role in ("admin", "member", "viewer"):
            user = User(
                id=str(uuid.uuid4()),
                email=f"{role}@example.com",
                name=role.capitalize(),
                role=role,
                org_id=org_id,
            )
            db.add(user)
        db.commit()

        users = db.query(User).filter(User.org_id == org_id).all()
        roles = {u.role for u in users}
        assert roles == {"admin", "member", "viewer"}

    def test_user_uuid_is_string(self, db, org_id):
        user = User(
            id=str(uuid.uuid4()),
            email="uuid@example.com",
            name="UUID Test",
            org_id=org_id,
        )
        db.add(user)
        db.commit()
        assert isinstance(user.id, str)


# ---------------------------------------------------------------------------
# AISystem model
# ---------------------------------------------------------------------------

class TestAISystemModel:
    def test_create_ai_system_defaults(self, db, org_id):
        system = AISystem(
            id=str(uuid.uuid4()),
            name="My AI",
            org_id=org_id,
        )
        db.add(system)
        db.commit()
        db.refresh(system)

        assert system.risk_classification == "unclassified"
        assert system.is_high_risk is False
        assert system.compliance_score is None
        assert system.data_types == [] or system.data_types is None or isinstance(system.data_types, list)

    def test_ai_system_risk_classifications(self, db, org_id):
        for tier in ("unacceptable", "high", "limited", "minimal", "unclassified"):
            system = AISystem(
                id=str(uuid.uuid4()),
                name=f"System {tier}",
                risk_classification=tier,
                org_id=org_id,
            )
            db.add(system)
        db.commit()

        systems = db.query(AISystem).filter(AISystem.org_id == org_id).all()
        tiers = {s.risk_classification for s in systems}
        assert tiers == {"unacceptable", "high", "limited", "minimal", "unclassified"}

    def test_ai_system_json_fields(self, db, org_id):
        system = AISystem(
            id=str(uuid.uuid4()),
            name="JSON System",
            data_types=["PII", "biometric", "health"],
            deployment_regions=["EU", "US", "IN"],
            org_id=org_id,
        )
        db.add(system)
        db.commit()
        db.refresh(system)

        assert "PII" in system.data_types
        assert "EU" in system.deployment_regions

    def test_ai_system_timestamps(self, db, org_id):
        system = AISystem(
            id=str(uuid.uuid4()),
            name="Timestamp Test",
            org_id=org_id,
        )
        db.add(system)
        db.commit()
        db.refresh(system)

        assert isinstance(system.created_at, datetime)
        assert isinstance(system.updated_at, datetime)


# ---------------------------------------------------------------------------
# Regulation model
# ---------------------------------------------------------------------------

class TestRegulationModel:
    def test_create_regulation(self, db):
        reg = Regulation(
            id=str(uuid.uuid4()),
            name="EU Artificial Intelligence Act",
            short_name="EU AI Act",
            jurisdiction="EU",
            category="AI Governance",
            url="https://example.com",
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        assert reg.id is not None
        assert reg.jurisdiction == "EU"
        assert isinstance(reg.created_at, datetime)

    def test_regulation_optional_fields(self, db):
        reg = Regulation(
            id=str(uuid.uuid4()),
            name="Minimal Regulation",
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        assert reg.short_name is None
        assert reg.jurisdiction is None
        assert reg.full_text is None
        assert reg.url is None


# ---------------------------------------------------------------------------
# ComplianceCheck model
# ---------------------------------------------------------------------------

class TestComplianceCheckModel:
    def test_create_compliance_check_defaults(self, db, org_id, sample_ai_system, sample_regulation):
        check = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            org_id=org_id,
        )
        db.add(check)
        db.commit()
        db.refresh(check)

        assert check.status == "pending"
        assert check.priority == "medium"
        assert isinstance(check.checked_at, datetime)

    def test_compliance_check_statuses(self, db, org_id, sample_ai_system, sample_regulation):
        for status in ("compliant", "non_compliant", "partial", "pending"):
            check = ComplianceCheck(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                regulation_id=sample_regulation.id,
                status=status,
                org_id=org_id,
            )
            db.add(check)
        db.commit()

        checks = db.query(ComplianceCheck).filter(ComplianceCheck.org_id == org_id).all()
        statuses = {c.status for c in checks}
        assert statuses == {"compliant", "non_compliant", "partial", "pending"}

    def test_compliance_check_priorities(self, db, org_id, sample_ai_system, sample_regulation):
        for priority in ("critical", "high", "medium", "low"):
            check = ComplianceCheck(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                regulation_id=sample_regulation.id,
                priority=priority,
                org_id=org_id,
            )
            db.add(check)
        db.commit()

        checks = db.query(ComplianceCheck).filter(ComplianceCheck.org_id == org_id).all()
        priorities = {c.priority for c in checks}
        assert priorities == {"critical", "high", "medium", "low"}


# ---------------------------------------------------------------------------
# BiasAudit model
# ---------------------------------------------------------------------------

class TestBiasAuditModel:
    def test_create_bias_audit_defaults(self, db, org_id, sample_ai_system):
        audit = BiasAudit(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            org_id=org_id,
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        assert audit.overall_status == "conditional"
        assert isinstance(audit.audit_date, datetime)

    def test_bias_audit_statuses(self, db, org_id, sample_ai_system):
        for status in ("pass", "fail", "conditional"):
            audit = BiasAudit(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                overall_status=status,
                org_id=org_id,
            )
            db.add(audit)
        db.commit()

        audits = db.query(BiasAudit).filter(BiasAudit.org_id == org_id).all()
        statuses = {a.overall_status for a in audits}
        assert statuses == {"pass", "fail", "conditional"}

    def test_bias_audit_json_findings(self, db, org_id, sample_ai_system):
        findings = {"gender": "FAIL", "age": "PASS", "score": 0.72}
        audit = BiasAudit(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            findings=findings,
            org_id=org_id,
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        assert audit.findings["gender"] == "FAIL"
        assert audit.findings["score"] == 0.72


# ---------------------------------------------------------------------------
# Incident model
# ---------------------------------------------------------------------------

class TestIncidentModel:
    def test_create_incident_defaults(self, db, org_id, sample_ai_system):
        incident = Incident(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            org_id=org_id,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        assert incident.severity == "medium"
        assert incident.status == "investigating"
        assert isinstance(incident.detected_at, datetime)

    def test_incident_severities(self, db, org_id, sample_ai_system):
        for severity in ("critical", "high", "medium", "low"):
            incident = Incident(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                severity=severity,
                org_id=org_id,
            )
            db.add(incident)
        db.commit()

        incidents = db.query(Incident).filter(Incident.org_id == org_id).all()
        severities = {i.severity for i in incidents}
        assert severities == {"critical", "high", "medium", "low"}

    def test_incident_statuses(self, db, org_id, sample_ai_system):
        for status in ("investigating", "mitigating", "resolved", "closed"):
            incident = Incident(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                status=status,
                org_id=org_id,
            )
            db.add(incident)
        db.commit()

        incidents = db.query(Incident).filter(Incident.org_id == org_id).all()
        statuses = {i.status for i in incidents}
        assert statuses == {"investigating", "mitigating", "resolved", "closed"}

    def test_incident_timeline_json(self, db, org_id, sample_ai_system):
        timeline = [
            {"timestamp": "2024-01-01T00:00:00", "event": "Incident detected"},
            {"timestamp": "2024-01-01T01:00:00", "event": "Team notified"},
        ]
        incident = Incident(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            timeline=timeline,
            org_id=org_id,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        assert len(incident.timeline) == 2
        assert incident.timeline[0]["event"] == "Incident detected"


# ---------------------------------------------------------------------------
# ModelCard model
# ---------------------------------------------------------------------------

class TestModelCardModel:
    def test_create_model_card(self, db, org_id, sample_ai_system):
        card = ModelCard(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            content={"model_name": "Test", "version": "1.0", "limitations": []},
            version="1.0",
            org_id=org_id,
        )
        db.add(card)
        db.commit()
        db.refresh(card)

        assert card.version == "1.0"
        assert card.content["model_name"] == "Test"
        assert isinstance(card.generated_at, datetime)


# ---------------------------------------------------------------------------
# TaskRecord model
# ---------------------------------------------------------------------------

class TestTaskRecordModel:
    def test_create_task_record(self, db):
        task = TaskRecord(
            id=str(uuid.uuid4()),
            status="pending",
            progress_percent=0.0,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        assert task.status == "pending"
        assert task.progress_percent == 0.0
        assert isinstance(task.created_at, datetime)

    def test_task_record_uuid_auto(self, db):
        task = TaskRecord()
        db.add(task)
        db.commit()
        # id default lambda should generate a UUID string
        assert task.id is not None
        # Validate it looks like a UUID
        parsed = uuid.UUID(task.id)
        assert str(parsed) == task.id
