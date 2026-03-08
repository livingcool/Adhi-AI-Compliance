"""
Tests for /api/v1/regulations endpoints.
Covers: CRUD, filtering by jurisdiction/category/search, 404 handling.
"""

import uuid
import pytest

BASE = "/api/v1/regulations"


def _reg_payload(**kwargs):
    defaults = dict(
        name=f"Regulation {uuid.uuid4().hex[:6]}",
        short_name="REG",
        jurisdiction="EU",
        category="AI Governance",
        url="https://example.com",
    )
    defaults.update(kwargs)
    return defaults


class TestCreateRegulation:
    def test_create_minimal(self, client):
        r = client.post(BASE, json={"name": "Minimal Regulation"})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Minimal Regulation"
        assert "id" in data
        assert "created_at" in data

    def test_create_full(self, client):
        payload = _reg_payload(
            name="EU Artificial Intelligence Act",
            short_name="EU AI Act",
            jurisdiction="EU",
            category="AI Governance",
            url="https://eur-lex.europa.eu/",
            full_text="Full text of the regulation...",
        )
        r = client.post(BASE, json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["short_name"] == "EU AI Act"
        assert data["jurisdiction"] == "EU"

    def test_create_missing_name_422(self, client):
        r = client.post(BASE, json={"jurisdiction": "US"})
        assert r.status_code == 422

    def test_optional_fields_null_by_default(self, client):
        r = client.post(BASE, json={"name": "No Extras"})
        assert r.status_code == 201
        data = r.json()
        assert data["short_name"] is None
        assert data["jurisdiction"] is None
        assert data["full_text"] is None


class TestGetRegulation:
    def test_get_existing(self, client, sample_regulation):
        r = client.get(f"{BASE}/{sample_regulation.id}")
        assert r.status_code == 200
        assert r.json()["id"] == sample_regulation.id

    def test_get_nonexistent_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


class TestListRegulations:
    def test_list_all(self, client, sample_regulation):
        r = client.get(BASE)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_filter_by_jurisdiction(self, client, db):
        from app.store.models import Regulation
        db.add(Regulation(id=str(uuid.uuid4()), name="EU Reg", jurisdiction="EU"))
        db.add(Regulation(id=str(uuid.uuid4()), name="US Reg", jurisdiction="US"))
        db.add(Regulation(id=str(uuid.uuid4()), name="IN Reg", jurisdiction="IN"))
        db.commit()

        r = client.get(BASE, params={"jurisdiction": "EU"})
        assert r.status_code == 200
        data = r.json()
        assert all(reg["jurisdiction"] == "EU" for reg in data)
        names = [reg["name"] for reg in data]
        assert "EU Reg" in names

    def test_filter_by_category(self, client, db):
        from app.store.models import Regulation
        db.add(Regulation(id=str(uuid.uuid4()), name="AI Gov", category="AI Governance"))
        db.add(Regulation(id=str(uuid.uuid4()), name="Data Priv", category="Data Privacy"))
        db.commit()

        r = client.get(BASE, params={"category": "AI Governance"})
        assert r.status_code == 200
        data = r.json()
        assert all(reg["category"] == "AI Governance" for reg in data)

    def test_filter_by_search(self, client, db):
        from app.store.models import Regulation
        db.add(Regulation(id=str(uuid.uuid4()), name="Artificial Intelligence Regulation"))
        db.add(Regulation(id=str(uuid.uuid4()), name="Data Protection Rule"))
        db.commit()

        r = client.get(BASE, params={"search": "Artificial"})
        assert r.status_code == 200
        data = r.json()
        assert all("artificial" in reg["name"].lower() for reg in data)


class TestUpdateRegulation:
    def test_patch_name(self, client, sample_regulation):
        r = client.patch(f"{BASE}/{sample_regulation.id}", json={"name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Name"

    def test_patch_jurisdiction(self, client, sample_regulation):
        r = client.patch(f"{BASE}/{sample_regulation.id}", json={"jurisdiction": "US"})
        assert r.status_code == 200
        assert r.json()["jurisdiction"] == "US"

    def test_patch_nonexistent_404(self, client):
        r = client.patch(f"{BASE}/{uuid.uuid4()}", json={"name": "Ghost"})
        assert r.status_code == 404


class TestDeleteRegulation:
    def test_delete_existing(self, client, sample_regulation):
        r = client.delete(f"{BASE}/{sample_regulation.id}")
        assert r.status_code == 204

    def test_delete_then_get_404(self, client, sample_regulation):
        client.delete(f"{BASE}/{sample_regulation.id}")
        r = client.get(f"{BASE}/{sample_regulation.id}")
        assert r.status_code == 404

    def test_delete_nonexistent_404(self, client):
        r = client.delete(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404
