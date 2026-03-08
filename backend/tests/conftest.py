"""
Shared test fixtures and factories for the Adhi Compliance test suite.

Sets required environment variables BEFORE any app module is imported so that
config.py singleton validation passes without real API keys.
"""

import os
import uuid

# ---------------------------------------------------------------------------
# Stub env vars before any app import (config.py validates on module load)
# ---------------------------------------------------------------------------
os.environ.setdefault("GOOGLE_API_KEY", "test-fake-google-key-for-testing-only")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret-at-least-32-chars!!")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("LLM_PROVIDER", "gemini")

import pytest
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# App imports (after env vars are set)
# ---------------------------------------------------------------------------
from app.store.metadata_store import Base, Organization, ServiceProvider
from app.store.models import (
    User, AISystem, Regulation, ComplianceCheck,
    BiasAudit, Incident, ModelCard, get_db_session,
)
from app.main import app

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


# ---------------------------------------------------------------------------
# Engine + Session fixtures  (function-scoped → fresh DB per test)
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    """Create a fresh in-memory SQLite engine with all tables for each test."""
    _engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)
    _engine.dispose()


@pytest.fixture
def db(engine):
    """Provide a SQLAlchemy session that rolls back after each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


# ---------------------------------------------------------------------------
# FastAPI test client with DB override
# ---------------------------------------------------------------------------

@pytest.fixture
def client(db):
    """Return a FastAPI TestClient with get_db_session overridden to use test DB."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db_session] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed helpers: ServiceProvider + Organization
# ---------------------------------------------------------------------------

