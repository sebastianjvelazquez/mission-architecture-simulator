# Software Implementation and Testing Document

## Mission-System Security Architecture Simulator

**Group 4**

**Version 1.0 - Increment 1**

**Date:** February 23, 2026

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

---

## 1. Programming Languages

### Backend: Python 3.11+

**Usage:** Core backend API, simulation engine, database operations

**Components:**
- `app/core/main.py` - FastAPI application entry point
- `app/core/simulator.py` - Mission architecture simulation engine using NetworkX
- `app/core/simulate.py` - Simulation API endpoint router
- `app/api/architectures.py` - CRUD endpoints for architectures
- `app/database.py` - SQLAlchemy database connection and session management
- `app/models/` - ORM models and Pydantic schemas

**Rationale:**
- Python is widely used in security and data analysis domains, making it appropriate for a security architecture simulator
- FastAPI provides automatic OpenAPI documentation, async support, and excellent performance
- NetworkX offers comprehensive graph algorithms essential for attack propagation simulation
- Strong ecosystem for testing (pytest) and code quality tools (black, flake8, isort)
- Team familiarity with Python from coursework

### Frontend: TypeScript (via Next.js/React)

**Usage:** User interface, diagram editor, results visualization

**Components:**
- `frontend/app/` - Next.js App Router pages and layouts
- `frontend/components/DiagramEditor.tsx` - React Flow-based architecture editor
- `frontend/components/Navbar.tsx` - Navigation component

**Rationale:**
- TypeScript provides type safety, reducing runtime errors and improving code maintainability
- React is the most popular frontend framework with extensive ecosystem support
- Next.js provides server-side rendering, optimized builds, and easy deployment to Vercel
- Team members had prior exposure to React through coursework

### Database: SQL (PostgreSQL)

**Usage:** Data persistence for architectures, components, and flows

**Components:**
- `backend/schema.sql` - Database schema definition
- `backend/app/models/architecture.py` - SQLAlchemy ORM models

**Rationale:**
- PostgreSQL is a robust, open-source RDBMS with excellent JSON support (JSONB)
- Well-suited for relational data (architectures → components → flows)
- Free tier available on Render for production deployment
- SQLAlchemy provides a mature ORM with migration support via Alembic

### Configuration/DevOps: YAML

**Usage:** CI/CD pipeline configuration, Docker Compose

**Components:**
- `.github/workflows/ci.yml` - GitHub Actions CI pipeline
- `docker-compose.yml` - Local development container orchestration

**Rationale:**
- Industry standard for CI/CD configuration
- Declarative and readable format
- Native support in GitHub Actions and Docker

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

### Database

| Database | Version | Usage |
|----------|---------|-------|
| **PostgreSQL** | 15 | Primary data store for architectures, components, flows |

**Schema Overview:**

```sql
-- Architectures table (parent)
CREATE TABLE architectures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Components table (child of architectures)
CREATE TABLE components (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER REFERENCES architectures(id) ON DELETE CASCADE,
    component_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    criticality INTEGER DEFAULT 5 CHECK (criticality >= 1 AND criticality <= 10),
    position_x FLOAT,
    position_y FLOAT,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flows table (child of architectures, references components)
CREATE TABLE flows (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER REFERENCES architectures(id) ON DELETE CASCADE,
    source_component_id INTEGER REFERENCES components(id),
    target_component_id INTEGER REFERENCES components(id),
    data_type VARCHAR(100),
    cia_requirement VARCHAR(50),
    latency_sensitivity VARCHAR(20),
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Other Technologies

| Technology | Usage |
|------------|-------|
| **Tailwind CSS** | Utility-first CSS framework for styling |
| **Uvicorn** | ASGI server to run FastAPI in production |
| **pytest** | Python testing framework |
| **pytest-cov** | Code coverage plugin for pytest |
| **GitHub Actions** | CI/CD pipeline for automated testing |
| **Docker Compose** | Multi-container development environment |

---

## 3. Execution-based Functional Testing

### Overview

Functional testing verifies that the system meets the functional requirements specified in the RD document. We use **pytest** for backend testing with the **FastAPI TestClient** for API integration tests.

### Test Coverage Summary

| Test File | Tests | Coverage Area |
|-----------|-------|---------------|
| `tests/test_api.py` | 33 | API endpoints, CORS, health check |
| `tests/test_simulator.py` | 61 | Simulation engine, graph algorithms |
| `tests/test_db_queries.py` | 27 | Database operations, eager loading |
| `tests/test_error_handling.py` | 36 | Error responses, validation |
| **Total** | **157** | **94.81% code coverage** |

### Functional Requirements Testing

#### FR-7, FR-8: Node Compromise and Propagation

**Test Class:** `TestPropagateCompromise` (test_simulator.py)

```python
def test_linear_full_chain_from_root(self, linear_sim):
    # Verify compromise propagates through entire chain
    affected = linear_sim.propagate_compromise("A")
    assert affected == {"A", "B", "C"}

