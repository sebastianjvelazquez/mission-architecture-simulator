"""Integration tests for DELETE /architectures/{id}."""

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
    Flow,
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
    session_factory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = session_factory()
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


def _seed_graph_and_scenario(db: Session) -> dict[str, int]:
    arch = Architecture(name="Delete Me", description="cascade test", properties={})
    db.add(arch)
    db.flush()

    c1 = Component(
        architecture_id=arch.id,
        component_id="a",
        name="A",
        component_type="Sensor",
        criticality=8,
        properties={},
    )
    c2 = Component(
        architecture_id=arch.id,
        component_id="b",
        name="B",
        component_type="Compute",
        criticality=9,
        properties={},
    )
    db.add(c1)
    db.add(c2)
    db.flush()

    flow = Flow(
        architecture_id=arch.id,
        source_component_id=c1.id,
        target_component_id=c2.id,
        properties={},
    )
    db.add(flow)
    db.flush()

    scenario = Scenario(
        architecture_id=arch.id,
        scenario_type="node_compromise",
        target_component_id=c1.id,
        parameters={"severity": "high"},
    )
    db.add(scenario)
    db.flush()

    result = SimulationResult(
        scenario_id=scenario.id,
        baseline_score=100.0,
        compromised_score=70.0,
        affected_components=[c1.id, c2.id],
        attack_path=["Step 1", "Step 2"],
        explanation="Propagation happened.",
    )
    db.add(result)
    db.commit()

    return {
        "architecture_id": arch.id,
        "scenario_id": scenario.id,
    }


class TestArchitectureDeleteEndpoint:

    def test_delete_architecture_returns_204(self, client, db_session):
        ids = _seed_graph_and_scenario(db_session)

        response = client.delete(f"/architectures/{ids['architecture_id']}")

        assert response.status_code == 204
        assert response.text == ""

    def test_delete_architecture_cascades_children(self, client, db_session):
        ids = _seed_graph_and_scenario(db_session)
        arch_id = ids["architecture_id"]
        scenario_id = ids["scenario_id"]

        deleted = client.delete(f"/architectures/{arch_id}")
        assert deleted.status_code == 204

        assert db_session.query(Architecture).filter(Architecture.id == arch_id).first() is None
        assert db_session.query(Component).filter(Component.architecture_id == arch_id).count() == 0
        assert db_session.query(Flow).filter(Flow.architecture_id == arch_id).count() == 0
        assert db_session.query(Scenario).filter(Scenario.architecture_id == arch_id).count() == 0
        assert (
            db_session.query(SimulationResult)
            .filter(SimulationResult.scenario_id == scenario_id)
            .count()
            == 0
        )

    def test_delete_missing_architecture_returns_404(self, client):
        response = client.delete("/architectures/999999")
        assert response.status_code == 404

    def test_openapi_documents_delete_architecture(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        path = "/architectures/{architecture_id}"
        assert path in response.json()["paths"]
        assert "delete" in response.json()["paths"][path]
