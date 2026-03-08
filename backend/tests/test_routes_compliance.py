"""
Tests for /api/v1/compliance-checks endpoints.
Covers: CRUD, status transitions, filtering, compliance summary.
RAG/LLM path is always disabled (use_rag=false) to avoid external calls.
"""

import uuid
import pytest

BASE = "/api/v1/compliance-checks"
SUMMARY = "/api/v1/compliance-summary"


# ---------------------------------------------------------------------------
# Helper: build a valid manual compliance check payload
# ---------------------------------------------------------------------------

def _check_payload(org_id, ai_system_id, regulation_id, **kwargs):
    defaults = dict(
        ai_system_id=ai_system_id,
        regulation_id=regulation_id,
        status="pending",
        priority="medium",
        org_id=org_id,
    )
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

class TestCreateComplianceCheck:
    def test_create_manual_check(self, client, org_id, sample_ai_system, sample_regulation):
        payload = _check_payload(org_id, sample_ai_system.id, sample_regulation.id)
        r = client.post(BASE, json=payload, params={"use_rag": "false"})
        assert r.status_code == 201
        data = r.json()
        assert data["status"] == "pending"
        assert data["priority"] == "medium"
        assert data["ai_system_id"] == sample_ai_system.id
        assert data["regulation_id"] == sample_regulation.id
        assert data["org_id"] == org_id

    def test_create_with_gap_description(self, client, org_id, sample_ai_system, sample_regulation):
        payload = _check_payload(
            org_id, sample_ai_system.id, sample_regulation.id,
            gap_description="Missing human oversight documentation",
            remediation_steps="1. Add oversight policy\n2. Train staff",
            priority="high",
        )
        r = client.post(BASE, json=payload, params={"use_rag": "false"})
        assert r.status_code == 201
        data = r.json()
        assert data["gap_description"] == "Missing human oversight documentation"
        assert data["priority"] == "high"

    def test_create_all_valid_statuses(self, client, org_id, sample_ai_system, sample_regulation):
        for status in ("compliant", "non_compliant", "partial", "pending"):
            payload = _check_payload(
                org_id, sample_ai_system.id, sample_regulation.id, status=status
            )
            r = client.post(BASE, json=payload, params={"use_rag": "false"})
            assert r.status_code == 201
            assert r.json()["status"] == status

    def test_create_all_valid_priorities(self, client, org_id, sample_ai_system, sample_regulation):
        for priority in ("critical", "high", "medium", "low"):
            payload = _check_payload(
                org_id, sample_ai_system.id, sample_regulation.id, priority=priority
            )
            r = client.post(BASE, json=payload, params={"use_rag": "false"})
            assert r.status_code == 201
            assert r.json()["priority"] == priority

    def test_create_missing_org_id_returns_422(self, client, sample_ai_system, sample_regulation):
        payload = {
            "ai_system_id": sample_ai_system.id,
            "regulation_id": sample_regulation.id,
        }
        r = client.post(BASE, json=payload, params={"use_rag": "false"})
        assert r.status_code == 422

    def test_create_missing_ai_system_id_returns_422(self, client, org_id, sample_regulation):
        payload = {"regulation_id": sample_regulation.id, "org_id": org_id}
        r = client.post(BASE, json=payload, params={"use_rag": "false"})
        assert r.status_code == 422

    def test_create_invalid_status_returns_422(self, client, org_id, sample_ai_system, sample_regulation):
        payload = _check_payload(
            org_id, sample_ai_system.id, sample_regulation.id, status="unknown_status"
        )
        r = client.post(BASE, json=payload, params={"use_rag": "false"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# READ (single)
# ---------------------------------------------------------------------------

class TestGetComplianceCheck:
    def test_get_existing(self, client, sample_compliance_check):
        r = client.get(f"{BASE}/{sample_compliance_check.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sample_compliance_check.id

    def test_get_nonexistent_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# LIST + FILTERING
# ---------------------------------------------------------------------------

class TestListComplianceChecks:
    def test_list_by_org(self, client, org_id, sample_compliance_check):
        r = client.get(BASE, params={"org_id": org_id})
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert all(c["org_id"] == org_id for c in data)

    def test_list_filter_by_ai_system(self, client, org_id, sample_ai_system, sample_regulation, db):
        from app.store.models import ComplianceCheck
        # Create two checks for different systems
        other_system_id = str(uuid.uuid4())
        check_other = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=other_system_id,
            regulation_id=sample_regulation.id,
            status="pending",
            priority="low",
            org_id=org_id,
        )
        db.add(check_other)
        db.commit()
        # Create check for our system
        payload = _check_payload(org_id, sample_ai_system.id, sample_regulation.id)
        client.post(BASE, json=payload, params={"use_rag": "false"})

        r = client.get(BASE, params={"org_id": org_id, "ai_system_id": sample_ai_system.id})
        assert r.status_code == 200
        data = r.json()
        assert all(c["ai_system_id"] == sample_ai_system.id for c in data)

    def test_list_filter_by_status(self, client, org_id, sample_ai_system, sample_regulation):
        for status in ("compliant", "non_compliant"):
            payload = _check_payload(
                org_id, sample_ai_system.id, sample_regulation.id, status=status
            )
            client.post(BASE, json=payload, params={"use_rag": "false"})

        r = client.get(BASE, params={"org_id": org_id, "status": "compliant"})
        assert r.status_code == 200
        data = r.json()
        assert all(c["status"] == "compliant" for c in data)

    def test_list_filter_by_priority(self, client, org_id, sample_ai_system, sample_regulation):
        payload = _check_payload(
            org_id, sample_ai_system.id, sample_regulation.id, priority="critical"
        )
        client.post(BASE, json=payload, params={"use_rag": "false"})

        r = client.get(BASE, params={"org_id": org_id, "priority": "critical"})
        assert r.status_code == 200
        data = r.json()
        assert all(c["priority"] == "critical" for c in data)

    def test_list_requires_org_id(self, client):
        r = client.get(BASE)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# UPDATE (PATCH) — Status Transitions
# ---------------------------------------------------------------------------

class TestUpdateComplianceCheck:
    def test_status_transition_pending_to_compliant(self, client, sample_compliance_check):
        r = client.patch(f"{BASE}/{sample_compliance_check.id}", json={"status": "compliant"})
        assert r.status_code == 200
        assert r.json()["status"] == "compliant"

    def test_status_transition_to_non_compliant(self, client, sample_compliance_check):
        r = client.patch(f"{BASE}/{sample_compliance_check.id}", json={"status": "non_compliant"})
        assert r.status_code == 200
        assert r.json()["status"] == "non_compliant"

    def test_status_transition_to_partial(self, client, sample_compliance_check):
        r = client.patch(f"{BASE}/{sample_compliance_check.id}", json={"status": "partial"})
        assert r.status_code == 200
        assert r.json()["status"] == "partial"

    def test_update_priority(self, client, sample_compliance_check):
        r = client.patch(f"{BASE}/{sample_compliance_check.id}", json={"priority": "critical"})
        assert r.status_code == 200
        assert r.json()["priority"] == "critical"

    def test_update_gap_description(self, client, sample_compliance_check):
        r = client.patch(
            f"{BASE}/{sample_compliance_check.id}",
            json={"gap_description": "New gap found", "remediation_steps": "Fix it"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["gap_description"] == "New gap found"
        assert data["remediation_steps"] == "Fix it"

    def test_update_nonexistent_returns_404(self, client):
        r = client.patch(f"{BASE}/{uuid.uuid4()}", json={"status": "compliant"})
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

class TestDeleteComplianceCheck:
    def test_delete_existing(self, client, sample_compliance_check):
        r = client.delete(f"{BASE}/{sample_compliance_check.id}")
        assert r.status_code == 204

    def test_delete_then_get_404(self, client, sample_compliance_check):
        client.delete(f"{BASE}/{sample_compliance_check.id}")
        r = client.get(f"{BASE}/{sample_compliance_check.id}")
        assert r.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# COMPLIANCE SUMMARY
# ---------------------------------------------------------------------------

class TestComplianceSummary:
    def test_summary_empty_org(self, client, org_id_b):
        r = client.get(SUMMARY, params={"org_id": org_id_b})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["by_status"] == {}
        assert data["by_priority"] == {}

    def test_summary_with_checks(self, client, org_id, sample_ai_system, sample_regulation):
        for status, priority in [
            ("compliant", "low"),
            ("non_compliant", "critical"),
            ("partial", "high"),
            ("pending", "medium"),
        ]:
            payload = _check_payload(
                org_id, sample_ai_system.id, sample_regulation.id,
                status=status, priority=priority
            )
            client.post(BASE, json=payload, params={"use_rag": "false"})

        r = client.get(SUMMARY, params={"org_id": org_id})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 4
        assert data["by_status"]["compliant"] == 1
        assert data["by_status"]["non_compliant"] == 1
        assert data["by_status"]["partial"] == 1
        assert data["by_status"]["pending"] == 1
        assert data["by_priority"]["critical"] == 1
        assert data["by_priority"]["low"] == 1

    def test_summary_requires_org_id(self, client):
        r = client.get(SUMMARY)
        assert r.status_code == 422
