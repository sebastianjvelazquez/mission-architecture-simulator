"""Integration tests for scenario and simulation-result persistence endpoints."""

from __future__ import annotations

import csv
import io
import json
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


class TestScenarioEndpoints:

    def test_create_and_list_scenarios(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)

        create_payload = {
            "scenario_type": "node_compromise",
            "target_component_id": target_id,
            "parameters": {"severity": "high", "retries": 2},
        }
        created = client.post(f"/architectures/{architecture_id}/scenarios", json=create_payload)

        assert created.status_code == 201
        created_body = created.json()
        assert created_body["architecture_id"] == architecture_id
        assert created_body["target_component_id"] == target_id
        assert created_body["scenario_type"] == "node_compromise"
        assert created_body["parameters"]["severity"] == "high"

        listed = client.get(f"/architectures/{architecture_id}/scenarios")
        assert listed.status_code == 200
        assert any(item["id"] == created_body["id"] for item in listed.json())

    def test_create_scenario_with_component_from_another_architecture_returns_422(
        self,
        client,
        db_session,
    ):
        architecture_id_a, _, _ = _seed_architecture(db_session)
        architecture_id_b, target_id_b, _ = _seed_architecture(db_session)

        payload = {
            "scenario_type": "node_compromise",
            "target_component_id": target_id_b,
            "parameters": {},
        }

        response = client.post(f"/architectures/{architecture_id_a}/scenarios", json=payload)
        assert response.status_code == 422
        assert str(architecture_id_a) in response.json()["detail"]
        assert architecture_id_a != architecture_id_b

    def test_delete_scenario_cascades_to_simulation_results(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)

        scenario = client.post(
            f"/architectures/{architecture_id}/scenarios",
            json={
                "scenario_type": "insider_tampering",
                "target_component_id": target_id,
                "parameters": {"operator": "insider"},
            },
        )
        scenario_id = scenario.json()["id"]

        result = client.post(
            f"/scenarios/{scenario_id}/results",
            json={
                "baseline_score": 100.0,
                "compromised_score": 62.5,
                "affected_components": [target_id],
                "attack_path": ["Step 1: Target modified"],
                "explanation": "Insider modified mission data path.",
            },
        )
        assert result.status_code == 201
        assert (
            db_session.query(SimulationResult)
            .filter(SimulationResult.scenario_id == scenario_id)
            .count()
            == 1
        )

        deleted = client.delete(f"/architectures/{architecture_id}/scenarios/{scenario_id}")
        assert deleted.status_code == 204

        assert db_session.query(Scenario).filter(Scenario.id == scenario_id).first() is None
        assert (
            db_session.query(SimulationResult)
            .filter(SimulationResult.scenario_id == scenario_id)
            .count()
            == 0
        )


class TestSimulationResultEndpoints:

    def test_create_and_list_results(self, client, db_session):
        architecture_id, target_id, _ = _seed_architecture(db_session)

        scenario_resp = client.post(
            f"/architectures/{architecture_id}/scenarios",
            json={
                "scenario_type": "link_degradation",
                "target_component_id": target_id,
                "parameters": {"packet_loss_percent": 35},
            },
        )
        scenario_id = scenario_resp.json()["id"]

        create_result = client.post(
            f"/scenarios/{scenario_id}/results",
            json={
                "baseline_score": 100.0,
                "compromised_score": 80.0,
                "affected_components": [target_id],
                "attack_path": [
                    "Step 1: Link degraded",
                    "Step 2: Downstream performance drops",
                ],
                "explanation": "Link degradation reduced mission performance.",
            },
        )

        assert create_result.status_code == 201
        body = create_result.json()
        assert body["scenario_id"] == scenario_id
        assert body["baseline_score"] == 100.0
        assert body["compromised_score"] == 80.0
        assert body["affected_components"] == [target_id]

        listed = client.get(f"/scenarios/{scenario_id}/results")
        assert listed.status_code == 200
        assert any(item["id"] == body["id"] for item in listed.json())

    def test_create_result_for_missing_scenario_returns_404(self, client):
        response = client.post(
            "/scenarios/999999/results",
            json={
                "baseline_score": 100.0,
                "compromised_score": 70.0,
                "affected_components": [1, 2],
                "attack_path": ["Step 1: Attack starts"],
                "explanation": "Scenario not found.",
            },
        )
        assert response.status_code == 404


class TestScenarioExportEndpoints:

    def _seed_scenario_with_result(self, client, db_session) -> int:
        architecture_id, target_id, _ = _seed_architecture(db_session)
        scenario_resp = client.post(
            f"/architectures/{architecture_id}/scenarios",
            json={
                "scenario_type": "node_compromise",
                "target_component_id": target_id,
                "parameters": {"severity": "high"},
            },
        )
        assert scenario_resp.status_code == 201
        scenario_id = scenario_resp.json()["id"]

        result_resp = client.post(
            f"/scenarios/{scenario_id}/results",
            json={
                "baseline_score": 100.0,
                "compromised_score": 75.0,
                "affected_components": [target_id],
                "attack_path": ["Step 1: target compromised"],
                "explanation": "Export test result.",
            },
        )
        assert result_resp.status_code == 201
        return scenario_id

    def test_export_json_download_contains_full_scenario_and_results(self, client, db_session):
        scenario_id = self._seed_scenario_with_result(client, db_session)

        response = client.get(f"/scenarios/{scenario_id}/export?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        assert "attachment; filename=scenario_" in response.headers["content-disposition"]

        payload = json.loads(response.text)
        assert payload["id"] == scenario_id
        assert payload["scenario_type"] == "node_compromise"
        assert "parameters" in payload
        assert len(payload["results"]) == 1
        assert payload["results"][0]["baseline_score"] == 100.0

    def test_export_csv_download_contains_flat_rows_with_scores(self, client, db_session):
        scenario_id = self._seed_scenario_with_result(client, db_session)

        response = client.get(f"/scenarios/{scenario_id}/export?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment; filename=scenario_" in response.headers["content-disposition"]

        reader = csv.DictReader(io.StringIO(response.text))
        rows = list(reader)
        assert len(rows) >= 1
        assert rows[0]["scenario_id"] == str(scenario_id)
        assert rows[0]["baseline_score"] == "100.0"
        assert rows[0]["compromised_score"] == "75.0"
