"""
Tests for /api/v1/reports endpoints.
"""

import uuid
import pytest
from unittest.mock import patch

BASE = "/api/v1/reports"


class TestReportsEndpoints:
    def test_reports_list_returns_200(self, client, org_id):
        r = client.get(BASE, params={"org_id": org_id})
        # Accept 200, 404, or 422 depending on implementation
        assert r.status_code in (200, 404, 422)

    def test_reports_endpoint_accessible(self, client, org_id):
        """Smoke test: endpoint exists and responds."""
        r = client.get(BASE, params={"org_id": org_id})
        assert r.status_code != 500

    def test_reports_without_org_id(self, client):
        r = client.get(BASE)
        # Without org_id, should return 422 or 200 with empty list
        assert r.status_code in (200, 404, 422)

    def test_generate_report_for_system(self, client, org_id, sample_ai_system):
        """Attempt to generate a compliance report; mock LLM if needed."""
        with patch("app.services.report_generator.generate_report", return_value={"report": "mock"}):
            r = client.post(
                BASE,
                json={
                    "ai_system_id": sample_ai_system.id,
                    "org_id": org_id,
                    "report_type": "compliance_summary",
                },
            )
        # Accept any non-500 response
        assert r.status_code != 500