@pytest.fixture
def service_provider(db):
    """Create and persist a test ServiceProvider."""
    provider = ServiceProvider(
        id=str(uuid.uuid4()),
        business_name="Test Service Provider",
        admin_email=f"provider-{uuid.uuid4().hex[:8]}@test.com",
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@pytest.fixture
def org_id(db, service_provider):
    """Create and persist a test Organization; return its ID string."""
    org = Organization(
        id=str(uuid.uuid4()),
        service_provider_id=service_provider.id,
        name="Test Organization",
        slug=f"test-org-{uuid.uuid4().hex[:6]}",
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org.id


@pytest.fixture
def org_id_b(db, service_provider):
    """A SECOND organization (for cross-tenant isolation tests)."""
    org = Organization(
        id=str(uuid.uuid4()),
        service_provider_id=service_provider.id,
        name="Other Organization",
        slug=f"other-org-{uuid.uuid4().hex[:6]}",
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org.id


# ---------------------------------------------------------------------------
# Model fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_user(db, org_id):
    user = User(
        id=str(uuid.uuid4()),
        email="user@example.com",
        name="Test User",
        role="member",
        org_id=org_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db, org_id):
    user = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        name="Admin User",
        role="admin",
        org_id=org_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_ai_system(db, org_id):
    system = AISystem(
        id=str(uuid.uuid4()),
        name="Test Chatbot",
        purpose="Customer support chatbot for e-commerce",
        description="Conversational AI for handling customer queries",
        model_provider="OpenAI",
        data_types=["text", "PII"],
        deployment_regions=["EU", "US"],
        risk_classification="limited",
        is_high_risk=False,
        compliance_score=75.0,
        org_id=org_id,
    )
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


@pytest.fixture
def high_risk_ai_system(db, org_id):
    system = AISystem(
        id=str(uuid.uuid4()),
        name="Biometric Auth System",
        purpose="Biometric identification and facial recognition for access control",
        description="Facial recognition system for building access",
        model_provider="Custom",
        data_types=["biometric", "facial images"],
        deployment_regions=["EU"],
        risk_classification="high",
        is_high_risk=True,
        compliance_score=30.0,
        org_id=org_id,
    )
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


@pytest.fixture
def sample_regulation(db):
    regulation = Regulation(
        id=str(uuid.uuid4()),
        name="EU Artificial Intelligence Act",
        short_name="EU AI Act",
        jurisdiction="EU",
        category="AI Governance",
        url="https://eur-lex.europa.eu/",
    )
    db.add(regulation)
    db.commit()
    db.refresh(regulation)
    return regulation


@pytest.fixture
def sample_compliance_check(db, org_id, sample_ai_system, sample_regulation):
    check = ComplianceCheck(
        id=str(uuid.uuid4()),
        ai_system_id=sample_ai_system.id,
        regulation_id=sample_regulation.id,
        status="pending",
        gap_description="Missing transparency documentation",
        remediation_steps="1. Add model card\n2. Document training data",
        priority="medium",
        org_id=org_id,
        checked_at=datetime.utcnow(),
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@pytest.fixture
def sample_incident(db, org_id, sample_ai_system):
    incident = Incident(
        id=str(uuid.uuid4()),
        ai_system_id=sample_ai_system.id,
        severity="high",
        incident_type="bias_detected",
        description="Bias detected in loan recommendation output",
        status="investigating",
        timeline=[{"timestamp": datetime.utcnow().isoformat(), "event": "Incident opened"}],
        org_id=org_id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@pytest.fixture
def sample_bias_audit(db, org_id, sample_ai_system):
    audit = BiasAudit(
        id=str(uuid.uuid4()),
        ai_system_id=sample_ai_system.id,
        dataset_description="Hiring dataset Q1 2024",
        demographic_parity_score=0.15,
        disparate_impact_ratio=0.72,
        overall_status="fail",
        findings={"summary": "Significant bias detected in gender attribute"},
        org_id=org_id,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


# ---------------------------------------------------------------------------
# Factory-style helpers (callable fixtures for creating multiple records)
# ---------------------------------------------------------------------------

@pytest.fixture
def make_ai_system(db, org_id):
    """Factory fixture — call to create custom AISystem records."""
    def _factory(**kwargs):
        defaults = dict(
            id=str(uuid.uuid4()),
            name=f"AI System {uuid.uuid4().hex[:6]}",
            purpose="General purpose AI",
            description="Test AI system",
            model_provider="TestProvider",
            data_types=["text"],
            deployment_regions=["EU"],
            risk_classification="minimal",
            is_high_risk=False,
            compliance_score=None,
            org_id=org_id,
        )
        defaults.update(kwargs)
        system = AISystem(**defaults)
        db.add(system)
        db.commit()
        db.refresh(system)
        return system
    return _factory


@pytest.fixture
def make_regulation(db):
    """Factory fixture — call to create custom Regulation records."""
    def _factory(**kwargs):
        defaults = dict(
            id=str(uuid.uuid4()),
            name=f"Regulation {uuid.uuid4().hex[:6]}",
            short_name="REG",
            jurisdiction="EU",
            category="AI Governance",
        )
        defaults.update(kwargs)
        reg = Regulation(**defaults)
        db.add(reg)
        db.commit()
        db.refresh(reg)
        return reg
    return _factory


@pytest.fixture
def make_incident(db, org_id, sample_ai_system):
    """Factory fixture — call to create custom Incident records."""
    def _factory(**kwargs):
        defaults = dict(
            id=str(uuid.uuid4()),
            ai_system_id=sample_ai_system.id,
            severity="medium",
            incident_type="drift",
            description="Test incident",
            status="investigating",
            timeline=[],
            org_id=org_id,
        )
        defaults.update(kwargs)
        incident = Incident(**defaults)
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident
    return _factory


# ---------------------------------------------------------------------------
# JWT test token helper
# ---------------------------------------------------------------------------

def make_test_jwt(user_id: str, email: str, secret: str = "test-jwt-secret-at-least-32-chars!!") -> str:
    """Generate a test HS256 JWT for auth tests."""
    from jose import jwt
    payload = {
        "sub": user_id,
        "email": email,
        "aud": "authenticated",
        "iat": 1700000000,
        "exp": 9999999999,  # far future
    }
    return jwt.encode(payload, secret, algorithm="HS256")
