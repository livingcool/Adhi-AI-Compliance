"""
Tests for /api/v1/incidents endpoints.
Covers: CRUD, status workflow transitions, timeline append, severity filtering.
"""

import uuid
import pytest
from datetime import datetime

BASE = "/api/v1/incidents"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _incident_payload(org_id, ai_system_id, **kwargs):
    defaults = dict(
        ai_system_id=ai_system_id,
        severity="medium",
        incident_type="data_drift",
        description="Unexpected model output drift detected",
        status="investigating",
        org_id=org_id,
    )
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

class TestCreateIncident:
    def test_create_minimal_incident(self, client, org_id, sample_ai_system):
        payload = _incident_payload(org_id, sample_ai_system.id)
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["severity"] == "medium"
        assert data["status"] == "investigating"
        assert data["org_id"] == org_id
        assert "id" in data
        assert "detected_at" in data

    def test_create_with_all_fields(self, client, org_id, sample_ai_system):
        payload = _incident_payload(
            org_id, sample_ai_system.id,
            severity="critical",
            incident_type="bias_detected",
            description="Critical bias found in outputs",
            status="mitigating",
            filing_status="filed",
            timeline=[{"timestamp": datetime.utcnow().isoformat(), "event": "Opened"}],
        )
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["severity"] == "critical"
        assert data["incident_type"] == "bias_detected"
        assert len(data["timeline"]) == 1

    @pytest.mark.parametrize("severity", ["critical", "high", "medium", "low"])
    def test_create_all_severities(self, client, org_id, sample_ai_system, severity):
        r = client.post(BASE, json=_incident_payload(org_id, sample_ai_system.id, severity=severity))
        assert r.status_code == 201
        assert r.json()["severity"] == severity

    @pytest.mark.parametrize("status", ["investigating", "mitigating", "resolved", "closed"])
    def test_create_all_statuses(self, client, org_id, sample_ai_system, status):
        r = client.post(BASE, json=_incident_payload(org_id, sample_ai_system.id, status=status))
        assert r.status_code == 201
        assert r.json()["status"] == status

    def test_create_missing_org_id_returns_422(self, client, sample_ai_system):
        r = client.post(BASE, json={"ai_system_id": sample_ai_system.id})
        assert r.status_code == 422

    def test_create_invalid_severity_returns_422(self, client, org_id, sample_ai_system):
        r = client.post(
            BASE,
            json=_incident_payload(org_id, sample_ai_system.id, severity="catastrophic"),
        )
        assert r.status_code == 422

    def test_create_invalid_status_returns_422(self, client, org_id, sample_ai_system):
        r = client.post(
            BASE,
            json=_incident_payload(org_id, sample_ai_system.id, status="unknown"),
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# READ (single)
# ---------------------------------------------------------------------------

class TestGetIncident:
    def test_get_existing(self, client, sample_incident):
        r = client.get(f"{BASE}/{sample_incident.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sample_incident.id
        assert data["severity"] == sample_incident.severity

    def test_get_nonexistent_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# LIST + FILTERING
# ---------------------------------------------------------------------------

class TestListIncidents:
    def test_list_by_org(self, client, org_id, sample_incident):
        r = client.get(BASE, params={"org_id": org_id})
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert all(i["org_id"] == org_id for i in data)

    def test_list_empty_org(self, client, org_id_b):
        r = client.get(BASE, params={"org_id": org_id_b})
        assert r.status_code == 200
        assert r.json() == []

    def test_list_filter_by_severity(self, client, org_id, sample_ai_system, make_incident):
        make_incident(severity="critical")
        make_incident(severity="low")
        r = client.get(BASE, params={"org_id": org_id, "severity": "critical"})
        assert r.status_code == 200
        data = r.json()
        assert all(i["severity"] == "critical" for i in data)

    def test_list_filter_by_status(self, client, org_id, sample_ai_system, make_incident):
        make_incident(status="resolved")
        make_incident(status="investigating")
        r = client.get(BASE, params={"org_id": org_id, "status": "resolved"})
        assert r.status_code == 200
        data = r.json()
        assert all(i["status"] == "resolved" for i in data)

    def test_list_filter_by_ai_system_id(self, client, org_id, sample_incident):
        r = client.get(
            BASE,
            params={"org_id": org_id, "ai_system_id": sample_incident.ai_system_id},
        )
        assert r.status_code == 200
        data = r.json()
        assert all(i["ai_system_id"] == sample_incident.ai_system_id for i in data)

    def test_list_ordered_by_detected_at_desc(self, client, org_id, make_incident):
        from datetime import timedelta
        make_incident()
        make_incident()
        r = client.get(BASE, params={"org_id": org_id})
        assert r.status_code == 200
        data = r.json()
        if len(data) >= 2:
            assert data[0]["detected_at"] >= data[1]["detected_at"]

    def test_list_requires_org_id(self, client):
        r = client.get(BASE)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# UPDATE (PATCH) — Status Workflow Transitions
# ---------------------------------------------------------------------------

class TestUpdateIncident:
    def test_status_transition_to_mitigating(self, client, sample_incident):
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"status": "mitigating"})
        assert r.status_code == 200
        assert r.json()["status"] == "mitigating"

    def test_status_transition_to_resolved(self, client, sample_incident):
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"status": "resolved"})
        assert r.status_code == 200
        assert r.json()["status"] == "resolved"

    def test_status_transition_to_closed(self, client, sample_incident):
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"status": "closed"})
        assert r.status_code == 200
        assert r.json()["status"] == "closed"

    def test_severity_escalation(self, client, sample_incident):
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"severity": "critical"})
        assert r.status_code == 200
        assert r.json()["severity"] == "critical"

    def test_update_description(self, client, sample_incident):
        new_desc = "Updated description with more details"
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"description": new_desc})
        assert r.status_code == 200
        assert r.json()["description"] == new_desc

    def test_update_filing_status(self, client, sample_incident):
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"filing_status": "filed"})
        assert r.status_code == 200
        assert r.json()["filing_status"] == "filed"

    def test_update_nonexistent_returns_404(self, client):
        r = client.patch(f"{BASE}/{uuid.uuid4()}", json={"status": "resolved"})
        assert r.status_code == 404

    def test_partial_update_preserves_other_fields(self, client, sample_incident):
        original_severity = sample_incident.severity
        r = client.patch(f"{BASE}/{sample_incident.id}", json={"status": "mitigating"})
        assert r.status_code == 200
        assert r.json()["severity"] == original_severity  # unchanged