def test_linear_middle_node_propagates_downstream_only(self, linear_sim):
    # Verify compromise only affects downstream nodes
    affected = linear_sim.propagate_compromise("B")
    assert affected == {"B", "C"}

def test_cycle_handled_gracefully(self, cycle_sim):
    # Verify circular dependencies don't cause infinite loops
    affected = cycle_sim.propagate_compromise("A")
    assert "A" in affected
    assert "B" in affected
```

**Result:** ✅ All propagation tests pass. The system correctly handles linear chains, branching graphs, isolated nodes, and cycles.

#### FR-9: Mission Score Calculation

**Test Class:** `TestCalculateMissionScore` (test_simulator.py)

```python
def test_baseline_is_100(self, three_node_sim):
    # No affected components = 100% mission success
    score = three_node_sim.calculate_mission_score(set())
    assert score == 100.0

def test_one_of_three_affected(self, three_node_sim):
    # 1 of 3 compromised = 66.67% healthy
    score = three_node_sim.calculate_mission_score({"A"})
    assert score == pytest.approx(66.67, rel=0.01)

def test_all_compromised_is_zero(self, three_node_sim):
    # All compromised = 0% mission success
    score = three_node_sim.calculate_mission_score({"A", "B", "C"})
    assert score == 0.0
```

**Result:** ✅ All score calculation tests pass. Formula correctly computes (healthy/total) * 100.

#### FR-10: Simulation Results

**Test Class:** `TestSimulateEndpoint` (test_api.py)

```python
def test_valid_request_returns_200(self, client):
    r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
    assert r.status_code == 200

def test_response_has_baseline_score(self, client):
    r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
    assert "baseline_score" in r.json()

def test_response_has_affected_components(self, client):
    r = client.post(f"{self.BASE}?scenario_type=node_compromise&target_component_id=sensor-1")
    assert "affected_components" in r.json()
```

**Result:** ✅ All API response tests pass. Simulation endpoint returns complete result schema.

#### FR-14, FR-15: API Documentation and Health Check

**Test Class:** `TestHealthCheck`, `TestAppMetadata` (test_api.py)

```python
def test_docs_accessible(self, client):
    assert client.get("/docs").status_code == 200

def test_openapi_json_accessible(self, client):
    assert client.get("/openapi.json").status_code == 200

def test_health_returns_200(self, client):
    assert client.get("/health").status_code == 200

def test_status_healthy(self, client):
    assert client.get("/health").json()["status"] == "healthy"
```

**Result:** ✅ Health check and documentation endpoints are accessible and return expected responses.

### Test Execution Command

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Coverage Report (Increment 1)

```
Name                         Stmts   Miss   Cover
-------------------------------------------------
app/api/architectures.py        76      7  90.79%
app/core/config.py              12      0 100.00%
app/core/main.py                17      0 100.00%
app/core/schemas.py             37      0 100.00%
app/core/simulate.py            21      0 100.00%
app/core/simulator.py          116      2  98.28%
app/database.py                 37     14  62.16%
app/main.py                      2      0 100.00%
app/models/architecture.py      52      0 100.00%
app/models/schemas.py           71      0 100.00%
app/services/simulator.py        2      0 100.00%
-------------------------------------------------
TOTAL                          443     23  94.81%
```

**Target:** 60% coverage (Increment 1)
**Achieved:** 94.81% coverage ✅

---

## 4. Execution-based Non-Functional Testing

### NFR-1: Performance (100 components < 1 second)

**Test Class:** `TestPerformance` (test_simulator.py)

```python
def test_large_linear_chain_under_1_second(self):
    """100-node linear chain should complete simulation in < 1 second."""
    n = 100
    components = [make_component(f"node-{i}") for i in range(n)]
    flows = [make_flow(f"node-{i}", f"node-{i+1}") for i in range(n - 1)]
    arch = make_arch(components, flows)
    
    start = time.time()
    sim = MissionArchitectureSimulator(arch)
    result = sim.run_simulation("node_compromise", "node-0")
    elapsed = time.time() - start
    
    assert elapsed < 1.0
    assert len(result.affected_components) == n
