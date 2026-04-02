# Software Requirements and Design Document

## Mission-System Security Architecture Simulator

**Group 4**

**Version 2.0 - Increment 2**

**Date:** March 23, 2026

---

**Authors:**

- Samson Shields (sjs23g) - Frontend Lead
- William Ohonba (weo24) - Backend/Simulation Lead
- Daniel Gonzalez (dg23c) - Database/Integration Lead
- Sebastian Velazquez (sv24m) - Testing/DevOps/Documentation Lead

---

## Table of Contents

1. [Overview](#overview)
2. [Functional Requirements](#functional-requirements)
3. [Non-functional Requirements](#non-functional-requirements)
4. [Use Case Diagram](#use-case-diagram)
5. [Use Case Descriptions](#use-case-descriptions)
6. [Class Diagram and Sequence Diagrams](#class-diagram-and-sequence-diagrams)
7. [Operating Environment](#operating-environment)
8. [Assumptions and Dependencies](#assumptions-and-dependencies)

---

## 1. Overview

The **Mission-System Security Architecture Simulator** is a web application that enables mission planners and security analysts to model system architectures, simulate cyber-attacks, and evaluate mission impact. Increment 2 expands upon the Increment 1 foundation by:

- **Wiring** the frontend to the backend (save, load, and simulate using real network requests)
- **Adding** link degradation and insider tampering attack scenarios
- **Implementing** CIA-aware (Confidentiality, Integrity, Availability) attack propagation
- **Deploying** the application publicly (frontend on Vercel, backend on Render)
- **Enabling** scenario management: save, list, and export simulation results
- **Increasing** test coverage to 70%+ with integration tests

The application continues to serve the defense and cybersecurity domains, giving analysts a visual, interactive environment to prototype and stress-test mission architectures against realistic threat models.

---

## 2. Functional Requirements

### Retained from Increment 1 (No Change)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | The system shall provide a visual diagram editor where users can add components to a canvas using drag-and-drop. | High |
| FR-2 | The system shall allow users to draw directed data flows (edges) between components. | High |
| FR-3 | The system shall allow users to delete components and data flows. | High |
| FR-4 | The system shall allow users to edit component properties including name and criticality (1-10). | High |
| FR-7 | The system shall implement a node compromise attack scenario. | High |
| FR-8 | The system shall propagate compromise effects through the dependency graph. | High |
| FR-9 | The system shall calculate a mission success score as a percentage of healthy components. | High |
| FR-10 | The system shall display simulation results including baseline score, compromised score, and affected components. | High |
| FR-14 | The system shall provide API documentation via Swagger/OpenAPI at `/docs`. | Medium |
| FR-15 | The system shall provide a health check endpoint (`GET /health`). | Medium |

### New in Increment 2

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-18 | The system shall wire the Save button to send a POST request to `/architectures` with the full architecture (components, flows, CIA properties). | High |
| FR-19 | The system shall wire the Load button to fetch saved architectures from `GET /architectures` and restore the canvas. | High |
| FR-20 | The system shall provide a "Run Simulation" button that sends a POST request to `/architectures/{id}/simulate` and navigates to the results dashboard. | High |
| FR-21 | The system shall display real simulation results on the dashboard (replacing hardcoded sample data). | High |
| FR-22 | The system shall implement a **link degradation** attack scenario that targets a communication edge and calculates downstream connectivity loss. | High |
| FR-23 | The system shall implement an **insider tampering** attack scenario that simulates data corruption originating from a compromised node. | High |
| FR-24 | The system shall factor CIA requirements (confidentiality, integrity, availability) into attack propagation logic. | High |
| FR-25 | The system shall allow users to set CIA requirement, data type, and latency sensitivity on data flow edges via a properties panel. | Medium |
| FR-26 | The system shall provide `PUT /architectures/{id}` to update an existing architecture without creating a duplicate. | High |
| FR-27 | The system shall provide `DELETE /architectures/{id}` to remove an architecture and all its associated data. | High |
| FR-28 | The system shall save simulation scenarios and results to a `scenarios` table in the database. | Medium |
| FR-29 | The system shall provide `GET /architectures/{id}/scenarios` to list all saved scenarios for an architecture. | Medium |
| FR-30 | The system shall provide `POST /scenarios/{id}/clone` to duplicate a scenario for side-by-side comparison. | Low |
| FR-31 | The system shall provide export endpoints (`GET /scenarios/{id}/export?format=json` and `?format=csv`) for sharing results. | Medium |
| FR-32 | The system shall display a side-by-side scenario comparison view on the dashboard. | Low |
| FR-33 | The simulation result shall include a structured `attack_path` list suitable for step-by-step visualization. | Medium |
| FR-34 | The system shall be deployed publicly: frontend on Vercel, backend API on Render. | High |

---

## 3. Non-functional Requirements

### Performance

| ID | Requirement |
|----|-------------|
| NFR-1 | The system shall complete attack propagation simulation for architectures with up to 100 components in under 1 second. *(retained)* |
| NFR-2 | The API response time for simulation requests shall not exceed 500ms for typical architectures (10–50 components). *(retained)* |
| NFR-3 | The frontend diagram editor shall maintain 60fps rendering during drag-and-drop. *(retained)* |
| NFR-18 | Database queries for architectures with up to 100 components and 200 flows shall complete in under 200ms. |
| NFR-19 | The deployed backend on Render (free tier) shall respond to health checks within 30 seconds after a cold start. |

### Reliability

| ID | Requirement |
|----|-------------|
| NFR-4 | The system shall handle circular dependencies in the architecture graph without infinite loops. *(retained)* |
| NFR-5 | The system shall gracefully handle database connection failures with meaningful error messages. *(retained)* |
| NFR-6 | The backend API shall achieve 95%+ uptime during the demonstration period. *(retained)* |
| NFR-20 | All new CRUD operations shall use database transactions with rollback on failure. |

### Security

| ID | Requirement |
|----|-------------|
| NFR-7 | The system shall implement CORS middleware restricting API access to authorized origins (localhost and Vercel domain). *(retained)* |
| NFR-8 | The system shall validate all input data with Pydantic schemas before processing. *(retained)* |
| NFR-9 | The system shall not expose internal error details or stack traces to end users. *(retained)* |
| NFR-21 | The deployed backend shall use HTTPS for all API communication. |

### Usability

| ID | Requirement |
|----|-------------|
| NFR-10 | The diagram editor shall provide visual feedback when components are selected or affected. *(retained)* |
| NFR-11 | Error messages shall be human-readable and actionable. *(retained)* |
| NFR-12 | The system shall be accessible via modern web browsers (Chrome, Firefox, Safari, Edge). *(retained)* |
| NFR-22 | Loading spinners shall be shown during all async API calls (save, load, simulate). |
| NFR-23 | Mission score on dashboard shall be color-coded: green (>80%), yellow (50–80%), red (<50%). |

### Maintainability

| ID | Requirement |
|----|-------------|
| NFR-13 | The backend codebase shall maintain **70%+ test coverage** in Increment 2, increasing to 85% in Increment 3. |
| NFR-14 | All API endpoints shall be documented in OpenAPI/Swagger format. *(retained)* |
| NFR-15 | Code shall follow PEP 8 style guidelines (Python) and ESLint rules (TypeScript). *(retained)* |
| NFR-24 | The CI pipeline shall enforce the 70% coverage threshold and fail the build if coverage drops below it. |

### Scalability

| ID | Requirement |
|----|-------------|
| NFR-16 | The database schema shall support storing unlimited architectures with up to 500 components each. *(retained)* |
| NFR-17 | The system architecture shall allow horizontal scaling of the backend API. *(retained)* |
| NFR-25 | Database indexes shall be created on `scenario_type` and `architecture_id` in the `scenarios` table. |

---

## 4. Use Case Diagram

```
                    +--------------------------------------------------+
                    |    Mission Architecture Simulator (Increment 2)   |
                    +--------------------------------------------------+
                                            |
     +------------------+   +------------------+   +------------------+
     |                  |   |                  |   |                  |
+----+----+        +----+----+            +----+----+            +----+----+
|  Add    |        |  Draw   |            |  Edit   |            | Delete  |
|Component|        |  Flow   |            |Properties|           |Component|
+---------+        +---------+            +---------+            +---------+
     |                  |                      |                      |
     +------------------+----------------------+----------------------+
                                        |
                    +-------------------+-------------------+
                    |                                       |
               +----+----+                           +----+----+
               |  Save   |                           |  Load   |
               |  Arch   |                           |  Arch   |
               +---------+                           +---------+
                    |                                       |
                    +-------------------+-------------------+
                                        |
               +------------------------+------------------------+
               |                        |                        |
          +----+-----+           +------+-----+          +-------+----+
          |   Run    |           |  Compare   |          |   Export   |
          |Simulation|           | Scenarios  |          |  Results   |
          +----------+           +------------+          +------------+
               |
          +----+----+
          |  View   |
          | Results |
          +---------+

    Actor: Mission Planner / Security Analyst
```

### Use Cases Summary (Increment 2)

| Use Case | Description | Status |
|----------|-------------|--------|
| UC-1: Add Component | User drags a component type onto the canvas | Retained |
| UC-2: Draw Data Flow | User draws a directed edge between two components | Retained |
| UC-3: Edit Component | User modifies name, criticality | Retained |
| UC-4: Delete Component | User removes a component and its flows | Retained |
| UC-5: Save Architecture | User clicks Save; frontend POSTs to `/architectures` | Updated (live API) |
| UC-6: Load Architecture | User selects a saved architecture; frontend fetches from API | Updated (live API) |
| UC-7: Run Simulation | User selects scenario type and target; frontend calls simulate endpoint | Updated (live API) |
| UC-8: View Results | User views real simulation results on the dashboard | Updated (real data) |
| UC-9: Edit CIA Properties | User double-clicks an edge to set CIA requirement | New |
| UC-10: Compare Scenarios | User views two simulation results side-by-side | New |
| UC-11: Export Results | User downloads scenario results as JSON or CSV | New |

---

## 5. Use Case Descriptions

### UC-5: Save Architecture

**Actor:** Mission Planner
**Precondition:** User has added at least one component to the canvas.
**Main Flow:**
1. User clicks the "Save" button in the editor toolbar.
2. If the architecture has no name, a modal prompts the user to provide one.
3. Frontend collects all nodes (components) and edges (flows) from React Flow state.
4. Frontend transforms data to the API schema (component_id, name, type, criticality, position, cia_requirement on flows).
5. Frontend sends `POST /architectures` with the full payload.
6. Backend validates, persists to PostgreSQL, and returns the new architecture ID.
7. Frontend stores the architecture ID in state and shows a success toast.
**Alternate Flow (Save Fails):** Backend returns an error → frontend shows an error message.
**Postcondition:** Architecture is persisted in the database with a unique integer ID.

---

### UC-7: Run Simulation

**Actor:** Mission Planner
**Precondition:** Architecture has been saved (has a database ID).
**Main Flow:**
1. User clicks "Run Simulation" in the toolbar.
2. A modal opens with two dropdowns: scenario type and target component.
3. User selects scenario type (node_compromise, link_degradation, or insider_tampering) and a target component.
4. User clicks "Run".
5. Frontend sends `POST /architectures/{id}/simulate?scenario_type=...&target_component_id=...`.
6. Backend loads the architecture, runs the scenario, and returns simulation results.
7. Frontend navigates to the dashboard page with the results data.
**Alternate Flow (Unsaved Architecture):** If architecture has no ID, user is prompted to save first.
**Postcondition:** Simulation results are displayed on the dashboard.

---

### UC-9: Edit CIA Properties on Edge

**Actor:** Mission Planner
**Precondition:** At least one edge (data flow) exists on the canvas.
**Main Flow:**
1. User double-clicks an edge.
2. An edge properties panel opens showing current label, data_type, cia_requirement, and latency_sensitivity.
3. User selects CIA requirement from dropdown: confidentiality, integrity, or availability.
4. User confirms; edge state is updated and visual label reflects the new CIA type.
5. When the architecture is saved, CIA properties are included in the POST payload.
**Postcondition:** Edge CIA requirement is stored in the architecture and factored into simulations.

---

## 6. Class Diagram and Sequence Diagrams

### 6.1 Updated Class Diagram (Increment 2 additions in bold)

```
+------------------------+       +------------------------+
|    ArchitectureSchema  |       |   ComponentSchema      |
+------------------------+       +------------------------+
| - id: int              |  1..* | - id: str              |
| - name: str            |<------| - name: str            |
| - description: str     |       | - type: str            |
| - components: List     |       | - criticality: int     |
| - flows: List          |       | - position: dict       |
+------------------------+       +------------------------+
          |
          | 1..*
          v
+--------------------------------+
|    DataFlowSchema              |
+--------------------------------+
| - id: str                      |
| - source: str                  |
| - target: str                  |
| - data_type: str               |
| - cia_requirement: str         |
| - latency_sensitivity: str     |
+--------------------------------+

+------------------------------+
| MissionArchitectureSimulator |
+------------------------------+
| - architecture: Schema       |
| - graph: nx.DiGraph          |
+------------------------------+
| + __init__(arch)             |
| + _build_graph()             |
| + run_simulation()           |
| + propagate_compromise()     |
| + simulate_link_degradation()|  <-- NEW
| + simulate_insider_tampering()|  <-- NEW
| + calculate_mission_score()  |
| + rank_criticality()         |
| + _build_attack_path()       |
| + _build_explanation()       |
+------------------------------+

+------------------------+    +------------------------+    +------------------------+
| Architecture (ORM)     |    | Scenario (ORM)         |    | SimulationResult (ORM) |
+------------------------+    +------------------------+    +------------------------+
| - id: int (PK)         | 1..* | - id: int (PK)       | 1  | - id: int (PK)         |
| - name: str            |<---| - architecture_id: FK  |<---| - scenario_id: FK      |
| - description: str     |    | - scenario_type: str   |    | - baseline_score: float|
| - properties: JSONB    |    | - target_component_id  |    | - compromised_score:   |
| - created_at: datetime |    | - parameters: JSONB    |    | - affected_components: |
| - updated_at: datetime |    | - created_at: datetime |    | - attack_path: JSONB   |
+------------------------+    +------------------------+    | - explanation: TEXT    |
                                                           | - created_at: datetime |
                                                           +------------------------+
```

### 6.2 Sequence Diagram: Link Degradation Simulation

```
User          Frontend           Backend API        Simulator         Database
  |               |                   |                 |                 |
  |--[1] Select   |                   |                 |                 |
  |   "Link       |                   |                 |                 |
  |   Degradation"|                   |                 |                 |
  |   + target    |                   |                 |                 |
  |               |--[2] POST ------->|                 |                 |
  |               |/architectures/    |                 |                 |
  |               |{id}/simulate      |                 |                 |
  |               |?scenario_type=    |                 |                 |
  |               | link_degradation  |                 |                 |
  |               |&target_component  |                 |                 |
  |               |_id=sensor-1       |                 |                 |
  |               |                   |--[3] Load Arch->|                 |
  |               |                   |                 |--[4] Query ---->|
  |               |                   |                 |<--[5] Arch Data-|
  |               |                   |--[6] Create --->|                 |
  |               |                   |   Simulator     |                 |
  |               |                   |--[7] simulate   |                 |
  |               |                   |   link_degr --> |                 |
  |               |                   |                 |--[8] Remove     |
  |               |                   |                 |   Edge from     |
  |               |                   |                 |   NetworkX      |
  |               |                   |                 |--[9] Find       |
  |               |                   |                 |   disconnected  |
  |               |                   |                 |   components    |
  |               |                   |                 |--[10] Calc      |
  |               |                   |                 |   Scores        |
  |               |                   |<--[11] Result --|                 |
  |               |<--[12] JSON -------|                 |                 |
  |<--[13] Display|                   |                 |                 |
  |   Dashboard   |                   |                 |                 |
```

### 6.3 Sequence Diagram: Save + Simulate (Full Integration)

```
User          Frontend           Backend API         Database
  |               |                   |                  |
  |--[1] Build    |                   |                  |
  |   Architecture|                   |                  |
  |   on Canvas   |                   |                  |
  |               |                   |                  |
  |--[2] Click    |                   |                  |
  |   "Save"      |                   |                  |
  |               |--[3] POST ------->|                  |
  |               |/architectures     |                  |
  |               |                   |--[4] INSERT ---->|
  |               |                   |   Arch+Components|
  |               |                   |   +Flows         |
  |               |                   |<--[5] {id: 7} ---|
  |               |<--[6] {id: 7} ----|                  |
  |               |-- Store arch_id=7 |                  |
  |               |                   |                  |
  |--[7] Click    |                   |                  |
  |  "Run Sim"    |                   |                  |
  |               |--[8] POST ------->|                  |
  |               |/architectures/7/  |                  |
  |               |simulate?scenario= |                  |
  |               |node_compromise    |                  |
  |               |&target=sensor-1   |                  |
  |               |                   |--[9] SELECT ---->|
  |               |                   |   Arch 7         |
  |               |                   |<--[10] Arch Data-|
  |               |                   |--[11] Run Sim -->|
  |               |                   |<--[12] Result ---|
  |               |<--[13] Result -----|                  |
  |<--[14] Show   |                   |                  |
  |   Dashboard   |                   |                  |
```

---

## 7. Operating Environment

### Hardware Requirements *(unchanged from v1)*

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 1 GB free | 5+ GB free |
| Network | Broadband internet | Broadband internet |

### Software Requirements

**Client Side:**
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- JavaScript enabled
- Screen resolution: 1280×720 minimum

**Server Side (Development):**
- Operating System: macOS, Linux, or Windows 10+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Docker & Docker Compose (optional)

**Server Side (Production — Increment 2):**
- Backend: Render.com (Python/FastAPI Web Service)
- Frontend: Vercel (Next.js)
- Database: Render PostgreSQL (free tier)

---

## 8. Assumptions and Dependencies

### Assumptions

1. **CIA Properties:** Users understand the meaning of confidentiality, integrity, and availability when assigning them to data flows.
2. **Browser Compatibility:** Users access the application via modern, standards-compliant browsers.
3. **Render Cold Starts:** Free-tier Render services may experience 30–60 second cold starts after periods of inactivity; this is acceptable for demonstration purposes.
4. **Single User Sessions:** Concurrent editing of the same architecture by multiple users is not supported in Increment 2.
5. **Scenario Ordering:** Link degradation and insider tampering scenarios require at least one edge in the architecture.

### Dependencies

**Third-Party Libraries (Backend — additions in Increment 2):**

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.109.0 | Web framework |
| NetworkX | 3.2.1 | Graph algorithms |
| SQLAlchemy | 2.0.25 | Database ORM |
| Pydantic | 2.5.3 | Data validation |
| Uvicorn | 0.27.0 | ASGI server |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| pytest | 7.4.4 | Testing framework |
| pytest-cov | 4.1.0 | Coverage reporting |

**Third-Party Libraries (Frontend):**

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 14.x | React framework |
| React Flow | latest | Diagram editor |
| Recharts | latest | Data visualization |
| Tailwind CSS | latest | Styling |
| Axios | latest | HTTP client |

**External Services:**

| Service | Purpose | Dependency Level |
|---------|---------|------------------|
| Vercel | Frontend hosting | High (production) |
| Render | Backend + database hosting | High (production) |
| GitHub | Version control, CI/CD | High |
| GitHub Actions | Automated testing + coverage enforcement | High |

### Changes from v1 Assumptions

- **Assumption 6 (Attack Scenario Simplicity):** Removed — link degradation and insider tampering are now implemented.
- **Assumption 5 (Stub Architecture):** Removed — the simulation endpoint now queries the real database (Issue #45).

---

*Document Version: 2.0*
*Last Updated: March 23, 2026*
*Prepared for: CEN 4090L Software Engineering Lab, Florida State University*
