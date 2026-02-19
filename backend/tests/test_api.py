"""
tests/test_api.py

Integration tests for app/main.py and app/routers/simulate.py.

These tests spin up the full FastAPI application using TestClient, which
runs requests in-process without needing a real running server. This means
they test the entire request/response cycle including middleware, routing,
validation, and error handling.

Covers:
    - _parse_allowed_origins helper function
    - GET /health endpoint
    - App metadata (title, version, OpenAPI docs)
    - CORS middleware headers
    - POST /architectures/{id}/simulate endpoint (happy path and error cases)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app, _parse_allowed_origins


# Override get_settings() for the entire test session so tests never read
# from the real .env file. FastAPI's dependency_overrides dict lets us swap
# any Depends() dependency with a test version at runtime.
def get_test_settings() -> Settings:
    return Settings(
        ENVIRONMENT="test",
        # Include both localhost:3000 and testserver so CORS tests pass
        # regardless of which origin TestClient sends.
        ALLOWED_ORIGINS="http://localhost:3000,http://testserver",
    )


# autouse=True means this fixture runs automatically for every test in the file
# without needing to declare it as a parameter. It ensures settings are always
# overridden before the test runs and cleared after, preventing test pollution.
@pytest.fixture(autouse=True)
def override_settings():
    app.dependency_overrides[get_settings] = get_test_settings
    yield
    # Clear all overrides after each test so one test's overrides can't
    # accidentally affect the next test.
    app.dependency_overrides.clear()


# Provides a fresh TestClient for each test that requests it.
# TestClient wraps the ASGI app and lets us make HTTP requests as if we were
# a real browser or curl command, but entirely in-memory.
@pytest.fixture
def client():
    return TestClient(app)


# Tests for the _parse_allowed_origins helper in main.py.
# This is a pure function (no HTTP involved) so we test it directly
# without needing the TestClient.
class TestParseAllowedOrigins:

    def test_single_origin(self):
        # Most basic case: one origin with no commas
        assert _parse_allowed_origins("http://localhost:3000") == ["http://localhost:3000"]

    def test_comma_separated(self):
        # Production scenario: local dev origin + deployed Vercel origin
        result = _parse_allowed_origins("http://localhost:3000,https://app.vercel.app")
        assert result == ["http://localhost:3000", "https://app.vercel.app"]

    def test_strips_whitespace(self):
        # .env files sometimes have spaces after commas, this must be handled
        result = _parse_allowed_origins("http://a.com , http://b.com")
        assert result == ["http://a.com", "http://b.com"]

    def test_empty_string_returns_empty_list(self):
        # Empty ALLOWED_ORIGINS triggers the fallback in add_middleware()
        assert _parse_allowed_origins("") == []

    def test_trailing_comma_ignored(self):
        # Guard against accidental trailing commas in .env
        result = _parse_allowed_origins("http://a.com,")
        assert result == ["http://a.com"]


class TestHealthCheck:

    def test_returns_200(self, client):
        # The most basic liveness check: the app is up and responding
        assert client.get("/health").status_code == 200

    def test_status_healthy(self, client):
        # The status field must always be exactly "healthy"
        assert client.get("/health").json()["status"] == "healthy"

    def test_environment_returned(self, client):
        # The environment field confirms which deployment we're hitting.
        # We expect "test" here because of the get_test_settings override above.
        data = client.get("/health").json()
        assert "environment" in data
        assert data["environment"] == "test"

    def test_post_not_allowed(self, client):
        # /health is GET only. POST should return 405 Method Not Allowed.
        assert client.post("/health").status_code == 405


class TestAppMetadata:

    def test_title(self):
        # Verify the app title contains "Mission" so it's clearly identified
        # in Swagger and monitoring dashboards.
        assert "Mission" in app.title

    def test_version(self):
        # Version must match what was declared in main.py
        assert app.version == "0.1.0"

    def test_docs_accessible(self, client):
        # Swagger UI should be reachable at /docs in all environments
        assert client.get("/docs").status_code == 200

    def test_openapi_json_accessible(self, client):
        # The raw OpenAPI schema at /openapi.json is used by Swagger,
        # Postman, and any other API clients
        assert client.get("/openapi.json").status_code == 200

    def test_openapi_contains_health_path(self, client):
        # Confirms /health is registered as a documented route
        paths = client.get("/openapi.json").json()["paths"]
        assert "/health" in paths

    def test_openapi_contains_simulate_path(self, client):
        # Confirms the simulate router was registered in main.py
        paths = client.get("/openapi.json").json()["paths"]
        assert any("simulate" in p for p in paths)


class TestCORSMiddleware:

    def test_cors_header_present(self, client):
        # When a request includes an Origin header, the response must include
        # access-control-allow-origin to tell the browser the call is allowed.
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers

    def test_preflight_returns_200(self, client):
        # Browsers send an OPTIONS preflight before cross-origin POST requests.
        # The middleware must respond with 200 or the actual request is blocked.
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200


class TestSimulateEndpoint:

    # Base URL used by all tests in this class. Architecture ID 1 is served
    # by the stub function in simulate.py for Increment 1.
    BASE = "/architectures/1/simulate"

    def test_valid_request_returns_200(self, client):
        # Happy path: valid scenario and a component ID that exists in the stub
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert r.status_code == 200

    def test_response_has_baseline_score(self, client):
        # baseline_score must always be present so the frontend can draw the chart
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "baseline_score" in r.json()

    def test_response_has_compromised_score(self, client):
        # compromised_score is the after-attack score shown in the bar chart
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "compromised_score" in r.json()

    def test_response_has_affected_components(self, client):
        # affected_components is the list the frontend uses to colour nodes red
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "affected_components" in r.json()

    def test_response_has_attack_path(self, client):
        # attack_path is the step-by-step propagation narrative in the results panel
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "attack_path" in r.json()

    def test_response_has_explanation(self, client):
        # explanation is the single-sentence summary shown at the top of results
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "explanation" in r.json()

    def test_response_has_criticality_ranking(self, client):
        # criticality_ranking is the table that tells planners what to harden first
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "criticality_ranking" in r.json()

    def test_baseline_is_100(self, client):
        # Before any attack, all components are healthy so the score must be 100
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert r.json()["baseline_score"] == 100.0

    def test_compromised_score_lower_than_baseline(self, client):
        # The attack must degrade the mission score, never improve it
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        data = r.json()
        assert data["compromised_score"] < data["baseline_score"]

    def test_invalid_scenario_returns_422(self, client):
        # An unknown scenario type should be rejected with 422, not 500.
        # 422 means "we understood the request but can't process it" which is
        # more accurate than 500 ("something blew up unexpectedly").
        r = client.post(f"{self.BASE}?scenario_type=invalid_xyz&target_component_id=sensor-1")
        assert r.status_code == 422

    def test_invalid_target_returns_422(self, client):
        # A component ID that doesn't exist in the architecture is a user error,
        # so we return 422 rather than 404 (404 is reserved for missing resources
        # like a nonexistent architecture ID).
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=GHOST")
        assert r.status_code == 422

    def test_missing_target_returns_422(self, client):
        # target_component_id is required (no default). FastAPI returns 422
        # automatically when a required query parameter is absent.
        r = client.post(f"{self.BASE}?scenario_type=node_compromise")
        assert r.status_code == 422

    def test_scenario_type_case_insensitive(self, client):
        # The simulator lowercases the scenario_type before matching, so
        # NODE_COMPROMISE and node_compromise should behave identically.
        r = client.post(f"{self.BASE}?scenario_type=NODE_COMPROMISE&target_component_id=sensor-1")
        assert r.status_code == 200

    def test_default_scenario_is_node_compromise(self, client):
        # When scenario_type is omitted the default must be node_compromise,
        # and the response must echo it back in the scenario_type field.
        r = client.post(f"{self.BASE}?target_component_id=sensor-1")
        assert r.status_code == 200
        assert r.json()["scenario_type"] == "node_compromise"

    def test_target_in_affected_components(self, client):
        # The directly attacked component must always appear in affected_components,
        # even if it has no downstream dependencies.
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert "sensor-1" in r.json()["affected_components"]

    def test_architecture_id_in_response(self, client):
        # The response echoes back the architecture ID so the frontend can
        # confirm the result belongs to the architecture it requested.
        r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
        assert r.json()["architecture_id"] == 1