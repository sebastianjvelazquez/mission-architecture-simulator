"""Integration tests for PUT /architectures/{id} full-replace update behavior."""

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
from app.models.architecture import Architecture, Base, Component, Flow

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


def _seed_architecture(db: Session) -> int:
    arch = Architecture(name="Original Architecture", description="v1", properties={"stage": 1})
    db.add(arch)
    db.flush()

    c1 = Component(
        architecture_id=arch.id,
        component_id="old-sensor",
        name="Old Sensor",
        component_type="Sensor",
        criticality=6,
        properties={},
    )
    c2 = Component(
        architecture_id=arch.id,
        component_id="old-compute",
        name="Old Compute",
        component_type="Compute",
        criticality=7,
        properties={},
    )
    db.add(c1)
    db.add(c2)
    db.flush()

    old_flow = Flow(
        architecture_id=arch.id,
        source_component_id=c1.id,
        target_component_id=c2.id,
        properties={},
    )
    db.add(old_flow)
    db.commit()
    return arch.id


class TestArchitectureUpdateEndpoint:

    def test_put_updates_architecture_and_returns_updated_payload(self, client, db_session):
        architecture_id = _seed_architecture(db_session)

        payload = {
            "name": "Updated Architecture",
            "description": "v2",
            "components": [
                {
                    "component_id": "new-sensor",
                    "name": "New Sensor",
                    "component_type": "Sensor",
                    "criticality": 9,
                    "position_x": 10,
                    "position_y": 20,
                },
                {
                    "component_id": "new-control",
                    "name": "New Control",
                    "component_type": "Control",
                    "criticality": 10,
                    "position_x": 100,
                    "position_y": 120,
                },
            ],
            "flows": [
                {
                    "source_component_id": "new-sensor",
                    "target_component_id": "new-control",
                    "cia_requirement": "integrity",
                }
            ],
        }

        response = client.put(f"/architectures/{architecture_id}", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == architecture_id
        assert body["name"] == "Updated Architecture"
        assert body["description"] == "v2"
        assert len(body["components"]) == 2
        assert len(body["flows"]) == 1
        assert {c["component_id"] for c in body["components"]} == {"new-sensor", "new-control"}

    def test_put_full_replace_removes_old_components_and_flows(self, client, db_session):
        architecture_id = _seed_architecture(db_session)

        response = client.put(
            f"/architectures/{architecture_id}",
            json={
                "name": "Replaced",
                "description": "replace-all",
                "components": [
                    {
                        "component_id": "only-one",
                        "name": "Only One",
                        "component_type": "Sensor",
                        "criticality": 5,
                    }
                ],
                "flows": [],
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["components"]) == 1
        assert body["components"][0]["component_id"] == "only-one"
        assert len(body["flows"]) == 0

        old_components = (
            db_session.query(Component)
            .filter(
                Component.architecture_id == architecture_id,
                Component.component_id.in_(["old-sensor", "old-compute"]),
            )
            .count()
        )
        assert old_components == 0

        old_flows = db_session.query(Flow).filter(Flow.architecture_id == architecture_id).count()
        assert old_flows == 0

    def test_put_returns_404_for_missing_architecture(self, client):
        payload = {
            "name": "Missing",
            "description": "none",
            "components": [],
            "flows": [],
        }
        response = client.put("/architectures/999999", json=payload)
        assert response.status_code == 404

    def test_put_validation_error_returns_422(self, client, db_session):
        architecture_id = _seed_architecture(db_session)
        response = client.put(
            f"/architectures/{architecture_id}",
            json={
                "description": "missing name",
                "components": [],
                "flows": [],
            },
        )
        assert response.status_code == 422

    def test_put_rejects_invalid_flow_references(self, client, db_session):
        architecture_id = _seed_architecture(db_session)
        response = client.put(
            f"/architectures/{architecture_id}",
            json={
                "name": "Bad Flow",
                "description": "refs",
                "components": [
                    {
                        "component_id": "c1",
                        "name": "C1",
                        "component_type": "Sensor",
                    }
                ],
                "flows": [
                    {
                        "source_component_id": "missing",
                        "target_component_id": "c1",
                    }
                ],
            },
        )
        assert response.status_code == 422

    def test_swagger_contains_put_architecture_path(self, client):
        openapi = client.get("/openapi.json")
        assert openapi.status_code == 200
        assert "/architectures/{architecture_id}" in openapi.json()["paths"]
        assert "put" in openapi.json()["paths"]["/architectures/{architecture_id}"]
