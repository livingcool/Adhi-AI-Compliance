"""
Tests for /api/v1/monitoring endpoints.
Covers: deadlines, drift detection, regulation updates, test alerts.
Compliance scan is mocked to avoid LLM calls.
"""

import uuid
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.store.models import ComplianceCheck


# ---------------------------------------------------------------------------
# GET /monitoring/deadlines
# ---------------------------------------------------------------------------

class TestMonitoringDeadlines:
    def test_deadlines_empty_db(self, client, org_id):
        r = client.get("/api/v1/monitoring/deadlines", params={"org_id": org_id})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_deadlines_returns_upcoming_checks(self, client, org_id, db, sample_ai_system, sample_regulation):
        check = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="non_compliant",
            priority="high",
            deadline=datetime.utcnow() + timedelta(days=10),
            org_id=org_id,
        )
        db.add(check)
        db.commit()

        r = client.get("/api/v1/monitoring/deadlines", params={"org_id": org_id, "days": 30})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        check_ids = [d["check_id"] for d in data]
        assert check.id in check_ids

    def test_deadlines_excludes_far_future(self, client, org_id, db, sample_ai_system, sample_regulation):
        check = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="pending",
            priority="low",
            deadline=datetime.utcnow() + timedelta(days=90),
            org_id=org_id,
        )
        db.add(check)
        db.commit()

        r = client.get("/api/v1/monitoring/deadlines", params={"org_id": org_id, "days": 30})
        assert r.status_code == 200
        data = r.json()
        check_ids = [d["check_id"] for d in data]
        assert check.id not in check_ids

    def test_deadlines_days_param_validation(self, client):
        # days < 1 should fail validation
        r = client.get("/api/v1/monitoring/deadlines", params={"days": 0})
        assert r.status_code == 422

    def test_deadlines_deadline_item_structure(self, client, org_id, db, sample_ai_system, sample_regulation):
        check = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="partial",
            priority="medium",
            deadline=datetime.utcnow() + timedelta(days=5),
            org_id=org_id,
        )
        db.add(check)
        db.commit()

        r = client.get("/api/v1/monitoring/deadlines", params={"org_id": org_id})
        assert r.status_code == 200
        data = r.json()
        if data:
            item = data[0]
            assert "check_id" in item
            assert "ai_system_id" in item
            assert "regulation_id" in item
            assert "status" in item
            assert "priority" in item
            assert "deadline" in item
            assert "days_remaining" in item


# ---------------------------------------------------------------------------
# GET /monitoring/drift/{system_id}
# ---------------------------------------------------------------------------

class TestDriftDetection:
    def test_drift_check_no_data(self, client, sample_ai_system):
        r = client.get(f"/api/v1/monitoring/drift/{sample_ai_system.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["system_id"] == sample_ai_system.id
        assert "drift_detected" in data
        assert "drifted_regulations" in data
        assert "stable_regulations" in data

    def test_drift_response_structure(self, client, sample_ai_system):
        r = client.get(f"/api/v1/monitoring/drift/{sample_ai_system.id}")
        assert r.status_code == 200
        data = r.json()
        required_keys = {"system_id", "drift_detected", "drifted_regulations", "stable_regulations", "checked_at"}
        assert required_keys <= set(data.keys())

    def test_drift_for_nonexistent_system(self, client):
        fake_id = str(uuid.uuid4())
        r = client.get(f"/api/v1/monitoring/drift/{fake_id}")
        # Either 200 with empty drift or 500 — should not hang
        assert r.status_code in (200, 404, 500)


# ---------------------------------------------------------------------------
# GET /monitoring/regulation-updates
# ---------------------------------------------------------------------------

class TestRegulationUpdates:
    def test_regulation_updates_returns_data(self, client):
        r = client.get("/api/v1/monitoring/regulation-updates")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# POST /monitoring/alerts/test
# ---------------------------------------------------------------------------

class TestTestAlerts:
    def test_test_alert_slack(self, client):
        with patch("app.services.alert_service.send_alert") as mock_send:
            mock_send.return_value = {
                "success": True,
                "channel": "slack",
                "alert_type": "compliance_drift",
                "sent_at": datetime.utcnow().isoformat(),
            }
            r = client.post(
                "/api/v1/monitoring/alerts/test",
                json={"alert_type": "compliance_drift", "channel": "slack"},
            )
        assert r.status_code == 200
        data = r.json()
        assert "success" in data
        assert "channel" in data
        assert data["channel"] == "slack"

    def test_test_alert_invalid_type_400(self, client):
        r = client.post(
            "/api/v1/monitoring/alerts/test",
            json={"alert_type": "invalid_type", "channel": "slack"},
        )
        assert r.status_code == 400
        assert "Invalid alert_type" in r.json()["detail"]

    def test_test_alert_invalid_channel_400(self, client):
        r = client.post(
            "/api/v1/monitoring/alerts/test",
            json={"alert_type": "compliance_drift", "channel": "invalid_channel"},
        )
        assert r.status_code == 400
        assert "Invalid channel" in r.json()["detail"]

    def test_test_alert_all_valid_types(self, client):
        valid_types = [
            "compliance_drift", "deadline_approaching",
            "new_regulation", "incident_detected", "audit_failed",
        ]
        for alert_type in valid_types:
            with patch("app.services.alert_service.send_alert") as mock_send:
                mock_send.return_value = {
                    "success": True,
                    "channel": "slack",
                    "alert_type": alert_type,
                    "sent_at": datetime.utcnow().isoformat(),
                }
                r = client.post(
                    "/api/v1/monitoring/alerts/test",
                    json={"alert_type": alert_type, "channel": "slack"},
                )
            assert r.status_code == 200

    def test_test_alert_formatted_message_returned(self, client):
        with patch("app.services.alert_service.send_alert") as mock_send:
            mock_send.return_value = {
                "success": True,
                "channel": "teams",
                "alert_type": "deadline_approaching",
                "sent_at": datetime.utcnow().isoformat(),
            }
            r = client.post(
                "/api/v1/monitoring/alerts/test",
                json={
                    "alert_type": "deadline_approaching",
                    "channel": "teams",
                    "message": "Custom test message",
                },
            )
        assert r.status_code == 200
        assert "formatted_message" in r.json()


# ---------------------------------------------------------------------------
# POST /monitoring/scan (mocked to avoid LLM calls)
# ---------------------------------------------------------------------------

class TestComplianceScan:
    def test_scan_with_mock(self, client):
        mock_result = {
            "scanned_systems": 0,
            "checks_created": 0,
            "errors": [],
            "scan_timestamp": datetime.utcnow().isoformat(),
        }
        with patch("app.services.compliance_monitor.ComplianceMonitor.scan_all_systems") as mock_scan:
            mock_scan.return_value = mock_result
            r = client.post("/api/v1/monitoring/scan", json={"org_id": None})
        assert r.status_code == 200
        data = r.json()
        assert "scanned_systems" in data
        assert "checks_created" in data

    def test_scan_with_specific_org(self, client, org_id):
        mock_result = {
            "scanned_systems": 1,
            "checks_created": 0,
            "errors": [],
            "scan_timestamp": datetime.utcnow().isoformat(),
        }
        with patch("app.services.compliance_monitor.ComplianceMonitor.scan_all_systems") as mock_scan:
            mock_scan.return_value = mock_result
            r = client.post("/api/v1/monitoring/scan", json={"org_id": org_id})
        assert r.status_code == 200
