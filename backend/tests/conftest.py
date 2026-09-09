"""Shared pytest fixtures.

Each test gets a fresh, isolated in-memory SQLite DB (via SQLAlchemy's
StaticPool so the single in-memory connection is shared across the app's
request-scoped sessions) -- this is intentionally NOT db/labor_planning.db,
which is the demo/seed database described in docs/SOLUTION_ARCHITECTURE.md.
Tests must never depend on or mutate that file.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def warehouse(client):
    payload = {
        "id": "wh-001",
        "name": "Chicago FC-1",
        "location": "Chicago, IL, USA",
        "timezone": "America/Chicago",
    }
    res = client.post("/warehouses", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture()
def job_role(client):
    payload = {"id": "role-picker", "name": "Picker", "skill_level": "entry", "labor_rate": 180.0}
    res = client.post("/job-roles", json=payload)
    assert res.status_code == 201
    return res.json()
