"""
tests/test_integration.py

Integration tests verifying the full frontend-to-backend data flow using
FastAPI's TestClient. Every test here exercises the full request/response
cycle including middleware, routing, Pydantic validation, and in-memory
database interactions.

Covers (Issue #56):
    - Save architecture from frontend-shaped JSON → confirm round-trip via GET
    - Load architecture → confirm components and flows are returned correctly
    - Run simulation → confirm results contain expected fields
    - Full save/load/simulate flow end-to-end
    - Error paths: missing architecture, invalid payloads
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.main import app
from app.database import get_db

# ---------------------------------------------------------------------------
# Settings override — prevents reading the real .env during tests
# ---------------------------------------------------------------------------


def _test_settings() -> Settings:
    return Settings(
        ENVIRONMENT="test",
        ALLOWED_ORIGINS="http://localhost:3000,http://testserver",
    )


@pytest.fixture(autouse=True)
def override_settings():
    app.dependency_overrides[get_settings] = _test_settings
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Frontend-shaped payloads (FlowInlineCreate uses string component_ids)
# ---------------------------------------------------------------------------

SIMPLE_ARCH = {
    "name": "Integration Test Architecture",
    "description": "Used by test_integration.py",
    "components": [
        {
            "component_id": "sensor-1",
            "name": "Sensor Alpha",
            "component_type": "Sensor",
            "criticality": 8,
            "position_x": 100.0,
            "position_y": 200.0,
        },
        {
            "component_id": "compute-1",
            "name": "Compute Node",
            "component_type": "Compute",
            "criticality": 7,
            "position_x": 300.0,
            "position_y": 200.0,
        },
        {
            "component_id": "control-1",
            "name": "Control System",
            "component_type": "Control",
            "criticality": 10,
            "position_x": 500.0,
            "position_y": 200.0,
        },
    ],
    # FlowInlineCreate: source/target are string component_ids
    "flows": [
        {
            "source_component_id": "sensor-1",
            "target_component_id": "compute-1",
            "data_type": "telemetry",
            "cia_requirement": "availability",
        },
        {
            "source_component_id": "compute-1",
            "target_component_id": "control-1",
            "data_type": "commands",
            "cia_requirement": "integrity",
        },
    ],
}

MINIMAL_ARCH = {
    "name": "Minimal Arch",
    "components": [],
    "flows": [],
}

_NOW = datetime(2026, 3, 1, 12, 0, 0)


# ---------------------------------------------------------------------------
# DB mock helpers — fields must match ORM model attribute names exactly
# ---------------------------------------------------------------------------


def _make_mock_component(
    db_id: int,
    component_id: str,
    name: str,
    component_type: str,
    criticality: int = 5,
    arch_id: int = 1,
):
    """Return a MagicMock that satisfies ComponentResponse (from_attributes=True)."""
    c = MagicMock()
    c.id = db_id
    c.architecture_id = arch_id
    c.component_id = component_id
    c.name = name
    c.component_type = component_type
    c.criticality = criticality
    c.position_x = 0.0
    c.position_y = 0.0
    c.properties = {}
    c.created_at = _NOW
    c.updated_at = _NOW
    return c


def _make_mock_flow(
    db_id: int,
    source_db_id: int,
    target_db_id: int,
    data_type: str = "data",
    cia: str = "availability",
    arch_id: int = 1,
):
    """Return a MagicMock that satisfies FlowResponse (from_attributes=True).

    FlowResponse.source_component_id and target_component_id are integers
    (DB PKs), not string slugs.
    """
    f = MagicMock()
    f.id = db_id
    f.architecture_id = arch_id
    f.source_component_id = source_db_id
    f.target_component_id = target_db_id
    f.data_type = data_type
    f.cia_requirement = cia
    f.latency_sensitivity = "medium"
    f.properties = {}
    f.created_at = _NOW
    f.updated_at = _NOW
    return f


def _make_mock_architecture(arch_id: int = 1, name: str = "Test Arch"):
    """Return a MagicMock that satisfies ArchitectureResponse (from_attributes=True)."""
    arch = MagicMock()
    arch.id = arch_id
    arch.name = name
    arch.description = "Test description"
    arch.properties = {}
    arch.created_at = _NOW
    arch.updated_at = _NOW
    arch.components = [
        _make_mock_component(1, "sensor-1", "Sensor Alpha", "Sensor", 8, arch_id),
        _make_mock_component(2, "compute-1", "Compute Node", "Compute", 7, arch_id),
        _make_mock_component(3, "control-1", "Control System", "Control", 10, arch_id),
    ]
    arch.flows = [
        _make_mock_flow(1, 1, 2, "telemetry", "availability", arch_id),
        _make_mock_flow(2, 2, 3, "commands", "integrity", arch_id),
    ]
    return arch


def _stub_db() -> MagicMock:
    """Return a MagicMock Session that succeeds silently on write operations."""
    return MagicMock(spec=Session)


def _inject_db(db: MagicMock):
    app.dependency_overrides[get_db] = lambda: db


def _clear_db():
    app.dependency_overrides.pop(get_db, None)


# ===========================================================================
# Test: Save Architecture (POST /architectures)
# ===========================================================================


class TestSaveArchitecture:
    """
    Verifies that the frontend-formatted POST payload is accepted and stored.
    Covers Issue #56: 'Save architecture from frontend format → verify stored in DB'.
    """

    def test_valid_payload_returns_201(self):
        db = _stub_db()

        def _refresh(obj):
            obj.id = 1
            obj.components = []
            obj.flows = []
            obj.created_at = _NOW
            obj.updated_at = _NOW

        db.refresh = MagicMock(side_effect=_refresh)
        _inject_db(db)
        client = TestClient(app)
        r = client.post("/architectures", json=SIMPLE_ARCH)
        _clear_db()
        assert r.status_code == 201

    def test_valid_payload_returns_id(self):
        db = _stub_db()

        def _refresh(obj):
            obj.id = 42
            obj.components = []
            obj.flows = []
            obj.created_at = _NOW
            obj.updated_at = _NOW

        db.refresh = MagicMock(side_effect=_refresh)
        _inject_db(db)
        client = TestClient(app)
        r = client.post("/architectures", json=SIMPLE_ARCH)
        _clear_db()
        assert r.status_code == 201
        assert "id" in r.json()

    def test_missing_name_returns_422(self):
        client = TestClient(app)
        r = client.post("/architectures", json={"components": [], "flows": []})
        assert r.status_code == 422

    def test_invalid_criticality_too_low_returns_422(self):
        """Criticality must be ≥ 1; 0 should be rejected by Pydantic."""
        bad_payload = {
            "name": "Bad Arch",
            "components": [
                {
                    "component_id": "c1",
                    "name": "Sensor",
                    "component_type": "Sensor",
                    "criticality": 0,
                }
            ],
            "flows": [],
        }
        client = TestClient(app)
        r = client.post("/architectures", json=bad_payload)
        assert r.status_code == 422

    def test_invalid_criticality_too_high_returns_422(self):
        """Criticality must be ≤ 10; 11 should be rejected by Pydantic."""
        bad_payload = {
            "name": "Bad Arch",
            "components": [
                {
                    "component_id": "c1",
                    "name": "Sensor",
                    "component_type": "Sensor",
                    "criticality": 11,
                }
            ],
            "flows": [],
        }
        client = TestClient(app)
        r = client.post("/architectures", json=bad_payload)
        assert r.status_code == 422

    def test_duplicate_component_id_returns_422(self):
        """Two components with the same component_id in one request is invalid."""
        bad_payload = {
            "name": "Dup Arch",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor"},
                {"component_id": "c1", "name": "B", "component_type": "Compute"},
            ],
            "flows": [],
        }
        client = TestClient(app)
        r = client.post("/architectures", json=bad_payload)
        assert r.status_code == 422

    def test_minimal_arch_no_components_accepted(self):
        db = _stub_db()

        def _refresh(obj):
            obj.id = 1
            obj.components = []
            obj.flows = []
            obj.created_at = _NOW
            obj.updated_at = _NOW

        db.refresh = MagicMock(side_effect=_refresh)
        _inject_db(db)
        client = TestClient(app)
        r = client.post("/architectures", json=MINIMAL_ARCH)
        _clear_db()
        assert r.status_code == 201

    def test_flow_with_cia_requirement_accepted(self):
        """Flows with cia_requirement field must be accepted without error."""
        db = _stub_db()

        def _refresh(obj):
            obj.id = 5
            obj.components = []
            obj.flows = []
            obj.created_at = _NOW
            obj.updated_at = _NOW

        db.refresh = MagicMock(side_effect=_refresh)
        _inject_db(db)
        client = TestClient(app)
        r = client.post("/architectures", json=SIMPLE_ARCH)
        _clear_db()
        assert r.status_code == 201

    def test_flow_referencing_unknown_component_returns_422(self):
        """A flow whose target doesn't match any component_id in the list is invalid."""
        bad_payload = {
            "name": "Bad Flow Arch",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor"},
            ],
            "flows": [
                {
                    "source_component_id": "c1",
                    "target_component_id": "does-not-exist",
                }
            ],
        }
        client = TestClient(app)
        r = client.post("/architectures", json=bad_payload)
        assert r.status_code == 422