```

**Result:** ✅ 100-node simulation completes in ~0.02 seconds (well under 1 second threshold).

### NFR-4: Circular Dependency Handling

**Test Method:** `test_cycle_handled_gracefully` (test_simulator.py)

```python
@pytest.fixture
def cycle_sim(self):
    """Graph with cycle: A -> B -> C -> A"""
    components = [make_component("A"), make_component("B"), make_component("C")]
    flows = [
        make_flow("A", "B"),
        make_flow("B", "C"),
        make_flow("C", "A"),  # Creates cycle
    ]
    return MissionArchitectureSimulator(make_arch(components, flows))

def test_cycle_handled_gracefully(self, cycle_sim):
    affected = cycle_sim.propagate_compromise("A")
    assert "A" in affected
    # NetworkX handles cycles internally - no infinite loop
```

**Result:** ✅ Cycles are handled gracefully by NetworkX's built-in visited tracking.

### NFR-7: CORS Middleware

**Test Class:** `TestCORSMiddleware` (test_api.py)

```python
def test_cors_header_present(self, client):
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in response.headers

def test_preflight_returns_200(self, client):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
```

**Result:** ✅ CORS headers are correctly set for cross-origin requests.

### NFR-8: Input Validation

**Test Class:** `TestValidationErrors` (test_error_handling.py)

```python
def test_criticality_below_minimum_returns_422(self, client, mock_db):
    payload = {"name": "Test", "components": [
        {"component_id": "c1", "name": "C1", "component_type": "Sensor", "criticality": 0}
    ]}
    r = client.post("/architectures", json=payload)
    assert r.status_code == 422

def test_duplicate_component_id_returns_422(self, client, mock_db):
    payload = {"name": "Test", "components": [
        {"component_id": "c1", "name": "C1", "component_type": "Sensor"},
        {"component_id": "c1", "name": "C2", "component_type": "Compute"},  # Duplicate
    ]}
    r = client.post("/architectures", json=payload)
    assert r.status_code == 422
```

**Result:** ✅ Pydantic validation catches invalid input and returns 422 errors.

---

## 5. Non-Execution-based Testing

### Code Reviews

All code changes are reviewed through **GitHub Pull Requests** before merging to the main branch. The review process includes:

1. **Automated Checks:** GitHub Actions CI runs all tests and linting on every PR
2. **Manual Review:** At least one team member reviews the code for:
   - Correctness and logic errors
   - Code style consistency
   - Documentation completeness
   - Test coverage for new features

**PR Review Statistics (Increment 1):**
- Total PRs merged: 42
- PRs with required review: 42 (100%)
- Average review time: < 24 hours

### Static Code Analysis

**Backend (Python):**

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **flake8** | Linting, PEP 8 compliance | `.github/workflows/ci.yml` |
| **black** | Code formatting | `pyproject.toml` |
| **isort** | Import sorting | `pyproject.toml` |
| **mypy** | Type checking | `requirements.txt` |

**Linting Commands:**
```bash
flake8 app --count --max-line-length=100 --statistics
black --check app
isort --check-only app
```

**Frontend (TypeScript):**

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **ESLint** | Linting, best practices | `eslint.config.mjs` |
| **TypeScript** | Type checking | `tsconfig.json` |

**Linting Command:**
```bash
npm run lint
```

### Documentation Review

All documentation is reviewed for:
- Technical accuracy
- Completeness
- Spelling and grammar
- Consistency with code

**Documentation Artifacts:**
- API documentation: Auto-generated via Swagger at `/docs`
- Code comments: Docstrings for all public functions
- README files: Setup instructions in each directory
- Database documentation: `docs/DATABASE.md`

### Walkthroughs

Team conducted informal code walkthroughs during weekly sync meetings:

| Date | Topic | Participants |
|------|-------|--------------|
| Feb 10 | Simulator architecture | William, Daniel, Sebastian |
| Feb 15 | Database schema design | Daniel, William, Sebastian |
| Feb 19 | API integration | All team members |
| Feb 22 | Final integration review | All team members |

---

## Appendix: Test Execution Output

```
============================= test session starts ==============================
platform darwin -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /backend
configfile: pyproject.toml
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
collected 157 items

tests/test_api.py ................................                       [ 21%]
tests/test_db_queries.py ...........................                     [ 38%]
tests/test_error_handling.py ....................................        [ 61%]
tests/test_simulator.py ...........................................      [100%]

================================ tests coverage ================================
TOTAL                          443     23  94.81%
======================= 157 passed, 3 warnings in 0.56s ========================
```

---

*Document Version: 1.0*
*Last Updated: February 23, 2026*
*Prepared for: CEN 4090L Software Engineering Lab, Florida State University*
