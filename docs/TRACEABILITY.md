# Requirements Traceability Matrix

## Mission-System Security Architecture Simulator

**Group 4 — Increment 3**
**Date:** April 27, 2026

---

This matrix maps each functional requirement (FR) from the Requirements Document to the
implementation file(s) that satisfy it and the test(s) that verify it.

---

## Functional Requirements Traceability

| FR ID | Requirement Summary | Implementation File(s) | Test File(s) | Test Name(s) |
|-------|---------------------|------------------------|--------------|--------------|
| FR-1 | Visual diagram editor — add components via drag-and-drop | `frontend/app/dashboard/page.tsx` | — | (frontend, manual E2E) |
| FR-2 | Draw directed data flows (edges) between components | `frontend/app/dashboard/page.tsx` | — | (frontend, manual E2E) |
| FR-3 | Delete components and flows from the diagram | `frontend/app/dashboard/page.tsx`, `backend/app/api/architectures.py` | `tests/test_api.py` | `TestArchitectureAPI::test_delete_architecture` |
| FR-4 | Edit component properties (name, criticality) | `backend/app/api/architectures.py` | `tests/test_architecture_update_api.py` | `TestUpdateArchitecture::*` |
| FR-5 | Save Architecture — persist to PostgreSQL | `backend/app/api/architectures.py` | `tests/test_api.py` | `TestArchitectureAPI::test_create_architecture` |
| FR-6 | Load Architecture — retrieve from database | `backend/app/api/architectures.py` | `tests/test_api.py` | `TestArchitectureAPI::test_get_architecture`, `test_list_architectures` |
| FR-7 | Node compromise attack scenario | `backend/app/core/simulator.py` | `tests/test_simulator.py` | `TestNodeCompromise::*` |
| FR-8 | Propagate compromise through dependency graph | `backend/app/core/simulator.py` | `tests/test_simulator.py` | `TestPropagation::*` |
| FR-9 | Calculate mission success score | `backend/app/core/simulator.py` | `tests/test_simulator.py` | `TestMissionScore::*` |
| FR-10 | Display simulation results (baseline, compromised, affected components) | `backend/app/core/simulate.py`, `frontend/app/dashboard/page.tsx` | `tests/test_api.py` | `TestSimulateEndpoint::*` |
| FR-11 | Bar chart comparing baseline and compromised scores | `frontend/app/dashboard/page.tsx` | — | (frontend, manual E2E) |
| FR-12 | Criticality ranking of components | `backend/app/core/simulator.py` | `tests/test_simulator.py` | `TestCriticalityRanking::*` |
| FR-13 | Step-by-step attack path description | `backend/app/core/simulator.py` | `tests/test_simulator.py` | `TestAttackPath::*` |
| FR-14 | API documentation via Swagger at `/docs` | `backend/app/core/main.py` | `tests/test_api.py` | `TestAPIDocumentation::*` |
| FR-15 | Health check endpoint `GET /health` | `backend/app/core/main.py` | `tests/test_api.py` | `TestHealthEndpoint::test_health_endpoint` |
| FR-16 | Multiple architectures per session | `backend/app/api/architectures.py` | `tests/test_api.py` | `TestArchitectureAPI::test_list_architectures` |
| FR-17 | Preserve component canvas positions on save/load | `backend/app/api/architectures.py`, `backend/app/models/architecture.py` | `tests/test_api.py` | `TestArchitectureAPI::test_create_architecture` |
| FR-18 | Save and list named scenarios for replay | `backend/app/api/scenarios.py` | `tests/test_scenarios_api.py`, `tests/test_increment3.py` | `TestScenariosAPI::*`, `TestScenariosApiErrors::*` |
| FR-19 | Delete a saved scenario | `backend/app/api/scenarios.py` | `tests/test_increment3.py` | `TestScenariosApiErrors::test_delete_scenario_returns_204` |
| FR-20 | Validate scenario type against allowed values | `backend/app/api/scenarios.py` | `tests/test_increment3.py` | `TestScenariosApiErrors::test_create_scenario_invalid_type_returns_422` |

---

## Non-Functional Requirements Traceability

