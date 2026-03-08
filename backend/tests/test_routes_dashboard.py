"""
Tests for /api/v1/dashboard endpoints.
Covers: stats counts, risk distribution, recent activity ordering.
"""

import uuid
import pytest
from datetime import datetime, timedelta

from app.store.models import AISystem, ComplianceCheck, Incident


STATS_URL = "/api/v1/dashboard/stats"
RISK_URL = "/api/v1/dashboard/risk-distribution"
ACTIVITY_URL = "/api/v1/dashboard/recent-activity"


# ---------------------------------------------------------------------------
# GET /dashboard/stats
# ---------------------------------------------------------------------------

class TestDashboardStats:
    def test_empty_org_all_zeros(self, client, org_id_b):
        r = client.get(STATS_URL, params={"org_id": org_id_b})
        assert r.status_code == 200
        data = r.json()
        assert data["total_systems"] == 0
        assert data["compliant_count"] == 0
        assert data["incidents_open"] == 0
        assert data["upcoming_deadlines_count"] == 0

    def test_total_systems_count(self, client, org_id, make_ai_system):
        make_ai_system(name="S1")
        make_ai_system(name="S2")
        make_ai_system(name="S3")
        r = client.get(STATS_URL, params={"org_id": org_id})
        assert r.status_code == 200
        assert r.json()["total_systems"] == 3

    def test_compliant_count_gte_70(self, client, org_id, make_ai_system):
        make_ai_system(compliance_score=90.0)   # compliant
        make_ai_system(compliance_score=70.0)   # compliant (boundary)
        make_ai_system(compliance_score=69.9)   # not compliant
        make_ai_system(compliance_score=None)   # not compliant
        r = client.get(STATS_URL, params={"org_id": org_id})
        assert r.status_code == 200
        assert r.json()["compliant_count"] == 2

    def test_incidents_open_count(self, client, org_id, db, sample_ai_system):
        # Create 2 open + 1 resolved incidents
        for status in ("investigating", "mitigating"):
            inc = Incident(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                severity="medium",
                status=status,
                org_id=org_id,
            )
            db.add(inc)
        resolved = Incident(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            severity="low",
            status="resolved",
            org_id=org_id,
        )
        db.add(resolved)
        db.commit()

        r = client.get(STATS_URL, params={"org_id": org_id})
        assert r.status_code == 200
        assert r.json()["incidents_open"] == 2

    def test_upcoming_deadlines_count(self, client, org_id, db, sample_ai_system, sample_regulation):
        # Create check with deadline in 10 days (within 30-day window)
        near_deadline = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="pending",
            priority="high",
            deadline=datetime.utcnow() + timedelta(days=10),
            org_id=org_id,
        )
        # Create check with deadline in 60 days (outside 30-day window)
        far_deadline = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="pending",
            priority="low",
            deadline=datetime.utcnow() + timedelta(days=60),
            org_id=org_id,
        )
        # Create compliant check with near deadline (should NOT count)
        compliant_near = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="compliant",
            priority="low",
            deadline=datetime.utcnow() + timedelta(days=5),
            org_id=org_id,
        )
        db.add_all([near_deadline, far_deadline, compliant_near])
        db.commit()

        r = client.get(STATS_URL, params={"org_id": org_id})
        assert r.status_code == 200
        assert r.json()["upcoming_deadlines_count"] == 1

    def test_stats_requires_org_id(self, client):
        r = client.get(STATS_URL)
        assert r.status_code == 422

    def test_stats_isolation_across_orgs(self, client, org_id, org_id_b, make_ai_system):
        make_ai_system(name="Org A only")
        r = client.get(STATS_URL, params={"org_id": org_id_b})
        assert r.json()["total_systems"] == 0


# ---------------------------------------------------------------------------
# GET /dashboard/risk-distribution
# ---------------------------------------------------------------------------

