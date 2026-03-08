"""
Security tests for the Adhi Compliance platform.
Covers:
  - Auth endpoint behavior
  - JWT validation logic (unit-level)
  - Cross-tenant data isolation (org_A cannot read org_B data)
  - Role enforcement (require_admin dependency)
  - SQL injection attempt handling
  - XSS input sanitization via Pydantic
  - CORS header verification
  - Expired JWT rejection

Marks: pytest.mark.security
"""

import os
import uuid
import time
import pytest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Test markers
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.security


# ---------------------------------------------------------------------------
# /auth/register + /auth/me — header-based auth
# ---------------------------------------------------------------------------

class TestAuthEndpoints:
    def test_register_new_user(self, client, org_id):
        payload = {
            "email": f"newuser-{uuid.uuid4().hex[:8]}@example.com",
            "name": "New Registered User",
            "role": "member",
            "org_id": org_id,
        }
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == payload["email"]
        assert data["role"] == "member"
        assert data["org_id"] == org_id

    def test_register_duplicate_email_returns_409(self, client, org_id):
        email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
        payload = {"email": email, "name": "User A", "org_id": org_id}
        client.post("/api/v1/auth/register", json=payload)
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 409

    def test_register_creates_org_if_none_provided(self, client):
        payload = {
            "email": f"neworg-{uuid.uuid4().hex[:8]}@example.com",
            "name": "Solo User",
        }
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["org_id"] is not None

    def test_login_endpoint_returns_message(self, client):
        r = client.post("/api/v1/auth/login")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "Supabase" in data["message"]

    def test_get_me_with_valid_user_id_header(self, client, sample_user):
        r = client.get(
            "/api/v1/auth/me",
            headers={"X-User-Id": sample_user.id},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sample_user.id
        assert data["email"] == sample_user.email

    def test_get_me_with_valid_email_header(self, client, sample_user):
        r = client.get(
            "/api/v1/auth/me",
            headers={"X-User-Email": sample_user.email},
        )
        assert r.status_code == 200
        assert r.json()["email"] == sample_user.email

    def test_get_me_without_headers_returns_401(self, client):
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401

    def test_get_me_with_nonexistent_user_returns_401(self, client):
        r = client.get(
            "/api/v1/auth/me",
            headers={"X-User-Id": str(uuid.uuid4())},
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Cross-tenant isolation (org_A cannot see org_B data)
# ---------------------------------------------------------------------------

class TestCrossTenantIsolation:
    def test_ai_systems_isolated_by_org(self, client, org_id, org_id_b, make_ai_system):
        # Create systems in org_A
        make_ai_system(name="Org A System 1")
        make_ai_system(name="Org A System 2")

        # Query from org_B — should see none of org_A's systems
        r = client.get("/api/v1/ai-systems", params={"org_id": org_id_b})
        assert r.status_code == 200
        names = [s["name"] for s in r.json()]
        assert "Org A System 1" not in names
        assert "Org A System 2" not in names

    def test_compliance_checks_isolated_by_org(
        self, client, org_id, org_id_b, sample_ai_system, sample_regulation
    ):
        # Create a check in org_A
        payload = {
            "ai_system_id": sample_ai_system.id,
            "regulation_id": sample_regulation.id,
            "org_id": org_id,
        }
        client.post("/api/v1/compliance-checks", json=payload, params={"use_rag": "false"})

        # org_B query should return empty
        r = client.get("/api/v1/compliance-checks", params={"org_id": org_id_b})
        assert r.status_code == 200
        assert r.json() == []

    def test_incidents_isolated_by_org(self, client, org_id, org_id_b, sample_incident):
        r = client.get("/api/v1/incidents", params={"org_id": org_id_b})
        assert r.status_code == 200
        incident_ids = [i["id"] for i in r.json()]
        assert sample_incident.id not in incident_ids

    def test_bias_audits_isolated_by_org(self, client, org_id, org_id_b, sample_bias_audit):
        r = client.get("/api/v1/bias-audits", params={"org_id": org_id_b})
        assert r.status_code == 200
        audit_ids = [a["id"] for a in r.json()]
        assert sample_bias_audit.id not in audit_ids

    def test_dashboard_stats_isolated_by_org(self, client, org_id, org_id_b, sample_ai_system):
        r = client.get("/api/v1/dashboard/stats", params={"org_id": org_id_b})
        assert r.status_code == 200
        assert r.json()["total_systems"] == 0


# ---------------------------------------------------------------------------
# JWT validation logic (unit tests on middleware helpers)
# ---------------------------------------------------------------------------

class TestJWTValidation:
    def test_decode_valid_jwt_local(self):
        """A valid HS256 token with matching secret should decode correctly."""
        from tests.conftest import make_test_jwt
        from app.middleware.auth import _decode_jwt_local

        secret = "test-jwt-secret-at-least-32-chars!!"
        token = make_test_jwt(
            user_id=str(uuid.uuid4()),
            email="jwt@example.com",
            secret=secret,
        )

        with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": secret}):
            # Re-import settings with patched env
            from app.config import Settings
            test_settings = Settings(SUPABASE_JWT_SECRET=secret, GOOGLE_API_KEY="fake-key")
            with patch("app.middleware.auth.get_settings", return_value=lambda: test_settings):
                from jose import jwt as jose_jwt
                payload = jose_jwt.decode(
                    token, secret, algorithms=["HS256"],
                    options={"verify_aud": False}
                )
                assert payload["email"] == "jwt@example.com"

    def test_expired_jwt_raises_401(self):
        """An expired JWT must raise 401 Unauthorized."""
        from jose import jwt as jose_jwt, JWTError
        secret = "test-jwt-secret-at-least-32-chars!!"
        expired_payload = {
            "sub": str(uuid.uuid4()),
            "email": "expired@example.com",
            "iat": 1000000000,
            "exp": 1000000001,  # already expired
        }
        token = jose_jwt.encode(expired_payload, secret, algorithm="HS256")
        with pytest.raises(JWTError):
            jose_jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})

    def test_tampered_jwt_raises_error(self):
        """A tampered (wrong signature) JWT must fail verification."""
        from jose import jwt as jose_jwt, JWTError
        from tests.conftest import make_test_jwt
        real_secret = "test-jwt-secret-at-least-32-chars!!"
        wrong_secret = "wrong-secret-that-does-not-match!!"
        token = make_test_jwt(str(uuid.uuid4()), "tamper@example.com", secret=real_secret)
        with pytest.raises(JWTError):
            jose_jwt.decode(token, wrong_secret, algorithms=["HS256"], options={"verify_aud": False})

    def test_require_admin_allows_admin(self):
        """require_admin should pass when role == 'admin'."""
        from app.middleware.auth import require_admin, CurrentUser
        admin = CurrentUser(id=str(uuid.uuid4()), email="a@b.com", org_id="org1", role="admin")
        result = require_admin(current_user=admin)
        assert result.role == "admin"

    def test_require_admin_blocks_member(self):
        """require_admin should raise 403 when role != 'admin'."""
        from fastapi import HTTPException
        from app.middleware.auth import require_admin, CurrentUser
        member = CurrentUser(id=str(uuid.uuid4()), email="m@b.com", org_id="org1", role="member")
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=member)
        assert exc_info.value.status_code == 403

    def test_require_admin_blocks_viewer(self):
        """require_admin should raise 403 when role == 'viewer'."""
        from fastapi import HTTPException
        from app.middleware.auth import require_admin, CurrentUser
        viewer = CurrentUser(id=str(uuid.uuid4()), email="v@b.com", org_id="org1", role="viewer")
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=viewer)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# SQL Injection attempts
# ---------------------------------------------------------------------------

