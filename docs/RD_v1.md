# Software Requirements and Design Document

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

1. [Overview](#overview)
2. [Functional Requirements](#functional-requirements)
3. [Non-functional Requirements](#non-functional-requirements)
4. [Use Case Diagram](#use-case-diagram)
5. [Class Diagram and Sequence Diagrams](#class-diagram-and-sequence-diagrams)
6. [Operating Environment](#operating-environment)
7. [Assumptions and Dependencies](#assumptions-and-dependencies)

---

## 1. Overview

The **Mission-System Security Architecture Simulator** is a web application that enables mission planners and security analysts to model system architectures, simulate cyber-attacks, and evaluate mission impact. Users can visually design mission systems with interconnected components (sensors, compute nodes, communication links, control systems), run attack scenarios (node compromise, link degradation, insider threats), and assess how attacks propagate through dependencies to degrade mission success.

The application provides real-time visualization of attack propagation, calculates mission degradation scores, and suggests architectural mitigations such as redundancy and network segmentation. This tool addresses a real-world need in the defense industry for mission assurance and cybersecurity resilience analysis, providing an accessible, visual, and interactive way to prototype and analyze security architectures.

---

## 2. Functional Requirements

### High Priority

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | The system shall provide a visual diagram editor where users can add components (Sensor, Compute, CommsLink, Control, Storage, External) to a canvas using drag-and-drop functionality. | High |
| FR-2 | The system shall allow users to draw directed data flows (edges) between components to represent data dependencies. | High |
| FR-3 | The system shall allow users to delete components and data flows from the architecture diagram. | High |
| FR-4 | The system shall allow users to edit component properties including name and criticality level (1-10 scale). | High |
| FR-5 | The system shall provide a "Save Architecture" feature that persists the architecture design (components, flows, positions) to a PostgreSQL database. | High |
| FR-6 | The system shall provide a "Load Architecture" feature that retrieves previously saved architectures from the database. | High |
| FR-7 | The system shall implement a node compromise attack scenario that simulates an attacker compromising a selected component. | High |
| FR-8 | The system shall propagate compromise effects through the dependency graph to all downstream components using graph traversal algorithms. | High |
| FR-9 | The system shall calculate a mission success score as a percentage of healthy (non-compromised) components. | High |
| FR-10 | The system shall display simulation results including baseline score, compromised score, and list of affected components. | High |

### Medium Priority

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-11 | The system shall display a bar chart comparing baseline and compromised mission scores. | Medium |
| FR-12 | The system shall generate a criticality ranking of components based on user-assigned criticality and graph topology (in-degree). | Medium |
| FR-13 | The system shall provide a step-by-step attack path description showing how compromise propagated through the system. | Medium |
| FR-14 | The system shall provide API documentation via Swagger/OpenAPI at the `/docs` endpoint. | Medium |
| FR-15 | The system shall provide a health check endpoint (`GET /health`) for monitoring and CI/CD integration. | Medium |

### Low Priority

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-16 | The system shall support multiple architectures per user session. | Low |
| FR-17 | The system shall preserve component canvas positions when saving and loading architectures. | Low |

---

## 3. Non-functional Requirements

### Performance

| ID | Requirement |
|----|-------------|
| NFR-1 | The system shall complete attack propagation simulation for architectures with up to 100 components in under 1 second. |
| NFR-2 | The API response time for simulation requests shall not exceed 500ms for typical architectures (10-50 components). |
| NFR-3 | The frontend diagram editor shall maintain 60fps rendering performance during drag-and-drop operations. |

### Reliability

| ID | Requirement |
|----|-------------|
| NFR-4 | The system shall handle circular dependencies in the architecture graph without entering infinite loops. |
| NFR-5 | The system shall gracefully handle database connection failures and provide meaningful error messages. |
| NFR-6 | The backend API shall achieve 95%+ uptime during the demonstration period. |

### Security

| ID | Requirement |
|----|-------------|
| NFR-7 | The system shall implement CORS middleware to restrict API access to authorized frontend origins. |
| NFR-8 | The system shall validate all input data using Pydantic schemas before processing. |
| NFR-9 | The system shall not expose internal error details or stack traces to end users. |

### Usability

| ID | Requirement |
|----|-------------|
| NFR-10 | The diagram editor shall provide visual feedback (highlighting, color changes) when components are selected or affected by attacks. |
| NFR-11 | Error messages shall be human-readable and actionable. |
| NFR-12 | The system shall be accessible via modern web browsers (Chrome, Firefox, Safari, Edge). |

### Maintainability

| ID | Requirement |
|----|-------------|
| NFR-13 | The backend codebase shall maintain 60%+ test coverage (Increment 1), increasing to 70% (Increment 2) and 85% (Increment 3). |
| NFR-14 | All API endpoints shall be documented in OpenAPI/Swagger format. |
| NFR-15 | Code shall follow PEP 8 style guidelines (Python) and ESLint rules (TypeScript). |

### Scalability

| ID | Requirement |
|----|-------------|
| NFR-16 | The database schema shall support storing unlimited architectures with up to 500 components each. |
| NFR-17 | The system architecture shall allow horizontal scaling of the backend API. |

---

## 4. Use Case Diagram

```
                    +------------------------------------------+
                    |    Mission Architecture Simulator        |
                    +------------------------------------------+
                                        |
         +------------------+   +------------------+   +------------------+
         |                  |   |                  |   |                  |
    +----+----+        +----+----+            +----+----+            +----+----+
    |  Add    |        |  Draw   |            |  Edit   |            | Delete  |
    |Component|        |  Flow   |            |Component|            |Component|
    +---------+        +---------+            +---------+            +---------+
         |                  |                      |                      |
         +------------------+----------------------+----------------------+
                                        |
                              +---------+---------+
                              |                   |
                         +----+----+         +----+----+
                         |  Save   |         |  Load   |
                         |  Arch   |         |  Arch   |
                         +---------+         +---------+
                              |                   |
                              +--------+----------+
                                       |
                              +--------+--------+
                              |                 |
                         +----+----+       +----+----+
                         |  Run    |       |  View   |
                         |Simulation|       | Results |
                         +---------+       +---------+


    Actor: Mission Planner / Security Analyst
```

### Use Cases Summary (Increment 1)

| Use Case | Description |
|----------|-------------|
| UC-1: Add Component | User adds a new component (Sensor, Compute, etc.) to the diagram canvas |
| UC-2: Draw Data Flow | User creates a directed edge between two components |
| UC-3: Edit Component | User modifies component name or criticality |
| UC-4: Delete Component | User removes a component and its associated flows |
| UC-5: Save Architecture | User saves the current architecture to the database |
| UC-6: Load Architecture | User loads a previously saved architecture |
| UC-7: Run Simulation | User selects an attack scenario and target, runs simulation |
| UC-8: View Results | User views simulation results including scores and affected components |

*Note: Detailed textual descriptions for each use case will be provided in Increment 2.*

---

## 5. Class Diagram and Sequence Diagrams

### 5.1 Class Diagram

```
+------------------------+       +------------------------+
|    ArchitectureSchema  |       |   ComponentSchema      |
+------------------------+       +------------------------+
| - id: int              |       | - id: str              |
| - name: str            |  1..* | - name: str            |
| - description: str     |<------| - type: str            |
| - components: List     |       | - criticality: int     |
| - flows: List          |       | - position: dict       |
+------------------------+       +------------------------+
          |
          | 1..*
          v
+------------------------+       +------------------------+
|    DataFlowSchema      |       | SimulationResultSchema |
+------------------------+       +------------------------+
| - id: str              |       | - architecture_id: int |
| - source: str          |       | - scenario_type: str   |
| - target: str          |       | - target_component_id: |
| - data_type: str       |       | - baseline_score: float|
| - cia_requirement: str |       | - compromised_score:   |
+------------------------+       | - affected_components: |
                                 | - attack_path: List    |
                                 | - explanation: str     |
                                 +------------------------+

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
| + calculate_mission_score()  |
| + rank_criticality()         |
| + _build_attack_path()       |
| + _build_explanation()       |
+------------------------------+

+------------------------+       +------------------------+
|    Architecture (ORM)  |       |    Component (ORM)     |
+------------------------+       +------------------------+
| - id: int (PK)         |  1..* | - id: int (PK)         |
| - name: str            |<------| - architecture_id: FK  |
| - description: str     |       | - component_id: str    |
| - properties: JSONB    |       | - name: str            |
| - created_at: datetime |       | - component_type: str  |
| - updated_at: datetime |       | - criticality: int     |
+------------------------+       | - position_x: float    |
          |                      | - position_y: float    |
          | 1..*                 +------------------------+
          v
+------------------------+
|      Flow (ORM)        |
+------------------------+
| - id: int (PK)         |
| - architecture_id: FK  |
| - source_component_id: |
| - target_component_id: |
| - cia_requirement: str |
+------------------------+
```

### 5.2 Sequence Diagram: Run Simulation (UC-7)

```
User          Frontend           Backend API        Simulator         Database
  |               |                   |                 |                 |
  |--[1] Click    |                   |                 |                 |
  |   "Simulate"  |                   |                 |                 |
  |               |                   |                 |                 |
  |               |--[2] POST ------->|                 |                 |
  |               |/architectures/    |                 |                 |
  |               |{id}/simulate      |                 |                 |
  |               |?scenario_type=    |                 |                 |
  |               | node_compromise   |                 |                 |
  |               |&target_component  |                 |                 |
  |               |_id=sensor-1       |                 |                 |
  |               |                   |                 |                 |
  |               |                   |--[3] Load ----->|                 |
  |               |                   |   Architecture  |                 |
  |               |                   |                 |--[4] Query ---->|
  |               |                   |                 |                 |
  |               |                   |                 |<--[5] Return ---|
  |               |                   |                 |   Arch Data     |
  |               |                   |                 |                 |
  |               |                   |--[6] Create --->|                 |
  |               |                   |   Simulator     |                 |
  |               |                   |   Instance      |                 |
  |               |                   |                 |                 |
  |               |                   |--[7] run_sim -->|                 |
  |               |                   |   (scenario,    |                 |
  |               |                   |    target)      |                 |
  |               |                   |                 |                 |
  |               |                   |                 |--[8] Build      |
  |               |                   |                 |   NetworkX      |
  |               |                   |                 |   Graph         |
  |               |                   |                 |                 |
  |               |                   |                 |--[9] Propagate  |
  |               |                   |                 |   Compromise    |
  |               |                   |                 |                 |
  |               |                   |                 |--[10] Calculate |
  |               |                   |                 |    Scores       |
  |               |                   |                 |                 |
  |               |                   |<--[11] Return --|                 |
  |               |                   |   SimResult     |                 |
  |               |                   |                 |                 |
  |               |<--[12] JSON ------|                 |                 |
  |               |   Response        |                 |                 |
  |               |                   |                 |                 |
  |<--[13] Display|                   |                 |                 |
  |   Results     |                   |                 |                 |
  |               |                   |                 |                 |
```

### 5.3 Sequence Diagram: Save Architecture (UC-5)

```
User          Frontend           Backend API         Database
  |               |                   |                  |
  |--[1] Click    |                   |                  |
  |   "Save"      |                   |                  |
  |               |                   |                  |
  |               |--[2] POST ------->|                  |
  |               |/architectures     |                  |
  |               |{name, desc,       |                  |
  |               | components,       |                  |
  |               | flows}            |                  |
  |               |                   |                  |
  |               |                   |--[3] Validate -->|
  |               |                   |   Input (Pydantic)
  |               |                   |                  |
  |               |                   |--[4] Begin ----->|
  |               |                   |   Transaction    |
  |               |                   |                  |
  |               |                   |--[5] INSERT ---->|
  |               |                   |   Architecture   |
  |               |                   |                  |
  |               |                   |--[6] INSERT ---->|
  |               |                   |   Components     |
  |               |                   |                  |
  |               |                   |--[7] INSERT ---->|
  |               |                   |   Flows          |
  |               |                   |                  |
  |               |                   |--[8] COMMIT ---->|
  |               |                   |                  |
  |               |                   |<--[9] Success ---|
  |               |                   |                  |
  |               |<--[10] 201 -------|                  |
  |               |   Created         |                  |
  |               |   {id, ...}       |                  |
  |               |                   |                  |
  |<--[11] Show   |                   |                  |
  |   Success     |                   |                  |
  |               |                   |                  |
```

### 5.4 Sequence Diagram: Load Architecture (UC-6)

```
User          Frontend           Backend API         Database
  |               |                   |                  |
  |--[1] Select   |                   |                  |
  |   Arch from   |                   |                  |
  |   dropdown    |                   |                  |
  |               |                   |                  |
  |               |--[2] GET -------->|                  |
  |               |/architectures/{id}|                  |
  |               |                   |                  |
  |               |                   |--[3] SELECT ---->|
  |               |                   |   Architecture   |
  |               |                   |   + Components   |
  |               |                   |   + Flows        |
  |               |                   |   (eager load)   |
  |               |                   |                  |
  |               |                   |<--[4] Result ----|
  |               |                   |                  |
  |               |<--[5] JSON -------|                  |
  |               |   Response        |                  |
  |               |                   |                  |
  |               |--[6] Render       |                  |
  |               |   Components      |                  |
  |               |   on Canvas       |                  |
  |               |                   |                  |
  |<--[7] Display |                   |                  |
  |   Architecture|                   |                  |
  |               |                   |                  |
```

---

## 6. Operating Environment

### Hardware Requirements

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
- Screen resolution: 1280x720 minimum

**Server Side (Development):**
- Operating System: macOS, Linux, or Windows 10+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Docker & Docker Compose (optional, for containerized development)

**Server Side (Production):**
- Backend: Render.com (Python/FastAPI)
- Frontend: Vercel (Next.js)
- Database: Render PostgreSQL (free tier)

### Network Requirements
- HTTPS for production deployment
- CORS configured for frontend-backend communication
- Port 8000 (backend API, local development)
- Port 3000 (frontend, local development)
- Port 5432 (PostgreSQL, local development)

---

## 7. Assumptions and Dependencies

### Assumptions

1. **User Technical Level**: Users are assumed to have basic familiarity with system architecture concepts (components, data flows, dependencies).

2. **Browser Compatibility**: Users will access the application through modern, standards-compliant web browsers with JavaScript enabled.

3. **Network Connectivity**: Users have stable internet connectivity for accessing the deployed web application.

4. **Data Volume**: Initial architectures will contain fewer than 100 components; the system is not optimized for extremely large graphs in Increment 1.

5. **Single User Sessions**: The system assumes single-user sessions; concurrent editing of the same architecture by multiple users is not supported in Increment 1.

6. **Attack Scenario Simplicity**: Only node compromise attacks are implemented in Increment 1; more complex scenarios (link degradation, insider threats) are deferred to Increment 2.

### Dependencies

**Third-Party Libraries (Backend):**
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
| Render | Backend hosting | High (production) |
| Render PostgreSQL | Database hosting | High (production) |
| GitHub | Version control, CI/CD | High |
| GitHub Actions | Automated testing | Medium |

### Risk Mitigation

1. **Library Version Conflicts**: Package versions are pinned in requirements.txt and package.json to ensure reproducible builds.

2. **Service Availability**: Free tier services (Render, Vercel) may have rate limits or cold start delays; documentation includes fallback to local Docker development.

3. **Database Schema Changes**: Alembic migrations are used to manage database schema changes safely.

---

*Document Version: 1.0*
*Last Updated: February 23, 2026*
*Prepared for: CEN 4090L Software Engineering Lab, Florida State University*