class TestRiskDistribution:
    def test_empty_org_all_zeros(self, client, org_id_b):
        r = client.get(RISK_URL, params={"org_id": org_id_b})
        assert r.status_code == 200
        dist = r.json()["risk_distribution"]
        assert dist["unacceptable"] == 0
        assert dist["high"] == 0
        assert dist["limited"] == 0
        assert dist["minimal"] == 0
        assert dist["unclassified"] == 0

    def test_all_risk_tiers_present_in_response(self, client, org_id_b):
        r = client.get(RISK_URL, params={"org_id": org_id_b})
        assert r.status_code == 200
        dist = r.json()["risk_distribution"]
        for tier in ("unacceptable", "high", "limited", "minimal", "unclassified"):
            assert tier in dist

    def test_risk_distribution_counts(self, client, org_id, make_ai_system):
        make_ai_system(risk_classification="high")
        make_ai_system(risk_classification="high")
        make_ai_system(risk_classification="limited")
        make_ai_system(risk_classification="minimal")
        make_ai_system(risk_classification="unclassified")

        r = client.get(RISK_URL, params={"org_id": org_id})
        assert r.status_code == 200
        dist = r.json()["risk_distribution"]
        assert dist["high"] == 2
        assert dist["limited"] == 1
        assert dist["minimal"] == 1
        assert dist["unclassified"] == 1

    def test_requires_org_id(self, client):
        r = client.get(RISK_URL)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /dashboard/recent-activity
# ---------------------------------------------------------------------------

class TestRecentActivity:
    def test_empty_org_empty_list(self, client, org_id_b):
        r = client.get(ACTIVITY_URL, params={"org_id": org_id_b})
        assert r.status_code == 200
        assert r.json()["recent_activity"] == []

    def test_activity_includes_compliance_checks(
        self, client, org_id, db, sample_ai_system, sample_regulation
    ):
        check = ComplianceCheck(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            regulation_id=sample_regulation.id,
            status="partial",
            priority="high",
            org_id=org_id,
        )
        db.add(check)
        db.commit()

        r = client.get(ACTIVITY_URL, params={"org_id": org_id})
        assert r.status_code == 200
        activity = r.json()["recent_activity"]
        types = [a["type"] for a in activity]
        assert "compliance_check" in types

    def test_activity_includes_incidents(self, client, org_id, sample_incident):
        r = client.get(ACTIVITY_URL, params={"org_id": org_id})
        assert r.status_code == 200
        activity = r.json()["recent_activity"]
        types = [a["type"] for a in activity]
        assert "incident" in types

    def test_activity_max_10_entries(self, client, org_id, db, sample_ai_system, sample_regulation):
        # Create 15 compliance checks
        for i in range(15):
            check = ComplianceCheck(
                id=str(uuid.uuid4()),
                ai_system_id=sample_ai_system.id,
                regulation_id=sample_regulation.id,
                status="pending",
                priority="low",
                org_id=org_id,
            )
            db.add(check)
        db.commit()

        r = client.get(ACTIVITY_URL, params={"org_id": org_id})
        assert r.status_code == 200
        assert len(r.json()["recent_activity"]) <= 10

    def test_activity_sorted_most_recent_first(self, client, org_id, db, sample_ai_system):
        # Create incidents at different times
        old_incident = Incident(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            severity="low",
            status="resolved",
            detected_at=datetime.utcnow() - timedelta(days=10),
            org_id=org_id,
        )
        new_incident = Incident(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            severity="high",
            status="investigating",
            detected_at=datetime.utcnow(),
            org_id=org_id,
        )
        db.add_all([old_incident, new_incident])
        db.commit()

        r = client.get(ACTIVITY_URL, params={"org_id": org_id})
        assert r.status_code == 200
        activity = r.json()["recent_activity"]
        # Most recent should appear first
        if len(activity) >= 2:
            assert activity[0]["timestamp"] >= activity[1]["timestamp"]

    def test_activity_entry_structure(self, client, org_id, sample_incident):
        r = client.get(ACTIVITY_URL, params={"org_id": org_id})
        assert r.status_code == 200
        activity = r.json()["recent_activity"]
        assert len(activity) >= 1
        entry = activity[0]
        assert "id" in entry
        assert "type" in entry
        assert "summary" in entry
        assert "status" in entry
        assert "timestamp" in entry

    def test_requires_org_id(self, client):
        r = client.get(ACTIVITY_URL)
        assert r.status_code == 422
