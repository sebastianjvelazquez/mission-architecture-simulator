"""
tests/test_error_handling.py

Unit tests for database error handling in the architectures API.

Tests cover:
    - 422 validation errors (duplicate component_id, unknown flow references,
      missing required fields) — no DB interaction needed
    - 409 Conflict on IntegrityError (unique / not-null / FK constraint violations)
    - 500 Internal Server Error on generic SQLAlchemyError
    - Rollback is called exactly once on every DB failure path
    - 404 for a missing architecture id
    - _integrity_error_detail helper message classification
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.architectures import _integrity_error_detail
from app.core.main import app
from app.database import get_db

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MINIMAL_PAYLOAD: dict = {
    "name": "Test Architecture",
    "components": [],
    "flows": [],
}

WITH_COMPONENTS: dict = {
    "name": "Arch With Components",
    "components": [
        {"component_id": "c1", "name": "Sensor", "component_type": "Sensor"},
        {"component_id": "c2", "name": "Compute", "component_type": "Compute"},
    ],
    "flows": [
        {"source_component_id": "c1", "target_component_id": "c2"},
    ],
}


def _mock_db(*, flush_exc=None, commit_exc=None) -> MagicMock:
    """Return a MagicMock Session with optional side-effects on flush/commit."""
    db = MagicMock(spec=Session)
    if flush_exc is not None:
        db.flush.side_effect = flush_exc
    if commit_exc is not None:
        db.commit.side_effect = commit_exc
    return db


def _override(mock_session: MagicMock):
    """Build a get_db override that yields the given mock session."""
    def _get_db_override():
        yield mock_session
    return _get_db_override


def _make_integrity_error(message: str = "UNIQUE constraint failed") -> IntegrityError:
    orig = Exception(message)
    return IntegrityError("INSERT INTO architectures", {}, orig)


def _make_sqlalchemy_error() -> SQLAlchemyError:
    return OperationalError("SELECT 1", {}, Exception("connection refused"))


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# _integrity_error_detail helper
# ---------------------------------------------------------------------------

class TestIntegrityErrorDetail:

    def test_unique_constraint_message(self):
        exc = _make_integrity_error("UNIQUE constraint failed: architectures.name")
        assert "unique constraint" in _integrity_error_detail(exc).lower()

    def test_duplicate_entry_message(self):
        exc = _make_integrity_error("duplicate key value violates unique constraint")
        assert "already exists" in _integrity_error_detail(exc).lower()

    def test_not_null_constraint_message(self):
        exc = _make_integrity_error("null value in column violates not-null constraint")
        assert "required field" in _integrity_error_detail(exc).lower()

    def test_notnull_sqlite_style(self):
        exc = _make_integrity_error("NOT NULL constraint failed: components.name")
        assert "required field" in _integrity_error_detail(exc).lower()

    def test_foreign_key_constraint_message(self):
        exc = _make_integrity_error("foreign key constraint fails")
        assert "does not exist" in _integrity_error_detail(exc).lower()

    def test_check_constraint_message(self):
        exc = _make_integrity_error("check constraint violated")
        assert "range" in _integrity_error_detail(exc).lower()

    def test_unknown_constraint_returns_generic(self):
        exc = _make_integrity_error("some obscure db error xyz")
        assert "constraint violation" in _integrity_error_detail(exc).lower()

    def test_none_orig_does_not_crash(self):
        exc = IntegrityError("stmt", {}, None)
        result = _integrity_error_detail(exc)
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Validation errors (422) — no DB interaction
# ---------------------------------------------------------------------------

class TestValidationErrors:

    def test_missing_name_returns_422(self, client):
        r = client.post("/architectures", json={"components": [], "flows": []})
        assert r.status_code == 422

    def test_duplicate_component_id_returns_422(self, client):
        payload = {
            "name": "Dup Test",
            "components": [
                {"component_id": "same", "name": "A", "component_type": "Sensor"},
                {"component_id": "same", "name": "B", "component_type": "Compute"},
            ],
            "flows": [],
        }
        r = client.post("/architectures", json=payload)
        assert r.status_code == 422
        assert "Duplicate" in r.json()["detail"]

    def test_flow_source_not_in_components_returns_422(self, client):
        payload = {
            "name": "Bad Flow",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor"},
            ],
            "flows": [{"source_component_id": "GHOST", "target_component_id": "c1"}],
        }
        r = client.post("/architectures", json=payload)
        assert r.status_code == 422
        assert "GHOST" in r.json()["detail"]

    def test_flow_target_not_in_components_returns_422(self, client):
        payload = {
            "name": "Bad Flow Target",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor"},
            ],
            "flows": [{"source_component_id": "c1", "target_component_id": "GHOST"}],
        }
        r = client.post("/architectures", json=payload)
        assert r.status_code == 422
        assert "GHOST" in r.json()["detail"]

    def test_criticality_below_minimum_returns_422(self, client):
        payload = {
            "name": "Bad Criticality",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor", "criticality": 0},
            ],
            "flows": [],
        }
        r = client.post("/architectures", json=payload)
        assert r.status_code == 422

    def test_criticality_above_maximum_returns_422(self, client):
        payload = {
            "name": "Bad Criticality High",
            "components": [
                {"component_id": "c1", "name": "A", "component_type": "Sensor", "criticality": 11},
            ],
            "flows": [],
        }
        r = client.post("/architectures", json=payload)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# IntegrityError → 409
# ---------------------------------------------------------------------------

class TestIntegrityErrorHandling:

    def test_unique_violation_returns_409(self, client):
        db = _mock_db(flush_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_409_detail_is_human_readable(self, client):
        db = _mock_db(flush_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            detail = r.json()["detail"]
            assert isinstance(detail, str)
            assert len(detail) > 10
            assert detail != "Internal Server Error"
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_not_null_violation_returns_409(self, client):
        db = _mock_db(
            flush_exc=_make_integrity_error(
                "null value in column violates not-null constraint"
            )
        )
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_foreign_key_violation_returns_409(self, client):
        db = _mock_db(flush_exc=_make_integrity_error("foreign key constraint fails"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_rollback_called_on_integrity_error(self, client):
        db = _mock_db(flush_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_commit_not_called_on_integrity_error(self, client):
        db = _mock_db(flush_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            db.commit.assert_not_called()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_integrity_error_on_commit_also_returns_409(self, client):
        # Integrity errors can surface at commit time too (deferred constraints).
        db = _mock_db(commit_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 409
        finally:
            app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# SQLAlchemyError → 500
# ---------------------------------------------------------------------------

class TestSQLAlchemyErrorHandling:

    def test_db_error_on_flush_returns_500(self, client):
        db = _mock_db(flush_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_db_error_on_commit_returns_500(self, client):
        db = _mock_db(commit_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_500_detail_is_meaningful(self, client):
        db = _mock_db(flush_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.post("/architectures", json=MINIMAL_PAYLOAD)
            detail = r.json()["detail"]
            assert "database" in detail.lower() or "failed" in detail.lower()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_rollback_called_on_sqlalchemy_error(self, client):
        db = _mock_db(flush_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_commit_not_called_on_sqlalchemy_error(self, client):
        db = _mock_db(flush_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            db.commit.assert_not_called()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_list_endpoint_db_error_returns_500(self, client):
        db = MagicMock(spec=Session)
        db.query.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.get("/architectures")
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_get_by_id_endpoint_db_error_returns_500(self, client):
        db = MagicMock(spec=Session)
        db.query.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.get("/architectures/1")
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# 404 — missing architecture
# ---------------------------------------------------------------------------

class TestNotFound:

    def test_get_nonexistent_id_returns_404(self, client):
        db = MagicMock(spec=Session)
        # Simulate query chain: .query().options().filter().first() -> None
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.get("/architectures/99999")
            assert r.status_code == 404
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_404_detail_includes_id(self, client):
        db = MagicMock(spec=Session)
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.get("/architectures/42")
            assert "42" in r.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_list_empty_returns_200_not_404(self, client):
        db = MagicMock(spec=Session)
        (
            db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all
            .return_value
        ) = []
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.get("/architectures")
            assert r.status_code == 200
            assert r.json() == []
        finally:
            app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Rollback isolation — verify rollback doesn't bleed across tests
# ---------------------------------------------------------------------------

class TestRollbackBehaviour:

    def test_rollback_called_exactly_once_per_integrity_error(self, client):
        db = _mock_db(flush_exc=_make_integrity_error("UNIQUE constraint failed"))
        app.dependency_overrides[get_db] = _override(db)
        try:
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert db.rollback.call_count == 1
        finally:
            app.dependency_overrides.pop(get_db, None)


class TestScenarioValidationAndErrors:

    def test_create_scenario_rejects_unsupported_type(self, client):
        payload = {
            "scenario_type": "bad_type",
            "target_component_id": 1,
            "parameters": {},
        }
        r = client.post("/architectures/1/scenarios", json=payload)
        assert r.status_code == 422
        assert "unsupported scenario_type" in r.json()["detail"].lower()

    def test_create_scenario_rejects_invalid_node_compromise_parameters(self, client):
        payload = {
            "scenario_type": "node_compromise",
            "target_component_id": 1,
            "parameters": {"severity": "extreme"},
        }
        r = client.post("/architectures/1/scenarios", json=payload)
        assert r.status_code == 422
        assert "severity" in r.json()["detail"].lower()

    def test_create_scenario_rejects_invalid_link_degradation_parameters(self, client):
        payload = {
            "scenario_type": "link_degradation",
            "target_component_id": 1,
            "parameters": {"packet_loss_percent": 120},
        }
        r = client.post("/architectures/1/scenarios", json=payload)
        assert r.status_code == 422
        assert "packet_loss_percent" in r.json()["detail"].lower()

    def test_create_scenario_integrity_error_returns_409_and_rolls_back(self, client):
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        db.commit.side_effect = _make_integrity_error("UNIQUE constraint failed")
        app.dependency_overrides[get_db] = _override(db)
        try:
            payload = {
                "scenario_type": "node_compromise",
                "target_component_id": 1,
                "parameters": {"severity": "high"},
            }
            r = client.post("/architectures/1/scenarios", json=payload)
            assert r.status_code == 409
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_create_scenario_db_error_returns_500_and_rolls_back(self, client):
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        db.commit.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            payload = {
                "scenario_type": "node_compromise",
                "target_component_id": 1,
                "parameters": {"severity": "high"},
            }
            r = client.post("/architectures/1/scenarios", json=payload)
            assert r.status_code == 500
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_list_scenarios_db_error_returns_500(self, client):
        db = MagicMock(spec=Session)
        db.query.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.get("/architectures/1/scenarios")
            assert r.status_code == 500
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_delete_scenario_db_error_returns_500_and_rolls_back(self, client):
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = MagicMock()
        db.commit.side_effect = _make_sqlalchemy_error()
        app.dependency_overrides[get_db] = _override(db)
        try:
            r = client.delete("/architectures/1/scenarios/9")
            assert r.status_code == 500
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_create_result_integrity_error_returns_409_and_rolls_back(self, client):
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = MagicMock()
        db.commit.side_effect = _make_integrity_error("FOREIGN KEY constraint failed")
        app.dependency_overrides[get_db] = _override(db)
        try:
            payload = {
                "baseline_score": 100.0,
                "compromised_score": 90.0,
                "affected_components": [],
                "attack_path": [],
                "explanation": "x",
            }
            r = client.post("/scenarios/1/results", json=payload)
            assert r.status_code == 409
            db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_rollback_called_exactly_once_per_sqlalchemy_error(self, client):
        db = _mock_db(flush_exc=_make_sqlalchemy_error())
        app.dependency_overrides[get_db] = _override(db)
        try:
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            assert db.rollback.call_count == 1
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_successful_path_does_not_call_rollback(self, client):
        db = MagicMock(spec=Session)
        # Make flush work (no side effect), query chain returns a mock arch.
        mock_arch = MagicMock()
        mock_arch.id = 1
        mock_arch.name = "Test"
        mock_arch.description = None
        mock_arch.properties = {}
        mock_arch.components = []
        mock_arch.flows = []
        # flush populates arch.id — simulate by setting it on mock results
        db.flush.side_effect = None
        db.commit.side_effect = None
        db.refresh.side_effect = None
        app.dependency_overrides[get_db] = _override(db)
        try:
            # We don't care if this returns 200 or 500 (serialisation will fail
            # since the mock arch isn't a real ORM object) — we only care that
            # rollback was NOT triggered by the flush/commit path.
            client.post("/architectures", json=MINIMAL_PAYLOAD)
            db.rollback.assert_not_called()
        finally:
            app.dependency_overrides.pop(get_db, None)