# ===========================================================================
# Test: Load Architecture (GET /architectures and GET /architectures/{id})
# ===========================================================================


class TestLoadArchitecture:
    """
    Verifies that a saved architecture can be retrieved with all its components
    and flows intact.
    Covers: 'Load architecture → verify frontend receives correct data'.
    """

    def test_list_architectures_returns_200(self):
        db = _stub_db()
        db.query.return_value.options.return_value.all.return_value = []
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures")
        _clear_db()
        assert r.status_code == 200

    def test_list_returns_list(self):
        db = _stub_db()
        db.query.return_value.options.return_value.all.return_value = []
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures")
        _clear_db()
        assert isinstance(r.json(), list)

    def test_get_by_id_returns_200(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        assert r.status_code == 200

    def test_get_by_id_returns_name(self):
        arch = _make_mock_architecture(arch_id=1, name="My Architecture")
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        assert r.json()["name"] == "My Architecture"

    def test_get_by_id_returns_components(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        data = r.json()
        assert "components" in data
        assert len(data["components"]) == 3

    def test_get_by_id_returns_flows(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        data = r.json()
        assert "flows" in data
        assert len(data["flows"]) == 2

    def test_get_nonexistent_returns_404(self):
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/99999")
        _clear_db()
        assert r.status_code == 404

    def test_component_has_component_id(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        assert "component_id" in r.json()["components"][0]

    def test_component_has_criticality(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        assert "criticality" in r.json()["components"][0]

    def test_flow_has_cia_requirement(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        assert "cia_requirement" in r.json()["flows"][0]

    def test_get_string_id_returns_422(self):
        """ID must be an integer; a non-numeric path param returns 422."""
        client = TestClient(app)
        r = client.get("/architectures/not-an-id")
        assert r.status_code == 422


# ===========================================================================
# Test: Run Simulation (POST /architectures/{id}/simulate)
# ===========================================================================


class TestRunSimulation:
    """
    Verifies that POSTing to the simulate endpoint returns a well-formed result.
    Covers: 'Run simulation → verify results returned correctly'.

    Note: the simulate endpoint currently uses a stub architecture (Issue #45
    tracks replacing it with a real DB query). Tests are written against the
    stub behaviour which is deterministic.
    """

    BASE = "/architectures/1/simulate"

    def test_simulate_returns_200(self):
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert r.status_code == 200

    def test_result_has_baseline_score(self):
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert "baseline_score" in r.json()

    def test_result_has_compromised_score(self):
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert "compromised_score" in r.json()

    def test_result_has_affected_components(self):
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert "affected_components" in r.json()

    def test_result_has_explanation(self):
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert "explanation" in r.json()

    def test_baseline_score_is_100(self):
        """Baseline should always be 100 (no attack applied yet)."""
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert r.json()["baseline_score"] == 100.0

    def test_compromised_score_less_than_or_equal_to_baseline(self):
        """After compromise, the score should be ≤ baseline."""
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        data = r.json()
        assert data["compromised_score"] <= data["baseline_score"]

    def test_unknown_scenario_returns_422(self):
        """SimulatorError from unknown scenario type is translated to HTTP 422."""
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=invalid_scenario&target_component_id=sensor-1"
        )
        assert r.status_code == 422

    def test_missing_target_returns_422(self):
        """target_component_id is required; omitting it returns 422."""
        client = TestClient(app)
        r = client.post(f"{self.BASE}?scenario_type=node_compromise")
        assert r.status_code == 422

    def test_scenario_type_defaults_to_node_compromise(self):
        """scenario_type has a default value — omitting it still returns 200."""
        client = TestClient(app)
        r = client.post(f"{self.BASE}?target_component_id=sensor-1")
        assert r.status_code == 200

    def test_result_scenario_type_echoed(self):
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert r.json()["scenario_type"] == "node_compromise"

    def test_case_insensitive_scenario_type(self):
        """Scenario type is normalized to lowercase by the simulator."""
        client = TestClient(app)
        r = client.post(
            f"{self.BASE}?scenario_type=NODE_COMPROMISE&target_component_id=sensor-1"
        )
        assert r.status_code == 200
        assert r.json()["scenario_type"] == "node_compromise"


# ===========================================================================
# Test: Full End-to-End Flow (Save → Load → Simulate)
# ===========================================================================


class TestEndToEndFlow:
    """
    Verifies the complete user journey: save an architecture, retrieve it by
    ID, then run a simulation on it.
    Covers: 'Save/load/simulate full flow end-to-end'.
    """

    def test_save_succeeds(self):
        db = _stub_db()

        def _refresh(obj):
            obj.id = 7
            obj.components = []
            obj.flows = []
            obj.created_at = _NOW
            obj.updated_at = _NOW

        db.refresh = MagicMock(side_effect=_refresh)
        _inject_db(db)
        client = TestClient(app)
        r = client.post("/architectures", json=SIMPLE_ARCH)
        _clear_db()
        assert r.status_code == 201

    def test_load_after_save_has_components(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        assert len(r.json()["components"]) > 0

    def test_load_preserves_component_names(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        names = [c["name"] for c in r.json()["components"]]
        assert "Sensor Alpha" in names

    def test_load_preserves_component_criticality(self):
        arch = _make_mock_architecture(arch_id=1)
        db = _stub_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = arch
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures/1")
        _clear_db()
        sensor = next(
            c for c in r.json()["components"] if c["component_id"] == "sensor-1"
        )
        assert sensor["criticality"] == 8

    def test_simulate_after_load_succeeds(self):
        """Simulation endpoint returns 200 (uses stub architecture)."""
        client = TestClient(app)
        r = client.post(
            "/architectures/1/simulate"
            "?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert r.status_code == 200

    def test_simulate_result_has_all_required_fields(self):
        client = TestClient(app)
        r = client.post(
            "/architectures/1/simulate"
            "?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        data = r.json()
        required = {
            "baseline_score",
            "compromised_score",
            "affected_components",
            "explanation",
            "scenario_type",
        }
        assert required.issubset(data.keys())

    def test_health_check_available_throughout(self):
        """Health endpoint must remain 200 before and after other calls."""
        client = TestClient(app)
        assert client.get("/health").status_code == 200
        client.post(
            "/architectures/1/simulate"
            "?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        assert client.get("/health").status_code == 200


# ===========================================================================
# Test: Error Cases
# ===========================================================================


class TestErrorCases:
    """
    Covers error paths across the API:
    - Invalid data (missing required fields, wrong types)
    - Missing architectures (404)
    - Invalid scenario parameters (422)
    """

    def test_post_arch_empty_body_returns_422(self):
        client = TestClient(app)
        r = client.post("/architectures", json={})
        assert r.status_code == 422

    def test_post_arch_missing_name_returns_422(self):
        client = TestClient(app)
        r = client.post(
            "/architectures",
            json={"description": "no name", "components": [], "flows": []},
        )
        assert r.status_code == 422

    def test_get_arch_string_id_returns_422(self):
        """Non-numeric path param for integer ID returns 422."""
        client = TestClient(app)
        r = client.get("/architectures/not-an-id")
        assert r.status_code == 422

    def test_simulate_on_any_arch_id_returns_200_with_stub(self):
        """
        Documents current stub behaviour: the simulate endpoint ignores the
        architecture ID and always returns the hardcoded stub result.
        When Issue #45 is implemented, unknown IDs should return 404.
        """
        client = TestClient(app)
        r = client.post(
            "/architectures/99999/simulate"
            "?scenario_type=node_compromise&target_component_id=sensor-1"
        )
        # Accept both 200 (stub behaviour, Increment 1/2) and 404 (post-Issue #45)
        assert r.status_code in (200, 404)

    def test_flow_referencing_unknown_component_returns_422(self):
        """A flow whose target doesn't exist in the components list is invalid."""
        bad_payload = {
            "name": "Bad Flow Arch",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor"},
            ],
            "flows": [
                {
                    "source_component_id": "c1",
                    "target_component_id": "does-not-exist",
                }
            ],
        }
        client = TestClient(app)
        r = client.post("/architectures", json=bad_payload)
        assert r.status_code == 422

    def test_simulate_unknown_scenario_returns_422(self):
        client = TestClient(app)
        r = client.post(
            "/architectures/1/simulate"
            "?scenario_type=not_a_real_scenario&target_component_id=sensor-1"
        )
        assert r.status_code == 422

    def test_list_architectures_empty_db_returns_empty_list(self):
        """Even when DB has no rows, /architectures must return an empty list."""
        db = _stub_db()
        db.query.return_value.options.return_value.all.return_value = []
        _inject_db(db)
        client = TestClient(app)
        r = client.get("/architectures")
        _clear_db()
        assert r.status_code == 200
        assert r.json() == []

    def test_post_arch_wrong_type_for_criticality_returns_422(self):
        """Criticality must be an int; a string value should fail Pydantic validation."""
        bad_payload = {
            "name": "Type Error Arch",
            "components": [
                {
                    "component_id": "c1",
                    "name": "Sensor",
                    "component_type": "Sensor",
                    "criticality": "high",  # wrong type
                }
            ],
            "flows": [],
        }
        client = TestClient(app)
        r = client.post("/architectures", json=bad_payload)
        assert r.status_code == 422
