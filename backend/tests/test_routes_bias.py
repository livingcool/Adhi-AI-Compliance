"""
Tests for /api/v1/bias-audits endpoints.
Covers: CRUD, file upload analysis, audit history, status filtering.
"""

import csv
import io
import uuid
import pytest

BASE = "/api/v1/bias-audits"


def _bias_audit_payload(org_id, ai_system_id, **kwargs):
    defaults = dict(
        ai_system_id=ai_system_id,
        dataset_description="Test dataset",
        demographic_parity_score=0.05,
        disparate_impact_ratio=0.92,
        overall_status="pass",
        findings={},
        org_id=org_id,
    )
    defaults.update(kwargs)
    return defaults


def _make_csv_bytes(rows, fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

class TestCreateBiasAudit:
    def test_create_pass_audit(self, client, org_id, sample_ai_system):
        payload = _bias_audit_payload(org_id, sample_ai_system.id)
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["overall_status"] == "pass"
        assert data["org_id"] == org_id
        assert "id" in data
        assert "audit_date" in data

    def test_create_fail_audit(self, client, org_id, sample_ai_system):
        payload = _bias_audit_payload(
            org_id, sample_ai_system.id,
            overall_status="fail",
            disparate_impact_ratio=0.65,
            demographic_parity_score=0.35,
        )
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        assert r.json()["overall_status"] == "fail"

    def test_create_conditional_audit(self, client, org_id, sample_ai_system):
        payload = _bias_audit_payload(
            org_id, sample_ai_system.id, overall_status="conditional"
        )
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        assert r.json()["overall_status"] == "conditional"

    def test_create_missing_org_id_422(self, client, sample_ai_system):
        r = client.post(BASE, json={"ai_system_id": sample_ai_system.id})
        assert r.status_code == 422

    def test_create_invalid_status_422(self, client, org_id, sample_ai_system):
        payload = _bias_audit_payload(org_id, sample_ai_system.id, overall_status="unknown")
        r = client.post(BASE, json=payload)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

class TestGetBiasAudit:
    def test_get_existing(self, client, sample_bias_audit):
        r = client.get(f"{BASE}/{sample_bias_audit.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sample_bias_audit.id
        assert data["overall_status"] == "fail"

    def test_get_nonexistent_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------

class TestListBiasAudits:
    def test_list_by_org(self, client, org_id, sample_bias_audit):
        r = client.get(BASE, params={"org_id": org_id})
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert all(a["org_id"] == org_id for a in data)

    def test_list_empty_org(self, client, org_id_b):
        r = client.get(BASE, params={"org_id": org_id_b})
        assert r.status_code == 200
        assert r.json() == []

    def test_list_filter_by_overall_status(self, client, org_id, sample_ai_system):
        # Create a pass audit
        client.post(BASE, json=_bias_audit_payload(org_id, sample_ai_system.id, overall_status="pass"))
        client.post(BASE, json=_bias_audit_payload(org_id, sample_ai_system.id, overall_status="fail"))

        r = client.get(BASE, params={"org_id": org_id, "overall_status": "pass"})
        assert r.status_code == 200
        data = r.json()
        assert all(a["overall_status"] == "pass" for a in data)

    def test_list_filter_by_ai_system_id(self, client, org_id, sample_bias_audit):
        r = client.get(
            BASE,
            params={"org_id": org_id, "ai_system_id": sample_bias_audit.ai_system_id},
        )
        assert r.status_code == 200
        data = r.json()
        assert all(a["ai_system_id"] == sample_bias_audit.ai_system_id for a in data)

    def test_list_requires_org_id(self, client):
        r = client.get(BASE)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

class TestUpdateBiasAudit:
    def test_update_status(self, client, sample_bias_audit):
        r = client.patch(f"{BASE}/{sample_bias_audit.id}", json={"overall_status": "conditional"})
        assert r.status_code == 200
        assert r.json()["overall_status"] == "conditional"

    def test_update_scores(self, client, sample_bias_audit):
        r = client.patch(
            f"{BASE}/{sample_bias_audit.id}",
            json={"demographic_parity_score": 0.03, "disparate_impact_ratio": 0.95},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["demographic_parity_score"] == 0.03
        assert data["disparate_impact_ratio"] == 0.95

    def test_update_nonexistent_404(self, client):
        r = client.patch(f"{BASE}/{uuid.uuid4()}", json={"overall_status": "pass"})
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

class TestDeleteBiasAudit:
    def test_delete_existing(self, client, sample_bias_audit):
        r = client.delete(f"{BASE}/{sample_bias_audit.id}")
        assert r.status_code == 204

    def test_delete_then_get_404(self, client, sample_bias_audit):
        client.delete(f"{BASE}/{sample_bias_audit.id}")
        r = client.get(f"{BASE}/{sample_bias_audit.id}")
        assert r.status_code == 404

    def test_delete_nonexistent_404(self, client):
        r = client.delete(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# File Upload + Analysis
# ---------------------------------------------------------------------------

class TestBiasAuditUpload:
    def test_upload_csv_biased_dataset(self, client, org_id, sample_ai_system):
        """Biased CSV dataset should create a FAIL audit."""
        rows = []
        for _ in range(90):
            rows.append({"gender": "male", "outcome": "1"})
        for _ in range(10):
            rows.append({"gender": "male", "outcome": "0"})
        for _ in range(20):
            rows.append({"gender": "female", "outcome": "1"})
        for _ in range(80):
            rows.append({"gender": "female", "outcome": "0"})
        csv_bytes = _make_csv_bytes(rows)

        r = client.post(
            f"{BASE}/upload",
            data={"ai_system_id": sample_ai_system.id, "org_id": org_id},
            files={"file": ("dataset.csv", csv_bytes, "text/csv")},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["overall_status"] == "fail"
        assert data["disparate_impact_ratio"] < 0.8

    def test_upload_csv_balanced_dataset(self, client, org_id, sample_ai_system):
        """Balanced dataset should create a PASS audit."""
        rows = []
        for gender in ("male", "female"):
            for _ in range(50):
                rows.append({"gender": gender, "outcome": "1"})
            for _ in range(50):
                rows.append({"gender": gender, "outcome": "0"})
        csv_bytes = _make_csv_bytes(rows)

        r = client.post(
            f"{BASE}/upload",
            data={"ai_system_id": sample_ai_system.id, "org_id": org_id},
            files={"file": ("balanced.csv", csv_bytes, "text/csv")},
        )
        assert r.status_code == 201
        assert r.json()["overall_status"] == "pass"

    def test_upload_with_dataset_description(self, client, org_id, sample_ai_system):
        rows = [{"gender": "male", "outcome": "1"}, {"gender": "female", "outcome": "1"}]
        csv_bytes = _make_csv_bytes(rows)
        r = client.post(
            f"{BASE}/upload",
            data={
                "ai_system_id": sample_ai_system.id,
                "org_id": org_id,
                "dataset_description": "Hiring Dataset Q2 2024",
            },
            files={"file": ("test.csv", csv_bytes, "text/csv")},
        )
        assert r.status_code == 201
        assert r.json()["dataset_description"] == "Hiring Dataset Q2 2024"

    def test_upload_with_explicit_protected_attributes(self, client, org_id, sample_ai_system):
        rows = [
            {"custom_attr": "A", "outcome": "1"},
            {"custom_attr": "B", "outcome": "0"},
        ]
        csv_bytes = _make_csv_bytes(rows)
        r = client.post(
            f"{BASE}/upload",
            data={
                "ai_system_id": sample_ai_system.id,
                "org_id": org_id,
                "protected_attributes": "custom_attr",
            },
            files={"file": ("test.csv", csv_bytes, "text/csv")},
        )
        assert r.status_code == 201


# ---------------------------------------------------------------------------
# Audit history for a system
# ---------------------------------------------------------------------------

class TestAuditHistory:
    def test_audit_history_for_system(self, client, org_id, sample_ai_system):
        # Create two audits
        for status in ("pass", "fail"):
            client.post(BASE, json=_bias_audit_payload(org_id, sample_ai_system.id, overall_status=status))

        r = client.get(
            f"{BASE}/{sample_ai_system.id}/history",
            params={"org_id": org_id},
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 2

    def test_audit_history_respects_limit(self, client, org_id, sample_ai_system):
        for _ in range(5):
            client.post(BASE, json=_bias_audit_payload(org_id, sample_ai_system.id))

        r = client.get(
            f"{BASE}/{sample_ai_system.id}/history",
            params={"org_id": org_id, "limit": 3},
        )
        assert r.status_code == 200
        assert len(r.json()) <= 3

    def test_audit_history_empty_for_unknown_system(self, client, org_id):
        r = client.get(
            f"{BASE}/{uuid.uuid4()}/history",
            params={"org_id": org_id},
        )
        assert r.status_code == 200
        assert r.json() == []
