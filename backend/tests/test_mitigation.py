"""
tests/test_increment3.py

"""

from __future__ import annotations

from typing import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.core.main import app
from app.core.mitigations import MitigationSuggestion, suggest_mitigations
from app.database import get_db
from app.models.architecture import Architecture, Base, Component, Flow

# SQLite compat: map JSONB → JSON
SQLiteTypeCompiler.visit_JSONB = SQLiteTypeCompiler.visit_JSON  # type: ignore[attr-defined]

# Shared DB fixtures

@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_conn, _):
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
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)

# DB seeding helpers

def _seed_linear_arch(db: Session, name: str = "Linear") -> tuple[int, str, str, str]:
    """
    Seed a 3-node linear architecture: Sensor → Compute → Control.
    Returns (arch_id, sensor_slug, compute_slug, control_slug).
    """
    arch = Architecture(name=name, description="linear test", properties={})
    db.add(arch)
    db.flush()

    sensor = Component(
        architecture_id=arch.id,
        component_id="sensor-1",
        name="Sensor-1",
        component_type="Sensor",
        criticality=7,
        position_x=100,
        position_y=100,
        properties={},
    )
    compute = Component(
        architecture_id=arch.id,
        component_id="compute-1",
        name="Compute-1",
        component_type="Compute",
        criticality=8,
        position_x=300,
        position_y=100,
        properties={},
    )
    control = Component(
        architecture_id=arch.id,
        component_id="control-1",
        name="Control-1",
        component_type="Control",
        criticality=9,
        position_x=500,
        position_y=100,
        properties={},
    )
    db.add(sensor)
    db.add(compute)
    db.add(control)
    db.flush()

    flow1 = Flow(
        architecture_id=arch.id,
        source_component_id=sensor.id,
        target_component_id=compute.id,
        cia_requirement="integrity",
        properties={},
    )
    flow2 = Flow(
        architecture_id=arch.id,
        source_component_id=compute.id,
        target_component_id=control.id,
        cia_requirement="availability",
        properties={},
    )
    db.add(flow1)
    db.add(flow2)
    db.commit()
    return arch.id, "sensor-1", "compute-1", "control-1"

# UNIT TESTS — suggest_mitigations() (no DB, no HTTP)

