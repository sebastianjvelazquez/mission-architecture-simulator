"""
tests/test_increment3.py

Increment 3 test suite — closes issues #90 and #92.

Covers three goals:
    1. Hit previously uncovered error-handling branches in architectures.py and
       scenarios.py to push backend coverage above 85 %.
    2. Validate Increment 3 clone and mitigation persistence behavior.
    3. Keep compare-feature placeholders (xfail) until compare endpoint lands.

Test classes
------------
TestCreateArchitectureErrors
    IntegrityError and SQLAlchemyError paths in POST /architectures when the
    payload actually contains components (the existing test_error_handling.py
    tests only use MINIMAL_PAYLOAD with no components, leaving the Component
    and Flow constructor lines uncovered).

TestUpdateArchitectureErrors
    422 validation paths (duplicate component_id, bad flow reference) and the
    IntegrityError / SQLAlchemyError handlers inside PUT /architectures/{id}.

TestListAndGetErrors
    SQLAlchemy error paths for GET /architectures and GET /architectures/{id}.

TestDeleteErrors
    The second try-block in DELETE /architectures/{id} (the commit step that
    can still raise even after the record is found).

TestScenariosApiErrors
    Error paths in the scenarios router that are not yet exercised by
    test_scenarios_api.py.

TestCloneFeature
    real tests for POST /architectures/{id}/clone deep-copy behavior.

TestMitigationFeature
    real tests for mitigation create/list/cascade behavior.

TestCompareFeaturePlaceholder
    xfail stubs for GET /architectures/compare (Increment 3 feature).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.main import app
from app.database import get_db
from app.models.architecture import Architecture, Base, Component, Flow, Mitigation

# SQLite doesn't know JSONB; reuse the JSON visitor so our ORM models work.
SQLiteTypeCompiler.visit_JSONB = SQLiteTypeCompiler.visit_JSON  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Shared in-memory SQLite database (module-scoped)
# ---------------------------------------------------------------------------

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
def db_session(db_engine):
    SessionFactory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = SessionFactory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def real_client(db_session: Session):
    """TestClient backed by a real in-memory SQLite DB."""
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Mock-DB helpers (mirror test_error_handling.py style)
# ---------------------------------------------------------------------------

def _mock_db(*, query_exc=None, flush_exc=None, commit_exc=None, delete_exc=None) -> MagicMock:
    db = MagicMock(spec=Session)
    if query_exc is not None:
        db.query.side_effect = query_exc
    if flush_exc is not None:
        db.flush.side_effect = flush_exc
    if commit_exc is not None:
        db.commit.side_effect = commit_exc
    if delete_exc is not None:
        db.delete.side_effect = delete_exc
    return db


def _override(mock_session: MagicMock):
    def _get_db_override():
        yield mock_session
    return _get_db_override


def _make_integrity_error(msg: str = "UNIQUE constraint failed") -> IntegrityError:
    return IntegrityError("stmt", {}, Exception(msg))


def _make_sqlalchemy_error() -> SQLAlchemyError:
    return OperationalError("stmt", {}, Exception("connection refused"))


@pytest.fixture
def mock_client():
    """TestClient that does NOT suppress server exceptions (so we can inspect them)."""
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Payload helpers
# ---------------------------------------------------------------------------

WITH_COMPONENTS = {
    "name": "Test Arch With Components",
    "components": [
        {"component_id": "c1", "name": "Sensor A", "component_type": "Sensor"},
        {"component_id": "c2", "name": "Compute B", "component_type": "Compute"},
    ],
    "flows": [
        {"source_component_id": "c1", "target_component_id": "c2"},
    ],
}

MINIMAL_PAYLOAD = {"name": "Minimal Arch", "components": [], "flows": []}


def _create_arch(client) -> int:
    """Create a real architecture and return its id."""
    r = client.post("/architectures", json=WITH_COMPONENTS)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _create_arch_and_component(client) -> tuple[int, int]:
    """Create a real architecture and return (arch_id, first_component_db_id)."""
    r = client.post("/architectures", json=WITH_COMPONENTS)
    assert r.status_code == 201, r.text
    data = r.json()
    return data["id"], data["components"][0]["id"]


# ===========================================================================
# 1. CREATE architecture — error paths with components present
# ===========================================================================

class TestCreateArchitectureErrors:
    """
    The existing test_error_handling.py uses MINIMAL_PAYLOAD (no components),
    so the Component-constructor and Flow-constructor lines inside the for-loops
    are never executed.  These tests supply real components and trigger errors
    during the component flush to cover those lines.
    """

    def test_integrity_error_during_component_flush_returns_409(self, mock_client):
        # Raise IntegrityError on the second flush() call (the component flush).
        flush_calls = [None, _make_integrity_error("UNIQUE constraint failed")]
        db = MagicMock(spec=Session)
        db.flush.side_effect = flush_calls
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post("/architectures", json=WITH_COMPONENTS)
            assert r.status_code == 409
            assert "already exists" in r.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_sqlalchemy_error_during_component_flush_returns_500(self, mock_client):
        flush_calls = [None, _make_sqlalchemy_error()]
        db = MagicMock(spec=Session)
        db.flush.side_effect = flush_calls
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post("/architectures", json=WITH_COMPONENTS)
            assert r.status_code == 500
            assert "Database error" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_rollback_called_on_component_integrity_error(self, mock_client):
        flush_calls = [None, _make_integrity_error("UNIQUE constraint failed")]
        db = MagicMock(spec=Session)
        db.flush.side_effect = flush_calls
        app.dependency_overrides[get_db] = _override(db)
        try:
            mock_client.post("/architectures", json=WITH_COMPONENTS)
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_sqlalchemy_error_on_commit_returns_500(self, mock_client):
        db = _mock_db(commit_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)


# ===========================================================================
# 2. UPDATE architecture — validation + error paths
# ===========================================================================

class TestUpdateArchitectureErrors:
    """
    PUT /architectures/{id} has its own duplicate-component-id and
    bad-flow-reference validation that mirrors the POST validation but
    runs AFTER the 404 check.  These are distinct code paths that need
    separate tests.
    """

    def test_update_nonexistent_architecture_returns_404(self, real_client):
        r = real_client.put("/architectures/99999", json=WITH_COMPONENTS)
        assert r.status_code == 404

    def test_update_duplicate_component_id_returns_422(self, real_client):
        arch_id = _create_arch(real_client)
        payload = {
            "name": "Dup Update",
            "components": [
                {"component_id": "same", "name": "A", "component_type": "Sensor"},
                {"component_id": "same", "name": "B", "component_type": "Compute"},
            ],
            "flows": [],
        }
        r = real_client.put(f"/architectures/{arch_id}", json=payload)
        assert r.status_code == 422
        assert "Duplicate" in r.json()["detail"]

    def test_update_flow_source_not_in_components_returns_422(self, real_client):
        arch_id = _create_arch(real_client)
        payload = {
            "name": "Bad Flow Update",
            "components": [
                {"component_id": "c1", "name": "Sensor", "component_type": "Sensor"},
            ],
            "flows": [{"source_component_id": "GHOST", "target_component_id": "c1"}],
        }
        r = real_client.put(f"/architectures/{arch_id}", json=payload)
        assert r.status_code == 422
        assert "GHOST" in r.json()["detail"]

    def test_update_flow_target_not_in_components_returns_422(self, real_client):
        arch_id = _create_arch(real_client)
        payload = {
            "name": "Bad Flow Target Update",
            "components": [
                {"component_id": "c1", "name": "Sensor", "component_type": "Sensor"},
            ],
            "flows": [{"source_component_id": "c1", "target_component_id": "GHOST"}],
        }
        r = real_client.put(f"/architectures/{arch_id}", json=payload)
        assert r.status_code == 422
        assert "GHOST" in r.json()["detail"]

    def test_update_successful_replaces_components(self, real_client):
        arch_id = _create_arch(real_client)
        new_payload = {
            "name": "Updated Arch",
            "description": "Updated description",
            "components": [
                {"component_id": "n1", "name": "New Node", "component_type": "Control"},
            ],
            "flows": [],
        }
        r = real_client.put(f"/architectures/{arch_id}", json=new_payload)
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Updated Arch"
        assert len(data["components"]) == 1
        assert data["components"][0]["component_id"] == "n1"

    def test_update_integrity_error_returns_409(self, mock_client):
        """Trigger IntegrityError inside the update try-block."""
        db = MagicMock(spec=Session)
        # First query() call returns a mock arch; subsequent calls raise.
        mock_arch = MagicMock(spec=Architecture)
        mock_arch.id = 1
        mock_arch.flows = []
        mock_arch.components = []
        db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_arch
        db.flush.side_effect = _make_integrity_error("UNIQUE constraint failed")
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.put("/architectures/1", json=WITH_COMPONENTS)
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_update_sqlalchemy_error_returns_500(self, mock_client):
        db = MagicMock(spec=Session)
        mock_arch = MagicMock(spec=Architecture)
        mock_arch.id = 1
        mock_arch.flows = []
        mock_arch.components = []
        db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_arch
        db.flush.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.put("/architectures/1", json=MINIMAL_PAYLOAD)
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)


# ===========================================================================
# 3. LIST and GET — SQLAlchemy error paths
# ===========================================================================

class TestListAndGetErrors:

    def test_list_sqlalchemy_error_returns_500(self, mock_client):
        db = _mock_db(query_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.get("/architectures")
            assert r.status_code == 500
            assert "Database error" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_get_sqlalchemy_error_returns_500(self, mock_client):
        db = _mock_db(query_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.get("/architectures/1")
            assert r.status_code == 500
            assert "Database error" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_get_nonexistent_architecture_returns_404(self, real_client):
        r = real_client.get("/architectures/99999")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_list_with_skip_and_limit(self, real_client):
        r = real_client.get("/architectures?skip=0&limit=5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_invalid_skip_returns_422(self, real_client):
        r = real_client.get("/architectures?skip=-1")
        assert r.status_code == 422

    def test_list_invalid_limit_returns_422(self, real_client):
        r = real_client.get("/architectures?limit=0")
        assert r.status_code == 422


# ===========================================================================
# 4. DELETE — error paths
# ===========================================================================

class TestDeleteErrors:

    def test_delete_nonexistent_returns_404(self, real_client):
        r = real_client.delete("/architectures/99999")
        assert r.status_code == 404

    def test_delete_sqlalchemy_error_on_query_returns_500(self, mock_client):
        db = _mock_db(query_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.delete("/architectures/1")
            assert r.status_code == 500
            assert "Database error" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_delete_sqlalchemy_error_on_commit_returns_500(self, mock_client):
        """Hit the second try-block in delete_architecture (the db.commit() path)."""
        db = MagicMock(spec=Session)
        mock_arch = MagicMock(spec=Architecture)
        mock_arch.id = 1
        db.query.return_value.filter.return_value.first.return_value = mock_arch
        db.commit.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.delete("/architectures/1")
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_delete_successful_returns_204(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.delete(f"/architectures/{arch_id}")
        assert r.status_code == 204
        # Confirm gone
        r2 = real_client.get(f"/architectures/{arch_id}")
        assert r2.status_code == 404


# ===========================================================================
# 5. Scenarios API — additional error coverage
# ===========================================================================

class TestScenariosApiErrors:
    """Cover error branches in app/api/scenarios.py not hit by test_scenarios_api.py."""

    def test_get_scenarios_for_nonexistent_architecture_returns_404(self, real_client):
        r = real_client.get("/architectures/99999/scenarios")
        assert r.status_code == 404

    def test_create_scenario_for_nonexistent_architecture_returns_404(self, real_client):
        # target_component_id must be an int (DB id) — use 1 so pydantic validation passes.
        # The architecture 99999 does not exist, so the handler returns 404.
        payload = {
            "scenario_type": "node_compromise",
            "target_component_id": 1,
        }
        r = real_client.post("/architectures/99999/scenarios", json=payload)
        assert r.status_code == 404

    def test_create_scenario_invalid_type_returns_422(self, real_client):
        arch_id, component_db_id = _create_arch_and_component(real_client)
        payload = {
            "scenario_type": "invalid_attack_type",
            "target_component_id": component_db_id,
        }
        r = real_client.post(f"/architectures/{arch_id}/scenarios", json=payload)
        assert r.status_code == 422

    def test_create_scenario_with_link_degradation_type(self, real_client):
        arch_id, component_db_id = _create_arch_and_component(real_client)
        payload = {
            "scenario_type": "link_degradation",
            "target_component_id": component_db_id,
            "parameters": {"packet_loss_percent": 10},
        }
        r = real_client.post(f"/architectures/{arch_id}/scenarios", json=payload)
        # link_degradation is a valid type for storage even though the simulator
        # doesn't run it yet
        assert r.status_code == 201
        assert r.json()["scenario_type"] == "link_degradation"

    def test_create_scenario_with_insider_tampering_type(self, real_client):
        arch_id, component_db_id = _create_arch_and_component(real_client)
        payload = {
            "scenario_type": "insider_tampering",
            "target_component_id": component_db_id,
        }
        r = real_client.post(f"/architectures/{arch_id}/scenarios", json=payload)
        assert r.status_code == 201
        assert r.json()["scenario_type"] == "insider_tampering"

    def test_delete_scenario_returns_204(self, real_client):
        arch_id, component_db_id = _create_arch_and_component(real_client)
        create_r = real_client.post(
            f"/architectures/{arch_id}/scenarios",
            json={
                "scenario_type": "node_compromise",
                "target_component_id": component_db_id,
            },
        )
        assert create_r.status_code == 201
        scenario_id = create_r.json()["id"]
        del_r = real_client.delete(f"/architectures/{arch_id}/scenarios/{scenario_id}")
        assert del_r.status_code == 204

    def test_delete_nonexistent_scenario_returns_404(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.delete(f"/architectures/{arch_id}/scenarios/99999")
        assert r.status_code == 404

    def test_create_scenario_for_nonexistent_component_returns_422(self, real_client):
        arch_id = _create_arch(real_client)
        payload = {
            "scenario_type": "node_compromise",
            "target_component_id": 999999,  # Does not belong to this arch
        }
        r = real_client.post(f"/architectures/{arch_id}/scenarios", json=payload)
        assert r.status_code == 422


# ===========================================================================
# 6. Simulator — edge cases not yet covered
# ===========================================================================

class TestSimulatorEdgeCases:
    """Additional simulator unit tests to cover remaining uncovered lines."""

    def test_propagate_compromise_unknown_node_returns_empty_set(self):
        from app.models.schemas import ArchitectureSchema, ComponentSchema, DataFlowSchema
        from app.services.simulator import MissionArchitectureSimulator

        arch = ArchitectureSchema(
            id=1,
            name="Test",
            components=[
                ComponentSchema(id="a", name="A", type="Sensor", criticality=5, position={"x": 0, "y": 0}),
            ],
            flows=[],
        )
        sim = MissionArchitectureSimulator(arch)
        result = sim.propagate_compromise("nonexistent-node")
        assert result == set()

    def test_get_component_metadata_unknown_raises(self):
        from app.models.schemas import ArchitectureSchema, ComponentSchema
        from app.services.simulator import MissionArchitectureSimulator, SimulatorError

        arch = ArchitectureSchema(
            id=1,
            name="Test",
            components=[
                ComponentSchema(id="a", name="A", type="Sensor", criticality=5, position={"x": 0, "y": 0}),
            ],
            flows=[],
        )
        sim = MissionArchitectureSimulator(arch)
        with pytest.raises(SimulatorError, match="not found"):
            sim.get_component_metadata("ghost")

    def test_run_simulation_unimplemented_scenario_raises(self):
        """The unreachable raise at the end of run_simulation should be covered
        if we bypass the SUPPORTED_SCENARIOS guard via monkeypatching."""
        from app.models.schemas import ArchitectureSchema, ComponentSchema
        from app.services.simulator import (
            MissionArchitectureSimulator,
            SimulatorError,
            SUPPORTED_SCENARIOS,
        )

        arch = ArchitectureSchema(
            id=1,
            name="Test",
            components=[
                ComponentSchema(id="a", name="A", type="Sensor", criticality=5, position={"x": 0, "y": 0}),
            ],
            flows=[],
        )
        sim = MissionArchitectureSimulator(arch)

        # Temporarily expand SUPPORTED_SCENARIOS so the guard passes,
        # then let the dispatch fall through to the unreachable raise.
        # Must patch the name as used *inside* the module that runs the check.
        with patch(
            "app.core.simulator.SUPPORTED_SCENARIOS",
            frozenset({"node_compromise", "ghost_scenario"}),
        ):
            with pytest.raises(SimulatorError):
                sim.run_simulation("ghost_scenario", "a")

    def test_calculate_mission_score_with_all_nodes_affected(self):
        from app.models.schemas import ArchitectureSchema, ComponentSchema
        from app.services.simulator import MissionArchitectureSimulator

        arch = ArchitectureSchema(
            id=1,
            name="Test",
            components=[
                ComponentSchema(id="a", name="A", type="Sensor", criticality=5, position={"x": 0, "y": 0}),
                ComponentSchema(id="b", name="B", type="Compute", criticality=5, position={"x": 0, "y": 0}),
            ],
            flows=[],
        )
        sim = MissionArchitectureSimulator(arch)
        score = sim.calculate_mission_score({"a", "b"})
        assert score == 0.0

    def test_calculate_mission_score_healthy_clamped_when_extra_ids_given(self):
        from app.models.schemas import ArchitectureSchema, ComponentSchema
        from app.services.simulator import MissionArchitectureSimulator

        arch = ArchitectureSchema(
            id=1,
            name="Test",
            components=[
                ComponentSchema(id="a", name="A", type="Sensor", criticality=5, position={"x": 0, "y": 0}),
            ],
            flows=[],
        )
        sim = MissionArchitectureSimulator(arch)
        # Passing more affected IDs than nodes in graph — should clamp to 0
        score = sim.calculate_mission_score({"a", "b", "c", "d", "e"})
        assert score == 0.0


# ===========================================================================
# 7. Compare Feature Placeholders (xfail until compare endpoint is implemented)
# ===========================================================================

class TestCloneFeature:

    def test_clone_creates_copy_with_new_id(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.post(f"/architectures/{arch_id}/clone")
        assert r.status_code == 201
        data = r.json()
        assert data["id"] != arch_id
        assert data["is_clone"] is True
        assert data["parent_id"] == arch_id
        assert "Clone" in data["name"]

    def test_clone_copies_all_components(self, real_client):
        arch_id = _create_arch(real_client)

        original = real_client.get(f"/architectures/{arch_id}")
        assert original.status_code == 200
        original_data = original.json()

        r = real_client.post(f"/architectures/{arch_id}/clone")
        assert r.status_code == 201
        data = r.json()
        assert len(data["components"]) == len(original_data["components"])
        assert len(data["flows"]) == len(original_data["flows"])

        original_component_ids = {c["id"] for c in original_data["components"]}
        cloned_component_ids = {c["id"] for c in data["components"]}
        assert original_component_ids.isdisjoint(cloned_component_ids)

        cloned_component_lookup = {c["id"] for c in data["components"]}
        for flow in data["flows"]:
            assert flow["source_component_id"] in cloned_component_lookup
            assert flow["target_component_id"] in cloned_component_lookup

    def test_clone_nonexistent_architecture_returns_404(self, real_client):
        r = real_client.post("/architectures/99999/clone")
        assert r.status_code == 404


class TestMitigationFeature:

    def test_get_mitigations_returns_list(self, real_client):
        arch_id = _create_arch(real_client)

        create_r = real_client.post(
            f"/architectures/{arch_id}/mitigations",
            json={
                "type": "network-segmentation",
                "description": "Segment sensor and control planes.",
            },
        )
        assert create_r.status_code == 201

        r = real_client.get(f"/architectures/{arch_id}/mitigations")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_mitigation_suggestion_has_required_fields(self, real_client):
        arch_id, component_id = _create_arch_and_component(real_client)
        create_r = real_client.post(
            f"/architectures/{arch_id}/mitigations",
            json={
                "type": "hardening",
                "affected_component_id": component_id,
                "description": "Enable signed firmware updates.",
            },
        )
        assert create_r.status_code == 201

        r = real_client.get(f"/architectures/{arch_id}/mitigations")
        assert r.status_code == 200
        if r.json():  # If any suggestions are returned
            suggestion = r.json()[0]
            assert "type" in suggestion
            assert "affected_component_id" in suggestion
            assert "description" in suggestion

    def test_get_mitigations_nonexistent_architecture_returns_404(self, real_client):
        r = real_client.get("/architectures/99999/mitigations")
        assert r.status_code == 404

    def test_delete_architecture_cascades_mitigations(self, real_client, db_session):
        arch_id, component_id = _create_arch_and_component(real_client)
        create_r = real_client.post(
            f"/architectures/{arch_id}/mitigations",
            json={
                "type": "encryption",
                "affected_component_id": component_id,
                "description": "Use mTLS between compute and storage components.",
            },
        )
        assert create_r.status_code == 201

        assert db_session.query(Mitigation).filter(Mitigation.architecture_id == arch_id).count() == 1

        delete_r = real_client.delete(f"/architectures/{arch_id}")
        assert delete_r.status_code == 204

        assert db_session.query(Mitigation).filter(Mitigation.architecture_id == arch_id).count() == 0


# ===========================================================================
# 8. Clone endpoint — error paths
# ===========================================================================

class TestCloneErrors:
    """Cover error branches added by the team in clone_architecture."""

    def test_clone_sqlalchemy_error_on_query_returns_500(self, mock_client):
        """First try-block in clone_architecture: db.query raises SQLAlchemyError."""
        db = _mock_db(query_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post("/architectures/1/clone")
            assert r.status_code == 500
            assert "Database error" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_clone_sqlalchemy_error_on_commit_returns_500(self, mock_client):
        """Second try-block in clone_architecture: commit raises SQLAlchemyError."""
        db = MagicMock(spec=Session)
        mock_source = MagicMock(spec=Architecture)
        mock_source.id = 1
        mock_source.name = "Original"
        mock_source.description = None
        mock_source.properties = {}
        mock_source.components = []
        mock_source.flows = []
        db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_source
        db.commit.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post("/architectures/1/clone")
            assert r.status_code == 500
            assert "Database error" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_clone_integrity_error_on_commit_returns_409(self, mock_client):
        """Second try-block in clone_architecture: commit raises IntegrityError."""
        db = MagicMock(spec=Session)
        mock_source = MagicMock(spec=Architecture)
        mock_source.id = 1
        mock_source.name = "Original"
        mock_source.description = None
        mock_source.properties = {}
        mock_source.components = []
        mock_source.flows = []
        db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_source
        db.commit.side_effect = _make_integrity_error("UNIQUE constraint failed")
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post("/architectures/1/clone")
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)


# ===========================================================================
# 9. Mitigation endpoint — error paths
# ===========================================================================

class TestMitigationErrors:
    """Cover error branches in create_mitigation and list_mitigations."""

    def test_create_mitigation_nonexistent_arch_returns_404(self, real_client):
        r = real_client.post(
            "/architectures/99999/mitigations",
            json={"type": "hardening", "description": "test"},
        )
        assert r.status_code == 404

    def test_create_mitigation_nonexistent_component_returns_422(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.post(
            f"/architectures/{arch_id}/mitigations",
            json={
                "type": "hardening",
                "affected_component_id": 999999,
                "description": "Bad component id",
            },
        )
        assert r.status_code == 422
        assert "does not belong" in r.json()["detail"]

    def test_create_mitigation_sqlalchemy_error_returns_500(self, mock_client):
        db = _mock_db(query_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post(
                "/architectures/1/mitigations",
                json={"type": "hardening", "description": "test"},
            )
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_create_mitigation_integrity_error_on_commit_returns_409(self, mock_client):
        """Trigger IntegrityError inside create_mitigation's except IntegrityError block."""
        db = _mock_db(commit_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.post(
                "/architectures/1/mitigations",
                json={"type": "hardening", "description": "test"},
            )
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_list_mitigations_sqlalchemy_error_returns_500(self, mock_client):
        db = _mock_db(query_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.get("/architectures/1/mitigations")
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_create_mitigation_without_component_id_succeeds(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.post(
            f"/architectures/{arch_id}/mitigations",
            json={"type": "network-segmentation", "description": "Segment the network."},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["type"] == "network-segmentation"
        assert data["affected_component_id"] is None


# ===========================================================================
# 10. Health DB endpoint
# ===========================================================================

class TestHealthDbEndpoint:
    """Cover the /health/db endpoint including the 503 unreachable path."""

    def test_health_db_connected_returns_200(self):
        from app.database import check_connection

        with patch("app.core.main.check_connection", return_value=True):
            client = TestClient(app)
            r = client.get("/health/db")
        assert r.status_code == 200
        assert r.json()["status"] == "connected"

    def test_health_db_unreachable_returns_503(self):
        with patch("app.core.main.check_connection", return_value=False):
            client = TestClient(app)
            r = client.get("/health/db")
        assert r.status_code == 503
        assert r.json()["status"] == "unreachable"


class TestCompareFeaturePlaceholder:
    """
    Tests for GET /architectures/compare?baseline_id={id}&mitigated_id={id}.

    Implemented in issue #84 (Compare Scenarios & Mitigation Scoring Logic).
    """

    def test_compare_returns_delta_score(self, real_client):
        arch_id_1 = _create_arch(real_client)
        arch_id_2 = _create_arch(real_client)
        r = real_client.get(
            f"/architectures/compare?baseline_id={arch_id_1}&mitigated_id={arch_id_2}"
        )
        assert r.status_code == 200
        data = r.json()
        assert "delta_mission_score" in data or "score_delta" in data

    def test_compare_with_nonexistent_baseline_returns_404(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.get(f"/architectures/compare?baseline_id=99999&mitigated_id={arch_id}")
        assert r.status_code == 404

    def test_compare_same_architecture_returns_zero_delta(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.get(
            f"/architectures/compare?baseline_id={arch_id}&mitigated_id={arch_id}"
        )
        assert r.status_code == 200
        data = r.json()
        delta = data.get("delta_mission_score") or data.get("score_delta", None)
        assert delta == 0 or delta is None

    def test_compare_mitigated_not_found_returns_404(self, real_client):
        arch_id = _create_arch(real_client)
        r = real_client.get(f"/architectures/compare?baseline_id={arch_id}&mitigated_id=99999")
        assert r.status_code == 404

    def test_compare_returns_all_expected_fields(self, real_client):
        arch_id_1 = _create_arch(real_client)
        arch_id_2 = _create_arch(real_client)
        r = real_client.get(
            f"/architectures/compare?baseline_id={arch_id_1}&mitigated_id={arch_id_2}"
        )
        assert r.status_code == 200
        data = r.json()
        assert "baseline_id" in data
        assert "mitigated_id" in data
        assert "baseline_score" in data
        assert "mitigated_score" in data
        assert "delta_mission_score" in data
        assert "score_delta" in data
        assert "baseline_component_count" in data
        assert "mitigated_component_count" in data
        assert "summary" in data
        assert isinstance(data["summary"], str)
        assert data["baseline_id"] == arch_id_1
        assert data["mitigated_id"] == arch_id_2

    def test_compare_sqlalchemy_error_on_baseline_returns_500(self, mock_client):
        db = MagicMock(spec=Session)
        db.query.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = mock_client.get("/architectures/compare?baseline_id=1&mitigated_id=2")
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

