# Software Implementation and Testing Document

## Mission-System Security Architecture Simulator

**Group 4**

**Version 3.0 - Increment 3**

**Date:** April 27, 2026

---

**Authors:**

- Samson Shields (sjs23g) - Frontend Lead
- William Ohonba (weo24) - Backend/Simulation Lead
- Daniel Gonzalez (dg23c) - Database/Integration Lead
- Sebastian Velazquez (sv24m) - Testing/DevOps/Documentation Lead

---

## Table of Contents

1. [Programming Languages](#1-programming-languages)
2. [Platforms, APIs, Databases, and Other Technologies](#2-platforms-apis-databases-and-other-technologies)
3. [Execution-based Functional Testing](#3-execution-based-functional-testing)
4. [Execution-based Non-Functional Testing](#4-execution-based-non-functional-testing)
5. [Non-Execution-based Testing](#5-non-execution-based-testing)
6. [API Documentation](#6-api-documentation)
7. [Deployment Guide](#7-deployment-guide)
8. [Known Issues and Limitations](#8-known-issues-and-limitations)
9. [Future Work](#9-future-work)

---

## 1. Programming Languages

### Backend: Python 3.11+

**Usage:** Core backend API, simulation engine, database operations

**Components:**
- `app/core/main.py` — FastAPI application entry point
- `app/core/simulator.py` — Mission architecture simulation engine using NetworkX
- `app/core/simulate.py` — Simulation API endpoint router
- `app/api/architectures.py` — CRUD endpoints for architectures
- `app/api/scenarios.py` — Scenario persistence and simulation result endpoints
- `app/database.py` — SQLAlchemy database connection and session management
- `app/models/` — ORM models and Pydantic schemas

**Rationale:** FastAPI provides automatic OpenAPI documentation and async support.
NetworkX offers comprehensive graph algorithms essential for attack propagation.
pytest has an excellent testing ecosystem with coverage reporting.

### Frontend: TypeScript (via Next.js/React)

**Usage:** User interface, diagram editor, results visualization

**Components:**
- `frontend/app/` — Next.js App Router pages and layouts
- `frontend/app/dashboard/page.tsx` — Main architecture editor and simulation runner
- `frontend/components/NavbarDashboard.tsx` — Dashboard navigation
- `frontend/components/NavbarEditor.tsx` — Editor navigation

**Rationale:** TypeScript provides type safety. Next.js enables easy deployment to Vercel
with optimized builds and server-side rendering.

### Database: SQL (PostgreSQL)

**Usage:** Data persistence for architectures, components, flows, scenarios, and simulation results

**Components:**
- `backend/schema.sql` — Production database schema
- `backend/test_data.sql` — Development seed data
- `backend/app/models/architecture.py` — SQLAlchemy ORM models

**Rationale:** PostgreSQL's JSONB support is used for flexible `properties` and `parameters`
columns. Render offers a free managed PostgreSQL 15 instance.

### Configuration/DevOps: YAML

**Usage:** CI/CD pipeline configuration, Docker Compose

**Components:**
- `.github/workflows/ci.yml` — GitHub Actions CI pipeline
- `docker-compose.yml` — Local development container orchestration

---

## 2. Platforms, APIs, Databases, and Other Technologies

### Platforms

| Platform | Component | Purpose |
|----------|-----------|---------|
| **Vercel** | Frontend | Production hosting for Next.js application |
| **Render** | Backend + Database | Production hosting for FastAPI and PostgreSQL |
| **GitHub** | All | Version control, issue tracking, CI/CD |
| **Docker** | Development | Containerized local development environment |

### APIs and Frameworks

| Technology | Version | Component | Purpose |
|------------|---------|-----------|---------|
| **FastAPI** | 0.109.0 | Backend | REST API framework with automatic OpenAPI docs |
| **React Flow** | latest | Frontend | Interactive node-based diagram editor |
| **Recharts** | latest | Frontend | Data visualization (bar charts for scores) |
| **NetworkX** | 3.2.1 | Backend | Graph algorithms for attack propagation |
| **SQLAlchemy** | 2.0.25 | Backend | Object-Relational Mapper for PostgreSQL |
| **Pydantic** | 2.5.3 | Backend | Request/response validation and serialization |
| **Tailwind CSS** | 3.x | Frontend | Utility-first CSS framework |
| **Uvicorn** | latest | Backend | ASGI server for FastAPI |

### Database

| Database | Version | Usage |
|----------|---------|-------|
| **PostgreSQL** | 15 | Primary data store for architectures, components, flows, scenarios |
| **SQLite (in-memory)** | built-in | Test environment (via SQLAlchemy) |

---

## 3. Execution-based Functional Testing

### Overview

Functional testing verifies that the system meets the functional requirements. We use
**pytest** for backend testing with the **FastAPI TestClient** for API integration tests
and a SQLite in-memory database to avoid PostgreSQL dependency in CI.

### Test Coverage Summary (Increment 3)

| Test File | Tests | Coverage Area |
|-----------|-------|---------------|
| `tests/test_api.py` | 33 | API endpoints, CORS, health check, simulation |
| `tests/test_simulator.py` | 61 | Simulation engine, graph algorithms, propagation |
| `tests/test_db_queries.py` | 27 | Database operations, eager loading, relationships |
| `tests/test_error_handling.py` | 36 | Error responses, IntegrityError, SQLAlchemyError |
| `tests/test_scenarios_api.py` | 30 | Scenario CRUD, simulation result storage |
| `tests/test_architecture_delete_api.py` | 14 | DELETE endpoint edge cases |
| `tests/test_architecture_update_api.py` | 20 | PUT endpoint validation |
| `tests/test_increment3.py` | **34** | **Increment 3 error paths + xfail placeholders** |
| **Total** | **221** | **94.24% code coverage** |

### Increment 3 New Tests (`tests/test_increment3.py`)

#### TestCreateArchitectureErrors
Tests error paths in `POST /architectures` when the payload includes components.
The existing tests only used `MINIMAL_PAYLOAD` (no components), leaving the
Component and Flow constructor lines in `architectures.py` uncovered.

```
test_integrity_error_during_component_flush_returns_409
test_sqlalchemy_error_during_component_flush_returns_500
test_rollback_called_on_component_integrity_error
test_sqlalchemy_error_on_commit_returns_500
```

#### TestUpdateArchitectureErrors
Tests validation paths unique to the PUT endpoint: duplicate `component_id` and
flow references to components not in the payload.

```
test_update_nonexistent_architecture_returns_404
test_update_duplicate_component_id_returns_422
test_update_flow_source_not_in_components_returns_422
test_update_flow_target_not_in_components_returns_422
test_update_successful_replaces_components
test_update_integrity_error_returns_409
test_update_sqlalchemy_error_returns_500
```

#### TestListAndGetErrors
Tests SQLAlchemy error paths for the list and get endpoints.

```
test_list_sqlalchemy_error_returns_500
test_get_sqlalchemy_error_returns_500
test_get_nonexistent_architecture_returns_404
test_list_with_skip_and_limit
test_list_invalid_skip_returns_422
test_list_invalid_limit_returns_422
```

#### TestDeleteErrors
Tests the two try-blocks in the delete endpoint: the query step and the commit step.

```
test_delete_nonexistent_returns_404
test_delete_sqlalchemy_error_on_query_returns_500
test_delete_sqlalchemy_error_on_commit_returns_500
test_delete_successful_returns_204
```

#### TestScenariosApiErrors
Tests scenario endpoint paths including all three scenario types and error conditions.

```
test_get_scenarios_for_nonexistent_architecture_returns_404
test_create_scenario_for_nonexistent_architecture_returns_404
test_create_scenario_invalid_type_returns_422
test_create_scenario_with_link_degradation_type
test_create_scenario_with_insider_tampering_type
test_delete_scenario_returns_204
test_delete_nonexistent_scenario_returns_404
test_create_scenario_for_nonexistent_component_returns_422
```

#### TestSimulatorEdgeCases
Tests simulator paths not hit by the existing test suite.

```
test_propagate_compromise_unknown_node_returns_empty_set
test_get_component_metadata_unknown_raises
test_run_simulation_unimplemented_scenario_raises
test_calculate_mission_score_with_all_nodes_affected
test_calculate_mission_score_healthy_clamped_when_extra_ids_given
```

#### Placeholder Tests (xfail — Increment 3 features pending)

```
TestCloneFeaturePlaceholder (3 tests)   — POST /architectures/{id}/clone
TestMitigationFeaturePlaceholder (3 tests) — GET /architectures/{id}/mitigations
TestCompareFeaturePlaceholder (3 tests)  — GET /architectures/compare
```

These use `@pytest.mark.xfail(strict=False)` so they appear as expected failures
in CI output without blocking the build. Remove the mark when endpoints are implemented.

### How to Run Tests

```bash
cd backend
source venv/bin/activate              # activate virtualenv (macOS/Linux)
pytest tests/ --cov=app --cov-report=term
```

For a specific test file:
```bash
pytest tests/test_increment3.py -v
```

For a coverage HTML report:
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Coverage Report (Increment 3)

```
Name                         Stmts   Miss   Cover   Missing
-----------------------------------------------------------
app/api/architectures.py       138      1  99.28%   327
app/api/scenarios.py           159     25  84.28%   (slow-query listeners)
app/core/config.py              12      0 100.00%
app/core/main.py                21      0 100.00%
app/core/schemas.py             37      0 100.00%
app/core/simulate.py            21      0 100.00%
app/core/simulator.py          116      1  99.14%   322
app/database.py                 37     14  62.16%   (DB event listeners)
app/main.py                      2      0 100.00%
app/models/architecture.py      78      0 100.00%
app/models/schemas.py           89      0 100.00%
app/services/simulator.py        2      0 100.00%
-----------------------------------------------------------
TOTAL                          712     41  94.24%
```

**Note on uncovered lines:**
- `app/database.py` lines 32, 37-47, 61-62, 67-73: SQLAlchemy event listeners for slow
  query monitoring. These fire only on real PostgreSQL connections with the `ENVIRONMENT`
  env var set. They are not testable with the SQLite in-memory test setup.
- `app/api/architectures.py` line 327: SQLAlchemy error path in list endpoint covered by
  mock tests; line 327 specifically is the logger call inside the except block.
- `app/core/simulator.py` line 322: `propagate_compromise` warning for unknown nodes
  (covered by `TestSimulatorEdgeCases::test_propagate_compromise_unknown_node_returns_empty_set`).

---

## 4. Execution-based Non-Functional Testing

### Performance Testing

#### NFR-1: Simulation completes in <1 second for 100 nodes

```python
# From tests/test_simulator.py: TestPerformance
def test_large_graph_performance():
    # Creates 100-node architecture and runs node_compromise
    # Asserts total time < 1.0 seconds
```

**Result:** Passed. NetworkX BFS traversal on 100 nodes completes in <50ms.

#### NFR-2: API response <500ms for 10-50 components

**Result:** Verified manually and via test timer assertions. Typical response is 20-80ms
for architectures in the expected range.

#### NFR-4: Circular dependency handling

```python
# From tests/test_simulator.py: TestCircularDependencies
# Creates A→B→C→A cycle and verifies simulation terminates correctly
```

**Result:** Passed. NetworkX's BFS does not revisit visited nodes.

---

## 5. Non-Execution-based Testing

### Code Review Process

All Increment 3 code merged to `Increment3` via pull requests on GitHub. Each PR required:
1. All CI checks to pass (pytest, coverage ≥ 85%, lint)
2. At least one team member review

### Linting and Static Analysis

```bash
./scripts/lint.sh       # runs flake8 (Python) + eslint (TypeScript)
```

All backend code passes flake8 with the configuration in `backend/pyproject.toml`.

### Documentation Review

All public API endpoints are documented in the FastAPI auto-generated Swagger UI at
`/docs`. Each endpoint includes:
- Summary string
- Request body schema
- Response schema
- Error codes

---

## 6. API Documentation

All endpoints are documented via FastAPI's auto-generated Swagger UI at `/docs` when the
backend is running. Below is a summary.

### Architecture Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `POST` | `/architectures` | Create new architecture with inline components and flows | 201, 409, 422, 500 |
| `GET` | `/architectures` | List all architectures (supports `skip` and `limit`) | 200, 422, 500 |
| `GET` | `/architectures/{id}` | Get architecture with components and flows | 200, 404, 500 |
| `PUT` | `/architectures/{id}` | Replace components and flows in an architecture | 200, 404, 409, 422, 500 |
| `DELETE` | `/architectures/{id}` | Delete architecture and all children | 204, 404, 500 |

### Scenario Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `POST` | `/architectures/{id}/scenarios` | Save a named scenario for replay | 201, 404, 409, 422, 500 |
| `GET` | `/architectures/{id}/scenarios` | List saved scenarios for an architecture | 200, 404, 500 |
| `DELETE` | `/architectures/{id}/scenarios/{sid}` | Delete a saved scenario | 204, 404, 500 |

### Simulation Result Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `POST` | `/scenarios/{sid}/results` | Save simulation output for a scenario | 201, 404, 500 |
| `GET` | `/scenarios/{sid}/results` | List all results for a scenario | 200, 404, 500 |
| `GET` | `/scenarios/{sid}/results/{rid}` | Get a specific simulation result | 200, 404, 500 |
| `GET` | `/scenarios/{sid}/results/{rid}/export` | Export result as CSV | 200, 404 |

### Simulation Endpoint

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `POST` | `/simulate` | Run a simulation and return results | 200, 422, 500 |

### System Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `GET` | `/health` | Health check | 200 |

### Allowed Scenario Types

| Type | Stored | Simulated |
|------|--------|-----------|
| `node_compromise` | ✅ | ✅ |
| `link_degradation` | ✅ | ❌ (Increment 3 WIP) |
| `insider_tampering` | ✅ | ❌ (Increment 3 WIP) |

---

## 7. Deployment Guide

See [docs/DEPLOYMENT.md](DEPLOYMENT.md) for the complete step-by-step guide to deploy
to Vercel (frontend) and Render (backend + PostgreSQL).

### Quick Reference

**Local Development:**
```bash
docker-compose up --build    # starts backend (8000), frontend (3000), postgres (5432)
```

**Run Tests:**
```bash
cd backend && source venv/bin/activate && pytest tests/ --cov=app
```

**Production:**
- Frontend: deploy `frontend/` directory to Vercel
- Backend: deploy `backend/` directory to Render (Web Service, Python 3.11)
- Database: Render managed PostgreSQL 15, apply `backend/schema.sql`

---

## 8. Known Issues and Limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| Render free tier cold start (~30s) | First request after idle period is slow | User waits; subsequent requests are fast |
| SQLite event listeners not testable | `app/database.py` lines 37-47 remain uncovered | Acceptable — slow-query monitoring only fires on real PostgreSQL |
| `link_degradation` and `insider_tampering` scenarios stored but not simulated | Calling `/simulate` with these types returns 422 | Use `node_compromise` for live simulation; other types are stored for future use |
| No authentication layer | Any user can read/modify any architecture | Acceptable for prototype; add JWT in production |
| Clone/Mitigation/Compare endpoints not yet merged | xfail placeholder tests in CI | Will be resolved when Issue #83 and #84 PRs are merged |

---

## 9. Future Work

| Feature | Description | Priority |
|---------|-------------|----------|
| `link_degradation` simulation | Implement graph edge weight degradation in simulator | High |
| `insider_tampering` simulation | Implement insider threat propagation model | High |
| Architecture comparison UI | Frontend panel showing delta scores | Medium |
| User authentication | JWT-based auth with user-scoped architectures | Medium |
| Export architecture as PDF/PNG | One-click export of the diagram | Low |
| Undo/Redo in diagram editor | Standard Ctrl+Z behavior in the canvas | Low |
| Alembic migrations | Replace manual `schema.sql` with versioned migrations | Low |
| WebSocket live simulation | Real-time propagation animation frame-by-frame | Low |