# ---------------------------------------------------------------------------
# TIMELINE APPEND
# ---------------------------------------------------------------------------

class TestIncidentTimeline:
    def test_append_timeline_event(self, client, sample_incident):
        event = {"timestamp": datetime.utcnow().isoformat(), "event": "Team notified"}
        r = client.post(f"{BASE}/{sample_incident.id}/timeline", json=event)
        assert r.status_code == 200
        timeline = r.json()["timeline"]
        # Should include the original event + new one
        assert len(timeline) >= 1
        events = [e["event"] for e in timeline]
        assert "Team notified" in events

    def test_append_multiple_timeline_events(self, client, sample_incident):
        events = [
            {"timestamp": "2024-01-01T10:00:00", "event": "Incident confirmed"},
            {"timestamp": "2024-01-01T11:00:00", "event": "Root cause identified"},
            {"timestamp": "2024-01-01T12:00:00", "event": "Fix deployed"},
        ]
        for ev in events:
            client.post(f"{BASE}/{sample_incident.id}/timeline", json=ev)

        r = client.get(f"{BASE}/{sample_incident.id}")
        assert r.status_code == 200
        timeline = r.json()["timeline"]
        event_texts = [e["event"] for e in timeline]
        assert "Root cause identified" in event_texts
        assert "Fix deployed" in event_texts

    def test_append_timeline_nonexistent_incident_returns_404(self, client):
        r = client.post(
            f"{BASE}/{uuid.uuid4()}/timeline",
            json={"timestamp": datetime.utcnow().isoformat(), "event": "Ghost event"},
        )
        assert r.status_code == 404

    def test_timeline_preserves_order(self, client, sample_incident):
        e1 = {"timestamp": "2024-01-01T10:00:00", "event": "First"}
        e2 = {"timestamp": "2024-01-01T11:00:00", "event": "Second"}
        client.post(f"{BASE}/{sample_incident.id}/timeline", json=e1)
        client.post(f"{BASE}/{sample_incident.id}/timeline", json=e2)

        r = client.get(f"{BASE}/{sample_incident.id}")
        timeline = r.json()["timeline"]
        events = [e["event"] for e in timeline]
        # First should appear before Second
        assert events.index("First") < events.index("Second")


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

class TestDeleteIncident:
    def test_delete_existing(self, client, sample_incident):
        r = client.delete(f"{BASE}/{sample_incident.id}")
        assert r.status_code == 204

    def test_delete_then_get_returns_404(self, client, sample_incident):
        client.delete(f"{BASE}/{sample_incident.id}")
        r = client.get(f"{BASE}/{sample_incident.id}")
        assert r.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404
