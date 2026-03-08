"""
Tests for /api/v1/ai-systems CRUD endpoints.
Covers: create, read, list, update, delete, pagination, filtering, validation.
"""

import uuid
import pytest


BASE = "/api/v1/ai-systems"


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

class TestCreateAISystem:
    def test_create_minimal(self, client, org_id):
        payload = {"name": "My AI", "org_id": org_id}
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "My AI"
        assert data["org_id"] == org_id
        assert data["risk_classification"] == "unclassified"
        assert data["is_high_risk"] is False
        assert "id" in data

    def test_create_full(self, client, org_id):
        payload = {
            "name": "Hiring AI",
            "purpose": "Recruitment screening",
            "description": "Screens job applications using ML",
            "model_provider": "OpenAI",
            "data_types": ["PII", "employment"],
            "deployment_regions": ["EU", "US"],
            "risk_classification": "high",
            "is_high_risk": True,
            "compliance_score": 45.0,
            "org_id": org_id,
        }
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["risk_classification"] == "high"
        assert data["is_high_risk"] is True
        assert data["compliance_score"] == 45.0
        assert "PII" in data["data_types"]

    def test_create_missing_name_returns_422(self, client, org_id):
        r = client.post(BASE, json={"org_id": org_id})
        assert r.status_code == 422

    def test_create_missing_org_id_returns_422(self, client):
        r = client.post(BASE, json={"name": "No Org System"})
        assert r.status_code == 422

    def test_create_invalid_risk_classification_returns_422(self, client, org_id):
        r = client.post(BASE, json={"name": "Bad", "org_id": org_id, "risk_classification": "super_dangerous"})
        assert r.status_code == 422

    def test_create_returns_timestamps(self, client, org_id):
        r = client.post(BASE, json={"name": "TS Test", "org_id": org_id})
        assert r.status_code == 201
        data = r.json()
        assert "created_at" in data
        assert "updated_at" in data


# ---------------------------------------------------------------------------
# READ (single)
# ---------------------------------------------------------------------------

class TestGetAISystem:
    def test_get_existing(self, client, sample_ai_system):
        r = client.get(f"{BASE}/{sample_ai_system.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sample_ai_system.id
        assert data["name"] == sample_ai_system.name

    def test_get_nonexistent_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_invalid_id_format(self, client):
        r = client.get(f"{BASE}/not-a-real-id")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------

class TestListAISystems:
    def test_list_by_org(self, client, org_id, make_ai_system):
        make_ai_system(name="System Alpha")
        make_ai_system(name="System Beta")
        r = client.get(BASE, params={"org_id": org_id})
        assert r.status_code == 200
        systems = r.json()
        assert len(systems) >= 2
        names = [s["name"] for s in systems]
        assert "System Alpha" in names
        assert "System Beta" in names

    def test_list_empty_org(self, client, org_id_b):
        r = client.get(BASE, params={"org_id": org_id_b})
        assert r.status_code == 200
        assert r.json() == []

    def test_list_filter_by_risk_classification(self, client, org_id, make_ai_system):
        make_ai_system(risk_classification="high", is_high_risk=True)
        make_ai_system(risk_classification="minimal")
        make_ai_system(risk_classification="limited")
        r = client.get(BASE, params={"org_id": org_id, "risk_classification": "high"})
        assert r.status_code == 200
        data = r.json()
        assert all(s["risk_classification"] == "high" for s in data)
        assert len(data) >= 1

    def test_list_filter_by_is_high_risk(self, client, org_id, make_ai_system):
        make_ai_system(risk_classification="high", is_high_risk=True)
        make_ai_system(risk_classification="minimal", is_high_risk=False)
        r = client.get(BASE, params={"org_id": org_id, "is_high_risk": "true"})
        assert r.status_code == 200
        data = r.json()
        assert all(s["is_high_risk"] is True for s in data)

    def test_list_requires_org_id(self, client):
        # org_id is a required query param
        r = client.get(BASE)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# UPDATE (PATCH)
# ---------------------------------------------------------------------------

class TestUpdateAISystem:
    def test_patch_name(self, client, sample_ai_system):
        r = client.patch(f"{BASE}/{sample_ai_system.id}", json={"name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Name"

    def test_patch_risk_classification(self, client, sample_ai_system):
        r = client.patch(
            f"{BASE}/{sample_ai_system.id}",
            json={"risk_classification": "high", "is_high_risk": True},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["risk_classification"] == "high"
        assert data["is_high_risk"] is True

    def test_patch_compliance_score(self, client, sample_ai_system):
        r = client.patch(f"{BASE}/{sample_ai_system.id}", json={"compliance_score": 88.5})
        assert r.status_code == 200
        assert r.json()["compliance_score"] == 88.5

    def test_patch_nonexistent_returns_404(self, client):
        r = client.patch(f"{BASE}/{uuid.uuid4()}", json={"name": "Ghost"})
        assert r.status_code == 404

    def test_patch_partial_update_preserves_other_fields(self, client, sample_ai_system):
        original_org = sample_ai_system.org_id
        r = client.patch(f"{BASE}/{sample_ai_system.id}", json={"name": "Partial Update"})
        assert r.status_code == 200
        data = r.json()
        assert data["org_id"] == original_org  # unchanged


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

class TestDeleteAISystem:
    def test_delete_existing(self, client, sample_ai_system):
        r = client.delete(f"{BASE}/{sample_ai_system.id}")
        assert r.status_code == 204

    def test_delete_then_get_returns_404(self, client, sample_ai_system):
        client.delete(f"{BASE}/{sample_ai_system.id}")
        r = client.get(f"{BASE}/{sample_ai_system.id}")
        assert r.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# All valid risk_classification enum values
# ---------------------------------------------------------------------------

class TestRiskClassificationEnum:
    @pytest.mark.parametrize("tier", ["unacceptable", "high", "limited", "minimal", "unclassified"])
    def test_all_risk_tiers_accepted(self, client, org_id, tier):
        r = client.post(BASE, json={"name": f"System {tier}", "org_id": org_id, "risk_classification": tier})
        assert r.status_code == 201
        assert r.json()["risk_classification"] == tier