| NFR ID | Requirement Summary | Verified By | Evidence |
|--------|---------------------|-------------|----------|
| NFR-1 | Simulation completes for 100 nodes in <1 second | `tests/test_simulator.py` | `TestPerformance::test_large_graph_performance` |
| NFR-2 | API response <500ms for 10–50 component architectures | `tests/test_simulator.py` | Performance test assertions |
| NFR-3 | 60fps frontend rendering during drag-and-drop | Manual browser testing | React Flow library handles rendering |
| NFR-4 | Handle circular dependencies without infinite loops | `tests/test_simulator.py` | `TestCircularDependencies::*` |
| NFR-5 | Graceful DB connection failure handling | `tests/test_error_handling.py`, `tests/test_increment3.py` | `TestSQLAlchemyErrors::*`, `TestListAndGetErrors::*` |
| NFR-6 | 95%+ API uptime during demonstration period | Render deployment monitoring | Render dashboard metrics |
| NFR-7 | CORS middleware restricts origins | `tests/test_api.py` | `TestCORS::*` |
| NFR-8 | Input validation via Pydantic schemas | `tests/test_error_handling.py` | `TestValidation::*` |
| NFR-9 | No internal error details exposed to users | `tests/test_error_handling.py`, `tests/test_increment3.py` | All 500 responses return generic messages |
| NFR-10 | Visual feedback on component selection | Manual browser testing | React Flow handles selection state |
| NFR-11 | Human-readable error messages | `tests/test_error_handling.py` | Assertions on `detail` field in error responses |
| NFR-12 | Accessible via modern browsers | Manual browser testing | Tested on Chrome, Firefox, Safari |
| NFR-13 | Test coverage: 60% (Incr 1) → 70% (Incr 2) → 85% (Incr 3) | pytest-cov | **94.24% achieved (Incr 3)** |
| NFR-14 | All endpoints documented in OpenAPI | FastAPI auto-docs | `/docs` endpoint live |
| NFR-15 | PEP 8 / ESLint compliance | `scripts/lint.sh`, CI pipeline | CI passes on every push |
| NFR-16 | Schema supports unlimited architectures | `backend/schema.sql` | SERIAL PRIMARY KEY, no hardcoded limits |
| NFR-17 | Horizontal scaling of backend API | Render deployment | Stateless FastAPI + external PostgreSQL |

---

## Test Coverage by Increment

| Increment | Tests | Coverage |
|-----------|-------|----------|
| Increment 1 | 157 | 94.81% |
| Increment 2 | 187 | 90.31% |
| Increment 3 | 221 | **94.24%** |

*Coverage measured with `pytest tests/ --cov=app --cov-report=term`*

---

## Increment 3 — New Tests Added

The following tests were added in `backend/tests/test_increment3.py` (Issue #90) specifically
to close coverage gaps and prepare for Increment 3 features:

| Test Class | Purpose | Issue |
|------------|---------|-------|
| `TestCreateArchitectureErrors` | Error paths in `POST /architectures` when components are present | #90, #92 |
| `TestUpdateArchitectureErrors` | Duplicate component_id and bad flow reference validation in `PUT /architectures/{id}` | #90, #92 |
| `TestListAndGetErrors` | SQLAlchemy error paths for `GET /architectures` and `GET /architectures/{id}` | #90, #92 |
| `TestDeleteErrors` | SQLAlchemy error on commit in `DELETE /architectures/{id}` | #90, #92 |
| `TestScenariosApiErrors` | Error paths in scenarios router including link_degradation and insider_tampering types | #90, #92 |
| `TestSimulatorEdgeCases` | `propagate_compromise` unknown node, unreachable raise path | #90, #92 |
| `TestCloneFeaturePlaceholder` | xfail stubs for `POST /architectures/{id}/clone` (pending Issue #83) | #90 |
| `TestMitigationFeaturePlaceholder` | xfail stubs for `GET /architectures/{id}/mitigations` (pending Issue #83) | #90 |
| `TestCompareFeaturePlaceholder` | xfail stubs for `GET /architectures/compare` (pending Issue #84) | #90 |