class TestSuggestMitigations:
    """Tests for the pure-function mitigation suggester."""

    def _build_graph(self, edges, cia=None):
        import networkx as nx
        g = nx.DiGraph()
        for src, tgt in edges:
            attr = {}
            if cia:
                attr["cia_requirement"] = cia
            g.add_edge(src, tgt, **attr)
        return g

    def _comp(self, name, ctype="Sensor", crit=5):
        return {"name": name, "type": ctype, "criticality": crit}

    def test_empty_graph_returns_no_suggestions(self):
        import networkx as nx
        assert suggest_mitigations(nx.DiGraph(), {}) == []

    def test_spof_detected_for_root_node_with_descendants(self):
        g = self._build_graph([("A", "B"), ("B", "C")])
        comps = {"A": self._comp("A"), "B": self._comp("B"), "C": self._comp("C")}
        suggestions = suggest_mitigations(g, comps)
        types = [s.type for s in suggestions]
        assert "redundancy" in types

    def test_spof_not_detected_for_isolated_node(self):
        import networkx as nx
        g = nx.DiGraph()
        g.add_node("A")
        comps = {"A": self._comp("A")}
        # A has no successors so no cascade risk → no SPOF suggestion
        suggestions = suggest_mitigations(g, comps)
        spof = [s for s in suggestions if s.type == "redundancy" and s.affected_component_id == "A"]
        assert spof == []

    def test_segmentation_suggested_for_high_criticality_root(self):
        g = self._build_graph([("A", "B")])
        comps = {
            "A": self._comp("A", crit=9),  # high criticality, no predecessors
            "B": self._comp("B"),
        }
        suggestions = suggest_mitigations(g, comps)
        seg = [s for s in suggestions if s.type == "segmentation"]
        assert len(seg) >= 1

    def test_no_segmentation_for_low_criticality_root(self):
        g = self._build_graph([("A", "B")])
        comps = {
            "A": self._comp("A", crit=3),  # low criticality
            "B": self._comp("B"),
        }
        suggestions = suggest_mitigations(g, comps)
        seg = [s for s in suggestions if s.type == "segmentation"]
        assert seg == []

    def test_validation_gate_suggested_for_integrity_flow(self):
        g = self._build_graph([("A", "B")], cia="integrity")
        comps = {"A": self._comp("A"), "B": self._comp("B")}
        suggestions = suggest_mitigations(g, comps)
        vg = [s for s in suggestions if s.type == "validation_gate"]
        assert len(vg) >= 1

    def test_no_validation_gate_for_availability_flow(self):
        g = self._build_graph([("A", "B")], cia="availability")
        comps = {"A": self._comp("A"), "B": self._comp("B")}
        suggestions = suggest_mitigations(g, comps)
        vg = [s for s in suggestions if s.type == "validation_gate"]
        assert vg == []

    def test_cascade_hub_detected_for_large_blast_radius(self):
        # A → B, C, D, E  (A has 4 descendants out of 5 total = 80%)
        edges = [("A", "B"), ("A", "C"), ("A", "D"), ("A", "E")]
        g = self._build_graph(edges)
        comps = {n: self._comp(n) for n in "ABCDE"}
        suggestions = suggest_mitigations(g, comps)
        cascade = [s for s in suggestions if s.type == "segmentation_cascade"]
        assert len(cascade) >= 1

    def test_suggestions_sorted_by_expected_improvement_descending(self):
        g = self._build_graph([("A", "B"), ("B", "C"), ("C", "D")])
        comps = {n: self._comp(n, crit=9) for n in "ABCD"}
        suggestions = suggest_mitigations(g, comps)
        improvements = [s.expected_score_improvement for s in suggestions]
        assert improvements == sorted(improvements, reverse=True)

    def test_no_duplicate_suggestions_same_type_and_component(self):
        g = self._build_graph([("A", "B"), ("A", "C")])
        comps = {"A": self._comp("A", crit=9), "B": self._comp("B"), "C": self._comp("C")}
        suggestions = suggest_mitigations(g, comps)
        seen: set[tuple] = set()
        for s in suggestions:
            key = (s.type, s.affected_component_id)
            assert key not in seen, f"Duplicate suggestion: {key}"
            seen.add(key)

    def test_suggestion_has_required_fields(self):
        g = self._build_graph([("A", "B")])
        comps = {"A": self._comp("Root", crit=9), "B": self._comp("Leaf")}
        suggestions = suggest_mitigations(g, comps)
        for s in suggestions:
            assert isinstance(s, MitigationSuggestion)
            assert s.type
            assert s.affected_component_id
            assert s.description
            assert 0.0 <= s.expected_score_improvement <= 100.0

# INTEGRATION TESTS — POST /architectures/{id}/clone

