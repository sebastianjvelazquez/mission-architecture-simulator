# Software Requirements and Design Document

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

1. [Overview](#1-overview)
2. [Functional Requirements](#2-functional-requirements)
3. [Non-functional Requirements](#3-non-functional-requirements)
4. [Use Case Diagram](#4-use-case-diagram)
5. [Class Diagram and Sequence Diagrams](#5-class-diagram-and-sequence-diagrams)
6. [Operating Environment](#6-operating-environment)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Assumptions and Dependencies](#8-assumptions-and-dependencies)
9. [Appendix A: Traceability Matrix](#9-appendix-a-traceability-matrix)

---

## 1. Overview

The **Mission-System Security Architecture Simulator** is a web application that enables
mission planners and security analysts to model system architectures, simulate cyber-attacks,
and evaluate mission impact. Users can visually design mission systems with interconnected
components (sensors, compute nodes, communication links, control systems), run attack
scenarios (node compromise, link degradation, insider threats), and assess how attacks
propagate through dependencies to degrade mission success.

The application provides real-time visualization of attack propagation, calculates mission
degradation scores, and suggests architectural mitigations such as redundancy and network
segmentation. This tool addresses a real-world need in the defense industry for mission
assurance and cybersecurity resilience analysis, providing an accessible, visual, and
interactive way to prototype and analyze security architectures.

**Increment 3 Additions:**
- Scenario persistence API (save, list, delete named attack scenarios)
- Clone architecture endpoint (duplicate an architecture for comparison)
- Mitigation suggester endpoint (automated recommendations based on graph topology)
- Architecture comparison endpoint (delta scoring between two architectures)
- Production deployment to Vercel (frontend) and Render (backend + PostgreSQL)
- 94.24% test coverage (up from 90.31% in Increment 2)

---

## 2. Functional Requirements

### High Priority

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1 | The system shall provide a visual diagram editor where users can add components (Sensor, Compute, CommsLink, Control, Storage, External) to a canvas using drag-and-drop functionality. | High | ✅ Implemented |
| FR-2 | The system shall allow users to draw directed data flows (edges) between components to represent data dependencies. | High | ✅ Implemented |
| FR-3 | The system shall allow users to delete components and data flows from the architecture diagram. | High | ✅ Implemented |
| FR-4 | The system shall allow users to edit component properties including name and criticality level (1-10 scale). | High | ✅ Implemented |
| FR-5 | The system shall provide a "Save Architecture" feature that persists the architecture design (components, flows, positions) to a PostgreSQL database. | High | ✅ Implemented |
| FR-6 | The system shall provide a "Load Architecture" feature that retrieves previously saved architectures from the database. | High | ✅ Implemented |
| FR-7 | The system shall implement a node compromise attack scenario that simulates an attacker compromising a selected component. | High | ✅ Implemented |
| FR-8 | The system shall propagate compromise effects through the dependency graph to all downstream components using graph traversal algorithms. | High | ✅ Implemented |
| FR-9 | The system shall calculate a mission success score as a percentage of healthy (non-compromised) components weighted by criticality. | High | ✅ Implemented |
| FR-10 | The system shall display simulation results including baseline score, compromised score, and list of affected components. | High | ✅ Implemented |

### Medium Priority

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-11 | The system shall display a bar chart comparing baseline and compromised mission scores. | Medium | ✅ Implemented |
| FR-12 | The system shall generate a criticality ranking of components based on user-assigned criticality and graph topology (in-degree). | Medium | ✅ Implemented |
| FR-13 | The system shall provide a step-by-step attack path description showing how compromise propagated through the system. | Medium | ✅ Implemented |
| FR-14 | The system shall provide API documentation via Swagger/OpenAPI at the `/docs` endpoint. | Medium | ✅ Implemented |
| FR-15 | The system shall provide a health check endpoint (`GET /health`) for monitoring and CI/CD integration. | Medium | ✅ Implemented |
| FR-18 | The system shall allow users to save named attack scenarios (type, target, parameters) for later replay. | Medium | ✅ Implemented |
| FR-19 | The system shall allow users to list and delete saved scenarios associated with an architecture. | Medium | ✅ Implemented |
| FR-20 | The system shall validate scenario types against the set of allowed values and return 422 on invalid input. | Medium | ✅ Implemented |
| FR-21 | The system shall support cloning an existing architecture to create an independent copy for mitigation experimentation. | Medium | 🔄 In Progress (Issue #83) |
| FR-22 | The system shall provide mitigation suggestions (redundancy, segmentation) based on graph topology analysis. | Medium | 🔄 In Progress (Issue #83) |
| FR-23 | The system shall provide a comparison endpoint that returns the delta mission score between a baseline and mitigated architecture. | Medium | 🔄 In Progress (Issue #84) |

### Low Priority

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-16 | The system shall support multiple architectures per user session. | Low | ✅ Implemented |
| FR-17 | The system shall preserve component canvas positions when saving and loading architectures. | Low | ✅ Implemented |

---

## 3. Non-functional Requirements

### Performance

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-1 | The system shall complete attack propagation simulation for architectures with up to 100 components in under 1 second. | ✅ Verified |
| NFR-2 | The API response time for simulation requests shall not exceed 500ms for typical architectures (10-50 components). | ✅ Verified |
| NFR-3 | The frontend diagram editor shall maintain 60fps rendering performance during drag-and-drop operations. | ✅ Verified (React Flow) |

### Reliability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-4 | The system shall handle circular dependencies in the architecture graph without entering infinite loops. | ✅ Verified |
| NFR-5 | The system shall gracefully handle database connection failures and provide meaningful error messages. | ✅ Verified |
| NFR-6 | The backend API shall achieve 95%+ uptime during the demonstration period. | 🔄 Target (Render deployment) |

### Security

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-7 | The system shall implement CORS middleware to restrict API access to authorized frontend origins. | ✅ Implemented |
| NFR-8 | The system shall validate all input data using Pydantic schemas before processing. | ✅ Implemented |
| NFR-9 | The system shall not expose internal error details or stack traces to end users. | ✅ Implemented |

### Usability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-10 | The diagram editor shall provide visual feedback (highlighting, color changes) when components are selected or affected by attacks. | ✅ Implemented |
| NFR-11 | Error messages shall be human-readable and actionable. | ✅ Implemented |
| NFR-12 | The system shall be accessible via modern web browsers (Chrome, Firefox, Safari, Edge). | ✅ Verified |

### Maintainability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-13 | The backend codebase shall maintain 60%+ test coverage (Increment 1), increasing to 70% (Increment 2) and 85% (Increment 3). | ✅ **94.24% achieved** |
| NFR-14 | All API endpoints shall be documented in OpenAPI/Swagger format. | ✅ Auto-generated by FastAPI |
| NFR-15 | Code shall follow PEP 8 style guidelines (Python) and ESLint rules (TypeScript). | ✅ Enforced by CI |

### Scalability

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-16 | The database schema shall support storing unlimited architectures with up to 500 components each. | ✅ Implemented |
| NFR-17 | The system architecture shall allow horizontal scaling of the backend API. | ✅ Stateless FastAPI + external DB |

### Deployment

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-18 | The frontend shall be deployed to Vercel and publicly accessible. | 🔄 In Progress (Issue #95) |
| NFR-19 | The backend API shall be deployed to Render and publicly accessible. | 🔄 In Progress (Issue #86) |
| NFR-20 | The production database shall be a managed PostgreSQL instance on Render. | 🔄 In Progress (Issue #86) |
| NFR-21 | The CI/CD pipeline shall automatically run tests on every push to the `Increment3` branch. | ✅ GitHub Actions |

---

## 4. Use Case Diagram

```
                    +--------------------------------------------------+
                    |     Mission Architecture Simulator (v3)          |
                    +--------------------------------------------------+
                                           |
    +------------------+   +------------------+   +------------------+   +------------------+
    |                  |   |                  |   |                  |   |                  |
+---+------+     +-----+----+          +------+---+          +------+---+          +------+---+
| Add      |     | Draw     |          | Edit     |          | Delete   |          | Save     |
| Component|     | Flow     |          | Component|          | Component|          | Arch     |
+----------+     +----------+          +----------+          +----------+          +----------+
                                           |
                              +------------+------------+
                              |                         |
                         +----+----+               +----+----+
                         | Load    |               | Clone   |
                         | Arch    |               | Arch    |
                         +---------+               +---------+
                              |
                    +---------+-----------+
                    |                     |
               +----+----+          +-----+----+
               | Save    |          | List     |
               | Scenario|          | Scenarios|
               +---------+          +----------+
                    |
          +---------+----------+
          |                    |
     +----+----+          +----+----+
     |  Run    |          | View    |
     |Simulation|          |Mitigations|
     +---------+          +---------+
          |
     +----+----+
     | Compare |
     |  Archs  |
     +---------+

    Actor: Mission Planner / Security Analyst
```

### Use Cases Summary (Increment 3)

| Use Case | Description | Status |
|----------|-------------|--------|
| UC-1 | Add Component | ✅ Implemented |
| UC-2 | Draw Data Flow | ✅ Implemented |
| UC-3 | Edit Component | ✅ Implemented |
| UC-4 | Delete Component | ✅ Implemented |
| UC-5 | Save Architecture | ✅ Implemented |
| UC-6 | Load Architecture | ✅ Implemented |
| UC-7 | Run Simulation | ✅ Implemented |
| UC-8 | View Results | ✅ Implemented |
| UC-9 | Save Scenario | ✅ Implemented |
| UC-10 | List Scenarios | ✅ Implemented |
| UC-11 | Delete Scenario | ✅ Implemented |
| UC-12 | Clone Architecture | 🔄 In Progress |
| UC-13 | View Mitigations | 🔄 In Progress |
| UC-14 | Compare Architectures | 🔄 In Progress |

---

## 5. Class Diagram and Sequence Diagrams

### 5.1 Class Diagram

```
+------------------------+       +------------------------+
|    Architecture        |       |   Component            |
+------------------------+       +------------------------+
| - id: int              |       | - id: int              |
| - name: str            |  1..* | - architecture_id: int |
| - description: str     |<------| - component_id: str    |
| - properties: JSONB    |       | - name: str            |
| - created_at: datetime |       | - component_type: str  |
| - updated_at: datetime |       | - criticality: int     |
+------------------------+       | - position_x: float    |
          |                      | - position_y: float    |
          | 1..*                 | - properties: JSONB    |
          v                      +------------------------+
+------------------------+
|    Flow                |
+------------------------+
| - id: int              |
| - architecture_id: int |
| - source_component_id  |
| - target_component_id  |
| - data_type: str       |
| - cia_requirement: str |
| - latency_sensitivity  |
+------------------------+
          |
          | 1..*
          v
+------------------------+       +------------------------+
|    Scenario            |       | SimulationResult       |
+------------------------+       +------------------------+
| - id: int              |       | - id: int              |
| - architecture_id: int |  1..* | - scenario_id: int     |
| - scenario_type: str   |<------| - baseline_score: float|
| - target_component_id  |       | - compromised_score    |
| - parameters: JSONB    |       | - affected_components  |
| - created_at: datetime |       | - attack_path: JSONB   |
+------------------------+       | - explanation: str     |
                                 +------------------------+

+-------------------------------+
| MissionArchitectureSimulator  |
+-------------------------------+
| - graph: DiGraph              |
| - architecture: Schema        |
| + run_simulation()            |
| + propagate_compromise()      |
| + calculate_mission_score()   |
| + get_component_metadata()    |
| + get_criticality_ranking()   |
+-------------------------------+
```

### 5.2 Sequence Diagram — Run Simulation

```
User        Frontend         Backend API        Simulator        Database
 |              |                 |                  |               |
 |--Click Run-->|                 |                  |               |
 |              |--POST /simulate>|                  |               |
 |              |                 |--GET arch------->|               |
 |              |                 |                  |--Query DB---->|
 |              |                 |                  |<--Arch data---|
 |              |                 |--build graph---->|               |
 |              |                 |--run_simulation->|               |
 |              |                 |<--results--------|               |
 |              |<---JSON 200-----|                  |               |
 |<--Display----|                 |                  |               |
```

### 5.3 Sequence Diagram — Save Scenario

```
User        Frontend         Backend API                   Database
 |              |                 |                              |
 |--Click Save->|                 |                              |
 |              |--POST /scenarios|                              |
 |              |                 |--Validate payload----------->|
 |              |                 |--Verify arch exists--------->|
 |              |                 |--Verify component belongs--->|
 |              |                 |--INSERT INTO scenarios------>|
 |              |                 |<--Scenario row---------------|
 |              |<---JSON 201-----|                              |
 |<--Feedback---|                 |                              |
```

---

## 6. Operating Environment

| Component | Technology | Version | Hosting |
|-----------|-----------|---------|---------|
| Frontend | Next.js + React | 16.1.6 | Vercel (production) / localhost:3000 (dev) |
| Backend API | FastAPI + Uvicorn | 0.109.0 | Render (production) / localhost:8000 (dev) |
| Database | PostgreSQL | 15 | Render managed DB (prod) / Docker (dev) |
| Simulation Engine | NetworkX | 3.2.1 | Embedded in backend |
| CI/CD | GitHub Actions | — | GitHub |
| Containers (dev) | Docker Compose | — | Local |
| Python Runtime | CPython | 3.11 (Docker) | — |
| Node Runtime | Node.js | 20-alpine | — |

---

## 7. Deployment Architecture

### 7.1 Production Topology

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                             │
└────────────────┬────────────────────────┬───────────────────┘
                 │                        │
        ┌────────┴────────┐      ┌────────┴────────┐
        │   Vercel CDN    │      │  Render Backend │
        │                 │      │                 │
        │  Next.js App    │      │  FastAPI API    │
        │  (Frontend)     │<---->│  Uvicorn ASGI   │
        │                 │ HTTPS│                 │
        └─────────────────┘      └────────┬────────┘
                                          │
                                 ┌────────┴────────┐
                                 │ Render PostgreSQL│
                                 │ Managed Database │
                                 │ (Private network)│
                                 └─────────────────┘
```

### 7.2 Environment Variables

**Frontend (Vercel):**

| Variable | Value | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | `https://<backend>.onrender.com` | Backend API base URL |

**Backend (Render):**

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | `postgresql://...` | Render internal DB connection string |
| `FRONTEND_URL` | `https://<app>.vercel.app` | Allowed CORS origin |
| `ENVIRONMENT` | `production` | Enables production settings |

### 7.3 CI/CD Pipeline

```
Developer pushes to Increment3 branch
           │
           ▼
GitHub Actions triggered
           │
    ┌──────┴────────┐
    │  Install deps  │
    │  (Python venv) │
    └──────┬────────┘
           │
    ┌──────┴────────┐
    │  Run pytest    │
    │  --cov=app     │
    └──────┬────────┘
           │
    ┌──────┴────────┐
    │ Coverage ≥ 85% │ <-- fails if below threshold
    └──────┬────────┘
           │
    ┌──────┴────────┐
    │  Lint check    │
    │  (flake8)      │
    └──────┬────────┘
           │
           ▼
       ✅ CI Passes
```

---

## 8. Assumptions and Dependencies

### Assumptions

1. Users have modern web browsers (Chrome 120+, Firefox 120+, Safari 17+, Edge 120+).
2. The Render free tier cold start delay (~30 seconds) is acceptable for demonstration.
3. Architecture data is not sensitive; no authentication layer is required for the prototype.
4. Canvas positions are stored as floats; precision beyond 2 decimal places is not needed.
5. The mission score formula (weighted average of healthy components) is an acceptable proxy for real mission assurance metrics.

### Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Clone/Mitigation endpoint | William Ohonba (Issue #83) | 🔄 In Progress |
| Compare endpoint | William Ohonba (Issue #84) | 🔄 In Progress |
| Backend deployment to Render | William Ohonba (Issue #86) | 🔄 In Progress |
| Frontend deployment to Vercel | Sebastian Velazquez (Issue #95) | 🔄 In Progress |
| Frontend architecture editor enhancements | Samson Shields (Issue #81) | 🔄 In Progress |

---

## 9. Appendix A: Traceability Matrix

See [docs/TRACEABILITY.md](TRACEABILITY.md) for the full requirements traceability matrix
mapping each FR/NFR to its implementation files and test cases.