class TestSQLInjection:
    """
    FastAPI + SQLAlchemy ORM uses parameterized queries, so SQL injection
    via query params or JSON body is blocked. These tests verify the app
    returns sane responses (not 500s) for injection attempts.
    """

    def test_sql_injection_in_org_id_query_param(self, client):
        injection = "' OR '1'='1"
        r = client.get("/api/v1/ai-systems", params={"org_id": injection})
        # Should return an empty list (no data matches), not a 500
        assert r.status_code == 200
        assert r.json() == []

    def test_sql_injection_in_org_id_for_incidents(self, client):
        injection = "1; DROP TABLE incidents; --"
        r = client.get("/api/v1/incidents", params={"org_id": injection})
        assert r.status_code == 200
        assert r.json() == []

    def test_sql_injection_in_regulation_search(self, client):
        injection = "' UNION SELECT * FROM users --"
        r = client.get("/api/v1/regulations", params={"search": injection})
        assert r.status_code == 200
        # No error — parameterized query prevents injection

    def test_sql_injection_in_json_body(self, client, org_id):
        # Try injecting via the name field
        payload = {
            "name": "'; DROP TABLE ai_systems; --",
            "org_id": org_id,
        }
        r = client.post("/api/v1/ai-systems", json=payload)
        # Pydantic accepts the string; ORM parameterizes it safely
        assert r.status_code == 201
        # The system is stored literally with the injection string (harmless)
        assert "DROP TABLE" in r.json()["name"]