class TestCloneEndpoint:

    def test_clone_returns_201(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Clone Me")
        resp = client.post(f"/architectures/{arch_id}/clone")
        assert resp.status_code == 201

    def test_clone_response_has_cloned_id(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Clone ID Test")
        resp = client.post(f"/architectures/{arch_id}/clone")
        body = resp.json()
        assert "cloned_architecture_id" in body
        assert isinstance(body["cloned_architecture_id"], int)
        assert body["cloned_architecture_id"] != arch_id

    def test_clone_name_has_clone_suffix(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "My Arch")
        resp = client.post(f"/architectures/{arch_id}/clone")
        assert resp.json()["cloned_architecture_name"] == "My Arch (Clone)"

    def test_clone_source_id_echoed(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Echo Arch")
        resp = client.post(f"/architectures/{arch_id}/clone")
        assert resp.json()["source_architecture_id"] == arch_id

    def test_clone_creates_independent_architecture(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Independent")
        clone_id = client.post(f"/architectures/{arch_id}/clone").json()["cloned_architecture_id"]

        orig = client.get(f"/architectures/{arch_id}").json()
        clone = client.get(f"/architectures/{clone_id}").json()

        assert len(orig["components"]) == len(clone["components"])
        assert len(orig["flows"]) == len(clone["flows"])
        # The clone must have different DB ids for components
        orig_comp_ids = {c["id"] for c in orig["components"]}
        clone_comp_ids = {c["id"] for c in clone["components"]}
        assert orig_comp_ids.isdisjoint(clone_comp_ids)

    def test_clone_components_have_same_slugs(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Slug Check")
        clone_id = client.post(f"/architectures/{arch_id}/clone").json()["cloned_architecture_id"]

        orig = client.get(f"/architectures/{arch_id}").json()
        clone = client.get(f"/architectures/{clone_id}").json()

        orig_slugs = sorted(c["component_id"] for c in orig["components"])
        clone_slugs = sorted(c["component_id"] for c in clone["components"])
        assert orig_slugs == clone_slugs

    def test_clone_missing_architecture_returns_404(self, client):
        resp = client.post("/architectures/999999/clone")
        assert resp.status_code == 404

    def test_clone_documented_in_openapi(self, client):
        openapi = client.get("/openapi.json").json()
        paths = openapi.get("paths", {})
        clone_path = "/architectures/{architecture_id}/clone"
        assert clone_path in paths
        assert "post" in paths[clone_path]

# INTEGRATION TESTS — GET /architectures/{id}/mitigations

class TestMitigationsEndpoint:

    def test_mitigations_returns_200(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Mitigation Check")
        resp = client.get(f"/architectures/{arch_id}/mitigations")
        assert resp.status_code == 200

    def test_mitigations_response_shape(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Shape Check")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        assert "architecture_id" in body
        assert "component_count" in body
        assert "flow_count" in body
        assert "suggestions" in body

    def test_mitigations_architecture_id_matches(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "ID Match")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        assert body["architecture_id"] == arch_id

    def test_mitigations_component_count_correct(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Count Check")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        assert body["component_count"] == 3

    def test_mitigations_suggestions_is_list(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "List Check")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        assert isinstance(body["suggestions"], list)

    def test_mitigations_suggestion_has_required_fields(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Fields Check")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        for s in body["suggestions"]:
            assert "type" in s
            assert "affected_component_id" in s
            assert "affected_component_name" in s
            assert "description" in s
            assert "expected_score_improvement" in s

    def test_mitigations_missing_architecture_returns_404(self, client):
        resp = client.get("/architectures/999999/mitigations")
        assert resp.status_code == 404

    def test_mitigations_linear_arch_produces_suggestions(self, client, db_session):
        # The linear Sensor→Compute→Control arch has a SPOF (Sensor has no predecessors
        # and has descendants) so we expect at least one suggestion.
        arch_id, *_ = _seed_linear_arch(db_session, "Linear Suggestions")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        assert len(body["suggestions"]) >= 1

    def test_mitigations_sorted_by_improvement_desc(self, client, db_session):
        arch_id, *_ = _seed_linear_arch(db_session, "Sort Check")
        body = client.get(f"/architectures/{arch_id}/mitigations").json()
        improvements = [s["expected_score_improvement"] for s in body["suggestions"]]
        assert improvements == sorted(improvements, reverse=True)

    def test_mitigations_documented_in_openapi(self, client):
        openapi = client.get("/openapi.json").json()
        paths = openapi.get("paths", {})
        mit_path = "/architectures/{architecture_id}/mitigations"
        assert mit_path in paths
        assert "get" in paths[mit_path]

# INTEGRATION TESTS — GET /architectures/compare

class TestCompareEndpoint:

    def _seed_pair(self, db: Session):
        """Seed a baseline + clone pair and return (arch_id, clone_id, sensor_slug)."""
        arch_id, sensor_slug, _, _ = _seed_linear_arch(db, "Compare Base")
        arch = db.query(Architecture).filter(Architecture.id == arch_id).first()
        # Build clone manually so we control it independently of the HTTP layer.
        clone_arch = Architecture(name="Compare Mitigated", description="", properties={})
        db.add(clone_arch)
        db.flush()

        id_map: dict[int, int] = {}
        orig_comps = db.query(Component).filter(Component.architecture_id == arch_id).all()
        for oc in orig_comps:
            nc = Component(
                architecture_id=clone_arch.id,
                component_id=oc.component_id,
                name=oc.name,
                component_type=oc.component_type,
                criticality=oc.criticality,
                position_x=oc.position_x,
                position_y=oc.position_y,
                properties={},
            )
            db.add(nc)
            db.flush()
            id_map[oc.id] = nc.id

        orig_flows = db.query(Flow).filter(Flow.architecture_id == arch_id).all()
        for of in orig_flows:
            nf = Flow(
                architecture_id=clone_arch.id,
                source_component_id=id_map[of.source_component_id],
                target_component_id=id_map[of.target_component_id],
                cia_requirement=of.cia_requirement,
                properties={},
            )
            db.add(nf)

        db.commit()
        return arch_id, clone_arch.id, sensor_slug

    def test_compare_returns_200(self, client, db_session):
        base_id, mit_id, slug = self._seed_pair(db_session)
        resp = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        )
        assert resp.status_code == 200

    def test_compare_response_has_required_fields(self, client, db_session):
        base_id, mit_id, slug = self._seed_pair(db_session)
        body = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        ).json()
        for field in ("scenario_type", "target_component_id", "baseline", "mitigated",
                      "score_improvement", "components_protected", "summary"):
            assert field in body, f"Missing field: {field}"

    def test_compare_baseline_and_mitigated_have_scores(self, client, db_session):
        base_id, mit_id, slug = self._seed_pair(db_session)
        body = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        ).json()
        assert "compromised_score" in body["baseline"]
        assert "compromised_score" in body["mitigated"]

    def test_compare_score_improvement_is_numeric(self, client, db_session):
        base_id, mit_id, slug = self._seed_pair(db_session)
        body = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        ).json()
        assert isinstance(body["score_improvement"], (int, float))

    def test_compare_components_protected_is_list(self, client, db_session):
        base_id, mit_id, slug = self._seed_pair(db_session)
        body = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        ).json()
        assert isinstance(body["components_protected"], list)

    def test_compare_missing_baseline_returns_404(self, client, db_session):
        _, mit_id, slug = self._seed_pair(db_session)
        resp = client.get(
            "/architectures/compare",
            params={
                "baseline_id": 999999,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        )
        assert resp.status_code == 404

    def test_compare_missing_mitigated_returns_404(self, client, db_session):
        base_id, _, slug = self._seed_pair(db_session)
        resp = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": 999999,
                "scenario_type": "node_compromise",
                "target_component_id": slug,
            },
        )
        assert resp.status_code == 404

    def test_compare_invalid_target_returns_422(self, client, db_session):
        base_id, mit_id, _ = self._seed_pair(db_session)
        resp = client.get(
            "/architectures/compare",
            params={
                "baseline_id": base_id,
                "mitigated_id": mit_id,
                "scenario_type": "node_compromise",
                "target_component_id": "ghost-node-xyz",
            },
        )
        assert resp.status_code == 422

    def test_compare_documented_in_openapi(self, client):
        openapi = client.get("/openapi.json").json()
        paths = openapi.get("paths", {})
        assert "/architectures/compare" in paths
        assert "get" in paths["/architectures/compare"]

# UNIT TESTS — Settings.get_allowed_origins()

class TestGetAllowedOrigins:

    def test_single_origin(self):
        s = Settings(ENVIRONMENT="production", ALLOWED_ORIGINS="http://localhost:3000")
        origins = s.get_allowed_origins()
        assert "http://localhost:3000" in origins

    def test_comma_separated_origins(self):
        s = Settings(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="http://localhost:3000,https://staging.vercel.app",
        )
        origins = s.get_allowed_origins()
        assert "http://localhost:3000" in origins
        assert "https://staging.vercel.app" in origins

    def test_frontend_url_appended(self):
        s = Settings(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="http://localhost:3000",
            FRONTEND_URL="https://my-app.vercel.app",
        )
        origins = s.get_allowed_origins()
        assert "https://my-app.vercel.app" in origins

    def test_frontend_url_not_duplicated(self):
        url = "https://my-app.vercel.app"
        s = Settings(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS=url,
            FRONTEND_URL=url,
        )
        origins = s.get_allowed_origins()
        assert origins.count(url) == 1

    def test_development_always_includes_localhost(self):
        s = Settings(
            ENVIRONMENT="development",
            ALLOWED_ORIGINS="https://other.example.com",
        )
        origins = s.get_allowed_origins()
        assert "http://localhost:3000" in origins

    def test_production_does_not_add_extra_localhost(self):
        s = Settings(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="https://my-app.vercel.app",
        )
        origins = s.get_allowed_origins()
        # localhost should NOT be added in production
        assert "http://localhost:3000" not in origins

    def test_whitespace_stripped_from_origins(self):
        s = Settings(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="http://a.com , http://b.com",
        )
        origins = s.get_allowed_origins()
        assert "http://a.com" in origins
        assert "http://b.com" in origins

    def test_trailing_comma_ignored(self):
        s = Settings(
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="http://a.com,",
        )
        origins = s.get_allowed_origins()
        assert "" not in origins

# INTEGRATION TESTS — /health extended fields

class TestHealthExtended:

    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_has_db_ok_field(self, client):
        resp = client.get("/health")
        assert "db_ok" in resp.json()

    def test_health_has_version_field(self, client):
        resp = client.get("/health")
        assert "version" in resp.json()

    def test_health_version_is_string(self, client):
        resp = client.get("/health")
        assert isinstance(resp.json()["version"], str)

    def test_health_status_healthy(self, client):
        resp = client.get("/health")
        assert resp.json()["status"] == "healthy"