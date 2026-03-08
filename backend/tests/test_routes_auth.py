"""
Tests for /api/v1/auth endpoints.
Covers: register, login, get_me.
"""

import uuid
import pytest

BASE = "/api/v1/auth"


class TestRegisterUser:
    def test_register_with_existing_org(self, client, org_id):
        email = f"reg-{uuid.uuid4().hex[:8]}@example.com"
        r = client.post(f"{BASE}/register", json={
            "email": email,
            "name": "Register Test",
            "role": "member",
            "org_id": org_id,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == email
        assert data["name"] == "Register Test"
        assert data["role"] == "member"
        assert data["org_id"] == org_id
        assert "id" in data

    def test_register_without_org_creates_new_org(self, client):
        email = f"solo-{uuid.uuid4().hex[:8]}@example.com"
        r = client.post(f"{BASE}/register", json={
            "email": email,
            "name": "Solo User",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["org_id"] is not None

    def test_register_duplicate_email_409(self, client, org_id):
        email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
        client.post(f"{BASE}/register", json={"email": email, "name": "First", "org_id": org_id})
        r = client.post(f"{BASE}/register", json={"email": email, "name": "Second", "org_id": org_id})
        assert r.status_code == 409
        assert "already exists" in r.json()["detail"].lower()

    def test_register_default_role_is_member(self, client, org_id):
        r = client.post(f"{BASE}/register", json={
            "email": f"defr-{uuid.uuid4().hex[:8]}@example.com",
            "name": "Default Role",
            "org_id": org_id,
        })
        assert r.status_code == 201
        assert r.json()["role"] == "member"

    @pytest.mark.parametrize("role", ["admin", "member", "viewer"])
    def test_register_all_roles(self, client, org_id, role):
        r = client.post(f"{BASE}/register", json={
            "email": f"role-{role}-{uuid.uuid4().hex[:6]}@example.com",
            "name": f"User {role}",
            "role": role,
            "org_id": org_id,
        })
        assert r.status_code == 201
        assert r.json()["role"] == role

    def test_register_missing_email_422(self, client, org_id):
        r = client.post(f"{BASE}/register", json={"name": "No Email", "org_id": org_id})
        assert r.status_code == 422

    def test_register_missing_name_422(self, client, org_id):
        r = client.post(f"{BASE}/register", json={
            "email": f"noname-{uuid.uuid4().hex[:8]}@example.com",
            "org_id": org_id,
        })
        assert r.status_code == 422


class TestLoginEndpoint:
    def test_login_returns_200_with_message(self, client):
        r = client.post(f"{BASE}/login")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "Supabase" in data["message"]
        assert "docs" in data


class TestGetMe:
    def test_get_me_by_user_id(self, client, sample_user):
        r = client.get(f"{BASE}/me", headers={"X-User-Id": sample_user.id})
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sample_user.id
        assert data["email"] == sample_user.email

    def test_get_me_by_email(self, client, sample_user):
        r = client.get(f"{BASE}/me", headers={"X-User-Email": sample_user.email})
        assert r.status_code == 200
        assert r.json()["email"] == sample_user.email

    def test_get_me_no_headers_401(self, client):
        r = client.get(f"{BASE}/me")
        assert r.status_code == 401

    def test_get_me_unknown_user_id_401(self, client):
        r = client.get(f"{BASE}/me", headers={"X-User-Id": str(uuid.uuid4())})
        assert r.status_code == 401

    def test_get_me_unknown_email_401(self, client):
        r = client.get(f"{BASE}/me", headers={"X-User-Email": "nobody@nowhere.com"})
        assert r.status_code == 401

    def test_get_me_returns_correct_role(self, client, admin_user):
        r = client.get(f"{BASE}/me", headers={"X-User-Id": admin_user.id})
        assert r.status_code == 200
        assert r.json()["role"] == "admin"