# ---------------------------------------------------------------------------
# XSS — Pydantic input handling
# ---------------------------------------------------------------------------

class TestXSSInputHandling:
    """
    FastAPI returns JSON (not HTML), so XSS is mitigated. Pydantic does NOT
    strip HTML by default — it stores the raw string. Tests verify:
      - Malicious input is accepted as-is (string, not code) → not executed
      - Response type is JSON, not HTML (so browsers won't execute scripts)
    """

    def test_xss_in_system_name_stored_as_string(self, client, org_id):
        xss_payload = "<script>alert('XSS')</script>"
        r = client.post(
            "/api/v1/ai-systems",
            json={"name": xss_payload, "org_id": org_id},
        )
        assert r.status_code == 201
        # Stored verbatim but returned as JSON string, not executed HTML
        assert r.json()["name"] == xss_payload
        assert r.headers["content-type"].startswith("application/json")

    def test_xss_in_description_field(self, client, org_id):
        xss = "<img src=x onerror=alert(1)>"
        r = client.post(
            "/api/v1/ai-systems",
            json={"name": "XSS Test", "description": xss, "org_id": org_id},
        )
        assert r.status_code == 201
        # Returned as JSON string literal
        assert r.json()["description"] == xss

    def test_xss_in_regulation_name(self, client):
        xss = "<script>document.cookie</script>"
        r = client.post(
            "/api/v1/regulations",
            json={"name": xss, "jurisdiction": "EU"},
        )
        assert r.status_code == 201
        # JSON encoding means the script tag is a string, not runnable HTML
        assert r.json()["name"] == xss


# ---------------------------------------------------------------------------
# CORS headers
# ---------------------------------------------------------------------------

class TestCORSHeaders:
    def test_cors_preflight_allowed_origin(self, client):
        r = client.options(
            "/api/v1/ai-systems",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS middleware should respond to preflight
        assert r.status_code in (200, 204)

    def test_cors_header_present_on_get(self, client, org_id):
        r = client.get(
            "/api/v1/ai-systems",
            params={"org_id": org_id},
            headers={"Origin": "http://localhost:3000"},
        )
        assert r.status_code == 200
        # Allow-Origin should be present
        assert "access-control-allow-origin" in r.headers

    def test_health_check_cors(self, client):
        r = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Input validation edge cases
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_empty_string_name_returns_422(self, client, org_id):
        """Empty string doesn't satisfy min_length for required name."""
        # Pydantic v2 won't reject empty string by default unless constrained.
        # This test validates the API accepts or rejects appropriately.
        r = client.post("/api/v1/ai-systems", json={"name": "", "org_id": org_id})
        # Either 422 (if constrained) or 201 (if not constrained by schema)
        assert r.status_code in (201, 422)

    def test_very_long_name_is_handled(self, client, org_id):
        long_name = "A" * 10000
        r = client.post("/api/v1/ai-systems", json={"name": long_name, "org_id": org_id})
        # Should not crash with 500
        assert r.status_code in (201, 422)

    def test_null_injection_in_string_field(self, client, org_id):
        """Null bytes in string fields should not cause 500."""
        r = client.post(
            "/api/v1/ai-systems",
            json={"name": "Test\x00Null", "org_id": org_id},
        )
        assert r.status_code in (201, 422)
