"""Integration tests for scenario save/list/retrieve/delete/clone operations."""

from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.main import app
from app.database import get_db
from app.models.architecture import (
    Architecture,
    Base,
    Component,
    Scenario,
    SimulationResult,
)

# SQLite does not support JSONB natively. Compile JSONB as JSON for tests.
SQLiteTypeCompiler.visit_JSONB = SQLiteTypeCompiler.visit_JSON  # type: ignore[attr-defined]


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_fk_pragma(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    SessionFactory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = SessionFactory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session: Session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def _seed_architecture(db: Session) -> tuple[int, int, int]:
    arch = Architecture(name="Scenario Storage Test", description="", properties={})
    db.add(arch)
    db.flush()

    c1 = Component(
        architecture_id=arch.id,
        component_id="sensor-1",
        name="Sensor 1",
        component_type="Sensor",
        criticality=7,
        properties={},
    )
    c2 = Component(
        architecture_id=arch.id,
        component_id="compute-1",
        name="Compute 1",
        component_type="Compute",
        criticality=8,
        properties={},
    )
    db.add(c1)
    db.add(c2)
    db.commit()
    return arch.id, c1.id, c2.id


def _create_scenario_with_results(client, architecture_id: int, target_id: int) -> dict:
    payload = {
        "scenario_type": "node_compromise",
        "target_component_id": target_id,
        "parameters": {"severity": "high", "retries": 2},
        "results": [
            {
                "baseline_score": 100.0,
                "compromised_score": 70.0,
                "affected_components": [target_id],
                "attack_path": ["Step 1: target compromised"],
                "explanation": "Scenario saved with one result.",
            }
        ],
    }
    response = client.post(f"/architectures/{architecture_id}/scenarios", json=payload)
    assert response.status_code == 201
    return response.json()


class TestScenarioLibraryEndpoints:

    def test_post_saves_scenario_and_results(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)

        saved = _create_scenario_with_results(client, architecture_id, target_id)

        assert saved["architecture_id"] == architecture_id
        assert saved["target_component_id"] == target_id
        assert saved["scenario_type"] == "node_compromise"
        assert len(saved["results"]) == 1
        assert saved["results"][0]["baseline_score"] == 100.0

    def test_get_architecture_scenarios_lists_all(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)
        created = _create_scenario_with_results(client, architecture_id, target_id)

        listed = client.get(f"/architectures/{architecture_id}/scenarios")
        assert listed.status_code == 200
        assert any(item["id"] == created["id"] for item in listed.json())

    def test_get_scenario_returns_full_results(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)
        created = _create_scenario_with_results(client, architecture_id, target_id)

        fetched = client.get(f"/scenarios/{created['id']}")
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == created["id"]
        assert body["architecture_id"] == architecture_id
        assert len(body["results"]) == 1
        assert body["results"][0]["compromised_score"] == 70.0

    def test_delete_scenario_by_id(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)
        created = _create_scenario_with_results(client, architecture_id, target_id)
        scenario_id = created["id"]

        deleted = client.delete(f"/scenarios/{scenario_id}")
        assert deleted.status_code == 204

        assert db_session.query(Scenario).filter(Scenario.id == scenario_id).first() is None
        assert (
            db_session.query(SimulationResult)
            .filter(SimulationResult.scenario_id == scenario_id)
            .count()
            == 0
        )

    def test_clone_scenario_duplicates_scenario_and_results(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)
        original = _create_scenario_with_results(client, architecture_id, target_id)

        cloned = client.post(f"/scenarios/{original['id']}/clone")
        assert cloned.status_code == 201

        body = cloned.json()
        assert body["id"] != original["id"]
        assert body["architecture_id"] == original["architecture_id"]
        assert body["scenario_type"] == original["scenario_type"]
        assert len(body["results"]) == 1
        assert (
            body["results"][0]["baseline_score"]
            == original["results"][0]["baseline_score"]
        )

    def test_missing_scenario_operations_return_404(self, client):
        assert client.get("/scenarios/999999").status_code == 404
        assert client.delete("/scenarios/999999").status_code == 404
        assert client.post("/scenarios/999999/clone").status_code == 404

    def test_openapi_contains_required_scenario_endpoints(self, client):
        openapi = client.get("/openapi.json")
        assert openapi.status_code == 200
        paths = openapi.json()["paths"]

        assert "/architectures/{architecture_id}/scenarios" in paths
        assert "post" in paths["/architectures/{architecture_id}/scenarios"]
        assert "get" in paths["/architectures/{architecture_id}/scenarios"]
        assert "/scenarios/{scenario_id}" in paths
        assert "get" in paths["/scenarios/{scenario_id}"]
        assert "delete" in paths["/scenarios/{scenario_id}"]
        assert "post" in paths["/scenarios/{scenario_id}/clone"]
