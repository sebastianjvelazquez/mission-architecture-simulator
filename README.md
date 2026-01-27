# MISSION-SYSTEM SECURITY ARCHITECTURE SIMULATOR
## Complete Project Breakdown & Team Guide
### Team Size: 4 People | Timeline: Jan 26 - Apr 27, 2026

**🌐 LIVE WEB DEPLOYMENT REQUIRED**

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Team Roles & Responsibilities](#team-roles--responsibilities)
3. [Tech Stack](#tech-stack)
4. [Deadlines & Timeline](#deadlines--timeline)
5. [Increment 1: Foundation (Feb 23)](#increment-1-foundation)
6. [Increment 2: Propagation Logic (Mar 23)](#increment-2-propagation-logic)
7. [Increment 3: Polish & Mitigations (Apr 27)](#increment-3-polish--mitigations)
8. [Web Deployment Guide](#web-deployment-guide)
9. [Communication & Workflow](#communication--workflow)
10. [Grading & ABET Outcomes](#grading--abet-outcomes)
11. [Weekly Checklists](#weekly-checklists)

---

# PROJECT OVERVIEW

## 🎯 What Are We Building?

**Mission-System Security Architecture Simulator** – A web application that allows mission planners to:
1. **Model** a mission system (sensors, compute nodes, communication links, control systems)
2. **Simulate** cyber attacks and failure scenarios
3. **Evaluate** how attacks propagate and degrade mission success
4. **Test** architectural mitigations (redundancy, segmentation, validation)

## One-Sentence Summary
*"Users draw system architecture → run attack scenarios → see mission impact → test mitigations."*

## Why This Matters
- **Defense Industry Relevance:** Mission assurance is a top priority for DoD, DISA, and defense contractors
- **Systems Thinking:** Teaches how attacks cascade through dependencies
- **Full-Stack Development:** Real-world architecture (frontend, backend, database, DevOps)
- **Cloud Deployment Experience:** Learn to deploy and manage production applications on Vercel and Render
- **Interview-Ready:** You'll have a live portfolio project with public URLs that impresses security teams at Raytheon, Lockheed Martin, Northrop Grumman
- **Public Accessibility:** Deployed online so anyone can access and test your work

---

# TEAM ROLES & RESPONSIBILITIES

## 4-Person Team Structure

### **Person 1: Frontend Lead**
**Primary Responsibility:** User Interface & Diagram Editor

**Key Tasks:**
- React Flow diagram editor (add/remove components, draw/remove flows)
- Results dashboard (charts, results display, criticality tables)
- UI polish (clean, professional interface)
- Component attribute editor (edit criticality, CIA requirements, etc.)
- Ensure responsive design works on deployed site

**Skills Needed:** 
- React/TypeScript (or willing to learn)
- UI/UX thinking
- Recharts (charting library)

**Effort:** ~12-15 hours/week average

**Deliverables by Increment:**
- Increment 1: Working diagram editor + basic results dashboard
- Increment 2: Scenario library UI + improved results panel
- Increment 3: Clone & compare UI, mitigation recommender UI, polish, production-ready for deployment

---

### **Person 2: Backend/Simulation Lead**
**Primary Responsibility:** API & Simulator Engine

**Key Tasks:**
- FastAPI endpoint setup and management
- Simulator engine (propagation logic, scoring algorithms)
- Graph algorithms using NetworkX
- Scenario logic (node compromise, link degradation, insider tampering)
- API documentation (Swagger/OpenAPI)
- Production environment configuration (CORS, environment variables)

**Skills Needed:**
- Python (or willing to learn)
- Understanding of graphs/algorithms
- FastAPI basics

**Effort:** ~12-15 hours/week average

**Deliverables by Increment:**
- Increment 1: FastAPI setup + node compromise scenario + scoring
- Increment 2: Link degradation + insider tampering scenarios + propagation logic
- Increment 3: Mitigation suggester logic + production deployment configuration

---

### **Person 3: Database/Integration Lead**
**Primary Responsibility:** Database Design & API Integration

**Key Tasks:**
- PostgreSQL schema design
- SQLAlchemy ORM models
- Database migrations
- Backend-database integration
- Data validation (Pydantic models)
- Production database setup on Render/Railway

**Skills Needed:**
- SQL basics (or willing to learn)
- Relational database design
- SQLAlchemy ORM

**Effort:** ~10-12 hours/week average

**Deliverables by Increment:**
- Increment 1: Schema design + models + save/load endpoints
- Increment 2: Scenario storage + query optimization
- Increment 3: Data integrity + backup considerations + production database deployment

---

### **Person 4: Testing/DevOps/Documentation Lead**
**Primary Responsibility:** Code Quality, CI/CD, & Documentation

**Key Tasks:**
- pytest unit tests (backend)
- GitHub Actions CI/CD setup
- Docker & Docker Compose configuration
- Code reviews (on all PRs)
- RD & IT documentation
- Progress reports
- Demo videos
- **Web deployment to Vercel (frontend) and Render (backend)**
- Production environment management

**Skills Needed:**
- Python testing (pytest)
- YAML (for GitHub Actions)
- Technical writing
- Docker basics
- **Vercel and Render deployment**

**Effort:** ~12-15 hours/week average

**Deliverables by Increment:**
- Increment 1: CI/CD pipeline + RD v1 + IT v1 + tests (60%+ coverage)
- Increment 2: RD v2 + IT v2 + tests (70%+ coverage) + video
- Increment 3: RD v3 + IT v3 + tests (85%+ coverage) + final video + progress report + **web deployment to Vercel and Render**

---

## 🔄 Cross-Functional Responsibilities

**All team members contribute to:**
- GitHub Issues creation & management
- Code reviews (at least one person reviews every PR)
- Weekly standup updates
- Testing (each person tests their own code + others' code)
- Teammate evaluations (each increment)

---

# TECH STACK

## Frontend
- **Framework:** Next.js 14 (React + TypeScript)
- **Diagram Editor:** React Flow
- **Charts:** Recharts
- **Styling:** Tailwind CSS
- **Node Version:** 18+

## Backend
- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy
- **Graph Algorithms:** NetworkX
- **Validation:** Pydantic
- **Python Version:** 3.11+

## Database
- **DBMS:** PostgreSQL 15
- **Port (local):** 5432
- **Driver:** psycopg2

## DevOps & Quality
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Testing:** pytest (backend), Playwright (frontend smoke tests)
- **Code Coverage:** pytest-cov

## Deployment
- **Local Development:** Docker Compose
- **Production (REQUIRED):**
  - **Frontend:** Vercel (https://vercel.com) - Free tier
  - **Backend:** Render (https://render.com) or Railway (https://railway.app) - Free tier
  - **Database:** PostgreSQL on Render or Railway - Free tier
  - **Total Cost:** $0

---

# DEADLINES & TIMELINE

## 📅 Key Dates

| Milestone | Date | Deliverables | Points |
|---|---|---|---|
| **Proposal** | Jan 26 @ 11:59pm | Project proposal (1-2 pages) | N/A |
| **Increment 1 Due** | Feb 23 @ 11:59pm | Code + RD + IT + Video + Progress Report + Tests | 255 pts |
| **Increment 2 Due** | Mar 23 @ 11:59pm | Code + RD + IT + Video + Progress Report + Tests | 255 pts |
| **Increment 3 Due** | Apr 27 @ 11:59pm | Code + RD + IT + Video + Progress Report + Tests + **Live Deployment URLs** | 255 pts |

## ⏰ Detailed Timeline

### **Week 1: Jan 20-26 (PROPOSAL WEEK)**

**Deadline:** Jan 26 @ 11:59pm

**Tasks:**
- [ ] Finalize 4-person team
- [ ] Confirm roles with each person
- [ ] Draft 1-2 page project proposal
- [ ] Create GitHub repository (`mission-architecture-simulator`)
- [ ] Add instructor (`crmillsfsu`) as collaborator
- [ ] Create folder structure
- [ ] Set up Discord/Slack for communication
- [ ] **SUBMIT PROPOSAL to Canvas**

**Effort:** 3-4 hours total

---

### **Week 2: Jan 27-Feb 2 (SETUP WEEK)**

**Duration:** 1 week

**Tasks:**
- [ ] Team kickoff meeting (30 min)
  - Review project overview
  - Confirm roles
  - Discuss tech stack
  - Set communication cadence (weekly standup)
  
- [ ] Each person installs local dev environment:
  - Git
  - Docker Desktop
  - Node.js + npm (Person 1)
  - Python 3.11+ (Person 2, 3, 4)
  - PostgreSQL client tools (Person 3)

- [ ] Create initial repo structure:
```
mission-architecture-simulator/
├── frontend/
├── backend/
├── docs/
├── scripts/
├── docker-compose.yml
├── README.md
└── .github/workflows/
```

- [ ] Person 1: Initialize Next.js app
- `npx create-next-app@latest frontend --typescript --tailwind`
- Install React Flow: `npm install reactflow`
- Install Recharts: `npm install recharts`

- [ ] Person 2: Create backend skeleton
- Create `backend/main.py`
- Create `backend/requirements.txt`
- Create virtual environment

- [ ] Person 3: Design PostgreSQL schema
- Create `backend/schema.sql`
- Start SQLAlchemy models

- [ ] Person 4: Set up CI/CD
- Create `.github/workflows/ci.yml`
- Create initial GitHub Issues template

**Effort:** 5-8 hours per person

**Deliverable:** Working local dev environment, all team members can clone and run code

---

### **Weeks 3-7: Feb 2 - Feb 23 (INCREMENT 1)**

**Duration:** 4 weeks

**Final Deadline:** Feb 23 @ 11:59pm

**What You're Building:**
- ✅ Diagram editor (React Flow)
- ✅ One attack scenario (node compromise)
- ✅ Mission score calculation
- ✅ Save/load to database
- ✅ Results dashboard
- ✅ Unit tests (60%+ coverage)
- ✅ GitHub Actions CI/CD working
- ✅ RD document v1
- ✅ IT document v1
- ✅ Demo video (5-7 min)
- ✅ Progress report

**Weekly Breakdown:**

#### **Week 3 (Feb 2-8): Core Setup**

Person 1 (Frontend):
- [ ] React Flow component setup
- [ ] Add/remove component buttons
- [ ] Canvas display (drag-and-drop)
- Effort: 8-10 hours

Person 2 (Backend):
- [ ] FastAPI app initialization
- [ ] Health check endpoint
- [ ] Swagger documentation setup
- Effort: 5-7 hours

Person 3 (Database):
- [ ] PostgreSQL schema finalized
- [ ] SQLAlchemy models created
- [ ] Database connection working
- Effort: 8-10 hours

Person 4 (Testing/DevOps):
- [ ] GitHub Actions basic CI pipeline
- [ ] pytest setup
- [ ] Docker Compose file complete
- Effort: 7-9 hours

**Sync Point:** Wed/Thu – all code syncs to main, no breaking changes

---

#### **Week 4 (Feb 9-15): Simulator Logic**

Person 1 (Frontend):
- [ ] Draw/delete edges (data flows)
- [ ] Edit component properties
- [ ] Save architecture button
- Effort: 10-12 hours

Person 2 (Backend):
- [ ] MissionArchitectureSimulator class
- [ ] Node compromise scenario logic
- [ ] Mission score calculation
- [ ] /simulate endpoint
- Effort: 12-15 hours

Person 3 (Database):
- [ ] SQLAlchemy relationships
- [ ] POST /architectures endpoint
- [ ] GET /architectures/{id} endpoint
- Effort: 10-12 hours

Person 4 (Testing/DevOps):
- [ ] Unit tests for simulator logic
- [ ] GitHub Actions passing
- [ ] Start RD document v1
- Effort: 10-12 hours

**Sync Point:** Fri – full integration test (end-to-end)

---

#### **Week 5 (Feb 16-22): Results & Testing**

Person 1 (Frontend):
- [ ] Results dashboard UI
- [ ] Recharts bar chart (before/after scores)
- [ ] Affected components table
- [ ] Load architecture feature
- Effort: 12-14 hours

Person 2 (Backend):
- [ ] Propagation logic refinement
- [ ] Criticality ranking algorithm
- [ ] API response optimization
- Effort: 10-12 hours

Person 3 (Database):
- [ ] Save/load architecture endpoints fully tested
- [ ] Database queries optimized
- [ ] Error handling
- Effort: 8-10 hours

Person 4 (Testing/DevOps):
- [ ] Expand pytest coverage to 60%+
- [ ] Complete RD document v1
- [ ] Complete IT document v1
- [ ] Record demo video script
- Effort: 14-16 hours

**Sync Point:** Daily – testing and integration

---

#### **Week 6 (Feb 23): Final Submission**

**All deliverables due by Feb 23 @ 11:59pm**

Person 1 (Frontend):
- [ ] UI polish (clean up, remove debug code)
- [ ] Test all buttons/flows
- [ ] Performance optimization
- Effort: 4-6 hours

Person 2 (Backend):
- [ ] Final testing of simulator
- [ ] Bug fixes
- [ ] Code cleanup
- Effort: 4-6 hours

Person 3 (Database):
- [ ] Final schema review
- [ ] Data integrity checks
- [ ] Backup strategy documented
- Effort: 2-4 hours

Person 4 (Testing/DevOps):
- [ ] Record and upload demo video
- [ ] Finalize progress report
- [ ] RD/IT final review
- [ ] Submit all deliverables
- Effort: 6-8 hours

**Deliverables Checklist:**
- [ ] Code committed to GitHub
- [ ] RD.docx uploaded to `/docs`
- [ ] IT.docx uploaded to `/docs`
- [ ] Progress Report uploaded to `/docs`
- [ ] Video link in progress report
- [ ] GitHub Issues labeled and linked
- [ ] 60%+ test coverage
- [ ] GitHub Actions passing
- [ ] All team members submit Teammate Evaluation forms on Canvas

**Total Increment 1 Effort:** ~160-180 hours total (40-45 hours/person average)

---

### **Weeks 8-12: Feb 24 - Mar 23 (INCREMENT 2)**

**Duration:** 4 weeks

**Final Deadline:** Mar 23 @ 11:59pm

**What You're Building:**
- ✅ Two more attack scenarios (link degradation, insider tampering)
- ✅ Propagation logic (compromise spreads through dependencies)
- ✅ Criticality ranking (which components matter most?)
- ✅ Scenario library (save/load attack scenarios)
- ✅ Results explanation panel (text description of attack path)
- ✅ Unit tests (70%+ coverage)
- ✅ RD document v2 (complete use case descriptions)
- ✅ IT document v2 (API spec, full testing strategy)
- ✅ Demo video (show 2 attacks, compare results)
- ✅ Progress report

**Weekly Breakdown:**

#### **Week 8 (Feb 24-Mar 2): New Scenarios**

Person 1 (Frontend):
- [ ] Scenario type selector dropdown
- [ ] Target component selector
- [ ] Enhanced results display (show attack path)
- Effort: 10-12 hours

Person 2 (Backend):
- [ ] Link degradation scenario implementation
- [ ] Insider tampering scenario implementation
- [ ] Propagation logic with CIA awareness
- Effort: 14-16 hours

Person 3 (Database):
- [ ] Attack scenario table & storage
- [ ] Scenario save/load endpoints
- Effort: 10-12 hours

Person 4 (Testing/DevOps):
- [ ] Tests for new scenarios (8-10 tests)
- [ ] Update RD document (add new use cases)
- Effort: 10-12 hours

---

#### **Week 9 (Mar 3-9): Criticality & Propagation**

Person 1 (Frontend):
- [ ] Criticality ranking table
- [ ] Visual highlighting of critical components
- [ ] Improved dashboard layout
- Effort: 10-12 hours

Person 2 (Backend):
- [ ] Criticality ranking algorithm
- [ ] NetworkX graph analysis
- [ ] Attack path tracing
- Effort: 12-14 hours

Person 3 (Database):
- [ ] Query optimization for large architectures
- [ ] Simulation results caching
- Effort: 8-10 hours

Person 4 (Testing/DevOps):
- [ ] Expand tests to 70%+ coverage
- [ ] Start API documentation (Swagger)
- [ ] Update IT document
- Effort: 12-14 hours

---

#### **Week 10 (Mar 10-16): Scenario Library**

Person 1 (Frontend):
- [ ] Save scenario button
- [ ] Load scenario dropdown
- [ ] Scenario management UI
- Effort: 10-12 hours

Person 2 (Backend):
- [ ] Scenario persistence logic
- [ ] Query saved scenarios
- Effort: 8-10 hours

Person 3 (Database):
- [ ] Scenario storage optimization
- Effort: 6-8 hours

Person 4 (Testing/DevOps):
- [ ] Complete IT document v2
- [ ] Complete RD document v2 (full use case descriptions)
- [ ] Record demo video script (2 attacks)
- Effort: 14-16 hours

---

#### **Week 11 (Mar 17-22): Testing & Polish**

Person 1 (Frontend):
- [ ] UI polish
- [ ] Bug fixes
- [ ] Usability testing
- Effort: 8-10 hours

Person 2 (Backend):
- [ ] Scenario logic refinement
- [ ] Performance testing
- Effort: 8-10 hours

Person 3 (Database):
- [ ] Final data integrity checks
- Effort: 4-6 hours

Person 4 (Testing/DevOps):
- [ ] Record and upload demo video
- [ ] Finalize progress report
- [ ] Verify 70%+ coverage
- Effort: 8-10 hours

**Deliverables Checklist:**
- [ ] Code with 3 scenarios working
- [ ] Propagation logic tested
- [ ] RD v2 complete (full use case descriptions)
- [ ] IT v2 complete (API spec, testing results)
- [ ] Progress report
- [ ] Video showing 2 attacks
- [ ] GitHub Actions passing
- [ ] Teammate Evaluation forms submitted

**Total Increment 2 Effort:** ~160-180 hours total (40-45 hours/person average)

---

### **Weeks 13-17: Mar 24 - Apr 27 (INCREMENT 3)**

**Duration:** 5 weeks

**Final Deadline:** Apr 27 @ 11:59pm

**What You're Building:**
- ✅ Mitigation recommender (simple rules)
- ✅ Clone & compare feature (baseline vs. hardened)
- ✅ UI polish (delete, edit, dark mode optional)
- ✅ Unit tests (85%+ coverage)
- ✅ Professional documentation
- ✅ RD document v3 (traceability matrix)
- ✅ IT document v3 (complete testing results, deployment guide)
- ✅ Final demo video (baseline → attack → mitigate → improved score)
- ✅ Final progress report
- ✅ **Web deployment (Vercel + Render)**
- ✅ **Live demo URLs working and accessible**
- ✅ **LIVE CLASS PRESENTATION**

**Weekly Breakdown:**

#### **Week 13 (Mar 24-30): Mitigations**

Person 1 (Frontend):
- [ ] Clone architecture button
- [ ] Add mitigation UI (add redundancy, validation gates)
- [ ] Side-by-side comparison view
- Effort: 12-14 hours

Person 2 (Backend):
- [ ] Mitigation suggester logic
- [ ] Clone architecture endpoint
- [ ] Scoring adjustment for mitigations
- Effort: 12-14 hours

Person 3 (Database):
- [ ] Track mitigations in database
- [ ] Manage cloned architectures
- Effort: 8-10 hours

Person 4 (Testing/DevOps):
- [ ] Tests for mitigation logic
- [ ] Start traceability matrix (RD v3)
- Effort: 10-12 hours

---

#### **Week 14 (Mar 31-Apr 6): Clone & Compare**

Person 1 (Frontend):
- [ ] Side-by-side dashboard (before/after)
- [ ] Compare button/feature
- [ ] Show improvement percentage
- Effort: 12-14 hours

Person 2 (Backend):
- [ ] Clone endpoints complete
- [ ] Compare scenarios logic
- Effort: 10-12 hours

Person 3 (Database):
- [ ] Clone operations tested
- Effort: 6-8 hours

Person 4 (Testing/DevOps):
- [ ] Tests for clone/compare
- [ ] Expand IT document (deployment)
- [ ] Create traceability matrix
- [ ] Create Vercel & Render accounts
- [ ] Plan deployment architecture
- Effort: 12-14 hours

---

#### **Week 15 (Apr 7-13): Final Polish & Deployment Prep**

Person 1 (Frontend):
- [ ] UI refinement
- [ ] Delete component/flow feature
- [ ] Edit component properties
- [ ] Performance optimization
- [ ] Optional: Dark mode
- [ ] Test all browsers
- Effort: 14-16 hours

Person 2 (Backend):
- [ ] Refactor for readability
- [ ] Optimize algorithms
- [ ] Final bug fixes
- [ ] CORS configured for production
- [ ] Environment variables documented
- Effort: 10-12 hours

Person 3 (Database):
- [ ] Final schema review
- [ ] Backup & recovery documentation
- [ ] Connection string for production ready
- Effort: 4-6 hours

Person 4 (Testing/DevOps):
- [ ] Expand to 85%+ coverage
- [ ] Complete RD v3 (with traceability matrix)
- [ ] Complete IT v3 (known issues, future work, deployment guide)
- [ ] Record final demo video script
- [ ] Begin backend deployment to Render
- Effort: 16-18 hours

---

#### **Week 16 (Apr 14-20): Testing & DEPLOYMENT**

**Person 1 (Frontend):**
- [ ] Final UI bugs
- [ ] Cross-browser testing
- [ ] Prepare for Vercel deployment
- Effort: 6-8 hours

**Person 2 (Backend):**
- [ ] Code cleanup
- [ ] Final tests
- [ ] Deploy backend to Render
- [ ] Test deployed API endpoints
- Effort: 8-10 hours

**Person 3 (Database):**
- [ ] Final integrity checks
- [ ] Create PostgreSQL database on Render
- [ ] Verify production database connection
- Effort: 6-8 hours

**Person 4 (Testing/DevOps):**
- [ ] Deploy frontend to Vercel
- [ ] Configure environment variables (Render & Vercel)
- [ ] End-to-end testing on live URLs
- [ ] Record and upload final demo video (use live URLs)
- [ ] Verify 85%+ coverage
- [ ] Final RD/IT review
- [ ] Write final progress report
- Effort: 12-16 hours

**All Team - DEPLOYMENT TASKS (CRITICAL):**
- [ ] Frontend deployed to Vercel (public URL)
- [ ] Backend deployed to Render (public API URL)
- [ ] PostgreSQL created on Render
- [ ] Environment variables configured
- [ ] CORS settings updated for production
- [ ] End-to-end testing complete (browser → Vercel → Render → PostgreSQL)
- [ ] Live URLs documented in README
- [ ] No console errors or warnings

---

#### **Week 17 (Apr 21-27): Final Submission & Presentation**

**Apr 27 @ 11:59pm: FINAL SUBMISSION**

All team members:
- [ ] Final code cleanup
- [ ] Final review of all deliverables
- [ ] **Verify live deployment is working (CRITICAL)**
- [ ] Submit to Canvas:
  - Progress Report
  - RD.docx (v3)
  - IT.docx (v3)
  - Video link
  - GitHub link
  - **🌐 LIVE DEPLOYMENT URLS:**
    - Frontend URL: https://your-project.vercel.app
    - Backend API URL: https://your-project.onrender.com
    - API Docs: https://your-project.onrender.com/docs

**Then (after Apr 27):**
- [ ] **LIVE CLASS PRESENTATION (5-7 min demo)**
  - **Open live deployed app in browser (NOT localhost!)**
  - Show architecture builder
  - Run attack on baseline
  - Show how it fails
  - Clone and harden
  - Run same attack again
  - Show improvement
  - Brief team reflection
  - **Share live URLs with class/professor**

**Total Increment 3 Effort:** ~180-200 hours total (45-50 hours/person average)

---

## 📊 Total Project Effort Summary

| Increment | Duration | Hours/Person | Total Hours |
|---|---|---|---|
| **Proposal + Setup** | 2 weeks | 5-6 hours | 20-24 hours |
| **Increment 1** | 4 weeks | 40-45 hours | 160-180 hours |
| **Increment 2** | 4 weeks | 40-45 hours | 160-180 hours |
| **Increment 3** | 5 weeks | 45-50 hours | 180-200 hours |
| **TOTAL** | **15 weeks** | **~130-145 hours** | **~520-584 hours** |

**Average per week:** ~10 hours/person (very manageable for a capstone)

---

# INCREMENT 1: FOUNDATION

## Increment 1 Goals

By **Feb 23 @ 11:59pm**, you must have:
- ✅ Functioning diagram editor
- ✅ One working attack scenario
- ✅ Mission score calculation
- ✅ Save/load to database
- ✅ Results dashboard
- ✅ All documentation (RD v1, IT v1)
- ✅ Demo video
- ✅ 60%+ test coverage
- ✅ GitHub Actions CI/CD
- ✅ Progress report

## What to Build

### **Component 1: React Flow Diagram Editor**

**User Stories:**
- As a mission planner, I can add components (Sensor, Compute, CommsLink, Control, Storage, External) to a canvas
- As a mission planner, I can drag components around the canvas
- As a mission planner, I can draw data flows (edges) between components
- As a mission planner, I can delete components or flows
- As a mission planner, I can edit component properties (name, criticality)

**Features:**
- Toolbar with buttons for each component type
- Right-click context menu to delete
- Edge drawing (click-drag from source to target)
- Component properties panel (edit on selection)

**Code Location:** `frontend/src/app/page.tsx` (or component structure)

**Technical Details:**
```typescript
// Initial structure
interface Component {
  id: string;
  name: string;
  type: "Sensor" | "Compute" | "CommsLink" | "Control" | "Storage" | "External";
  criticality: number; // 1-10
  position: { x: number; y: number };
}

interface DataFlow {
  id: string;
  source: string;
  target: string;
  dataType?: string;
  ciaRequirement?: string;
  latencySensitivity?: string;
}

interface Architecture {
  id?: number;
  name: string;
  description?: string;
  components: Component[];
  flows: DataFlow[];
}
```

### Component 2: Node Compromise Simulator

**User Stories:**

- As a mission planner, I can select a component and run a "node compromise" attack
- As a mission planner, I can see which components are affected by the compromise
- As a mission planner, I can see the mission score drop

**Features:**

- API endpoint: POST /architectures/{id}/simulate?scenario_type=node_compromise&target_component_id=1
- Compromise propagates downstream (to all components that depend on the compromised node)
- Returns:
  - Baseline mission score
  - Compromised mission score
  - List of affected components
  - Text explanation

**Code Location:** `backend/simulator.py`

**Algorithm:**

```python
def propagate_compromise(graph, compromised_node_id):
    """
    Find all descendants of the compromised node.
    Compromise spreads to any component downstream.
    """
    descendants = set(nx.descendants(graph, compromised_node_id))
    descendants.add(compromised_node_id)  # Include the compromised node itself
    return descendants

def calculate_mission_score(total_components, affected_components):
    """
    Simple formula: (healthy / total) * 100
    """
    healthy = total_components - len(affected_components)
    return (healthy / total_components) * 100
```

**Test Cases:**

- Simple 3-node chain: compromise node 1, nodes 2 & 3 affected
- Branching graph: compromise splits into multiple paths
- Isolated node: no downstream, only itself affected

### Component 3: Database Persistence

**User Stories:**

- As a mission planner, I can save my architecture
- As a mission planner, I can load a previously saved architecture

**Features:**

- PostgreSQL schema (architectures, components, flows)
- SQLAlchemy ORM models
- POST /architectures – save
- GET /architectures/{id} – load
- GET /architectures – list all

**Schema:**

```sql
CREATE TABLE architectures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE components (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER REFERENCES architectures(id) ON DELETE CASCADE,
    name VARCHAR(255),
    component_type VARCHAR(50),
    criticality INTEGER,
    position_x FLOAT,
    position_y FLOAT
);

CREATE TABLE data_flows (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER REFERENCES architectures(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES components(id),
    target_id INTEGER REFERENCES components(id),
    data_type VARCHAR(100),
    cia_requirement VARCHAR(50),
    latency_sensitivity VARCHAR(20)
);

CREATE TABLE simulation_runs (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER REFERENCES architectures(id),
    scenario_type VARCHAR(100),
    target_component_id INTEGER,
    baseline_score FLOAT,
    compromised_score FLOAT,
    affected_components TEXT, -- JSON
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Component 4: Results Dashboard

**User Stories:**

- As a mission planner, I can see my mission score before and after the attack
- As a mission planner, I can see which components were affected
- As a mission planner, I can see a text explanation of what happened

**Features:**

- Bar chart (Recharts): Baseline vs. Compromised scores
- Table: List of affected components
- Text explanation panel
- Top 5 criticality ranking table

**Layout:**

```
┌─────────────────────────────────────────┐
│ Mission Success Score                   │
│ [Bar Chart: 100% → 60%]                 │
│ Score Impact: -40%                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ What Happened                           │
│ "Node 1 compromised. Propagated to      │
│  nodes 2 and 3. Mission degrades."      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Component Criticality Ranking           │
│ ┌────────┬──────────┬──────────┐        │
│ │ Component │ Criticality │ Affected │        │
│ ├────────┼──────────┼──────────┤        │
│ │ Node 2 │ 8        │ Yes      │        │
│ │ Node 3 │ 7        │ Yes      │        │
│ │ Node 4 │ 3        │ No       │        │
│ └────────┴──────────┴──────────┘        │
└─────────────────────────────────────────┘
```

## Increment 1 Deliverables

### 1. Source Code

**Must Include:**

- `frontend/src/app/page.tsx` – Diagram editor with React Flow
- `backend/simulator.py` – Node compromise logic
- `backend/models.py` – SQLAlchemy ORM
- `backend/main.py` – FastAPI endpoints
- `backend/test_simulator.py` – Unit tests
- `docker-compose.yml` – Local environment
- `.github/workflows/ci.yml` – GitHub Actions

**Acceptance Criteria:**

- [ ] Can add components
- [ ] Can draw flows
- [ ] Can save to database
- [ ] Can load from database
- [ ] Can run node compromise attack
- [ ] Results show before/after scores
- [ ] Tests pass (60%+ coverage)
- [ ] GitHub Actions CI passing
- [ ] No syntax errors
- [ ] Code is clean and readable

### 2. RD Document (v1)
File: docs/RD.docx

Sections Required:

Overview (1 page)

What the system does
Who uses it (mission planners)
Why it matters
Functional Requirements (1 page)

REQ-001: Add components
REQ-002: Draw flows
REQ-003: Save architecture
REQ-004: Load architecture
REQ-005: Run node compromise attack
REQ-006: Calculate mission score
REQ-007: Identify affected components
REQ-008: Display results
Non-Functional Requirements (0.5 page)

NFR-001: Performance (<500ms for 50-node simulation)
NFR-002: Usability (5-min learning curve)
NFR-003: Code quality (PEP8, TypeScript strict)
NFR-004: Testing (60%+ coverage)
NFR-005: Reliability (data persists)
Use Cases (1.5 pages)

UC-001: Build Architecture
UC-002: Run Simulation
UC-003: View Results
(Each: 2-3 sentences describing main flow)
Preliminary Design (1 page)

System architecture diagram (3-tier: Frontend → API → Database)
Class diagram (Component, DataFlow, Architecture, SimulationRun)
Sequence diagram (User saves architecture)
Total Length: 5-6 pages

3. IT Document (v1)
File: docs/IT.docx

Sections Required (1 & 2 only for Inc 1):

Architecture & Technology Choices (1 page)

Frontend: Next.js + TypeScript + React Flow
Backend: FastAPI + Python + NetworkX
- Database: PostgreSQL + SQLAlchemy
- Why each choice
- High-level architecture diagram

**Initial Testing Approach (0.5 page)**

- Test framework: pytest
- Test cases written (node compromise, propagation, scoring)
- How to run tests
- Coverage target: 60%
- Manual test cases for UI

**Total Length:** 1.5-2 pages

### 4. Demo Video

**Length:** 5-7 minutes

**Host:** YouTube (unlisted) or Google Drive

**Content:**

```
0:00-0:30 – OPENING
"We're building a Mission-System Security Architecture Simulator. 
 In this first increment, we've created a diagram editor, 
 a simulator engine, and a results dashboard."

0:30-1:30 – DEMO: Build Architecture
Screen recording:
- Add Sensor, Compute, CommsLink, Control nodes
- Draw data flows between them
- Click Save
- Show database confirmation

1:30-3:00 – DEMO: Run Attack
- Click "Run Simulation"
- Select "Node Compromise"
- Choose target component (Sensor)
- Show results: 100% → 60%
- Show affected components
- Show criticality table

3:00-4:00 – WHAT WE BUILT
"In Increment 1, we implemented:
- React Flow diagram editor
- Node compromise simulator
- PostgreSQL database
- FastAPI REST API
- Results dashboard with charts
- Unit tests (60%+ coverage)
- GitHub Actions CI/CD"

4:00-5:00 – CHALLENGES & SOLUTIONS
"We encountered a few challenges:
- React Flow learning curve → solved by reviewing docs
- Database schema design → solved with JSON flexibility
- Propagation logic correctness → verified with unit tests"

5:00-6:30 – PLAN FOR INCREMENT 2
"In Increment 2, we're adding:
- Two more attack scenarios (link degradation, insider tampering)
- Improved propagation logic that respects CIA properties
- Criticality ranking
- Scenario library (save/load attacks)"

6:30-7:00 – CLOSING
"Thanks for watching. Code is on GitHub at [link]. 
 See you in Increment 2!"
```

### 5. Progress Report

**File:** `docs/Progress_Report_Increment_1.docx`

**Use:** FSU Progress Report Template.docx (found on Canvas)

**Key Sections:**

- Summary: What was accomplished
- Status: 100% of Increment 1 complete
- Individual Contributions:
  - Person 1 (Frontend): Completed React Flow editor, dashboard UI
  - Person 2 (Backend): Implemented simulator logic, FastAPI setup
  - Person 3 (Database): Designed schema, built ORM models
  - Person 4 (Testing): Set up CI/CD, wrote tests, docs
- Challenges & Resolutions
- Plan for Increment 2

### 6. GitHub Issues & PRs

**Issues Created (minimum 10):**

- FEAT-001: Build diagram editor
- FEAT-002: Implement node compromise scenario
- FEAT-003: Save/load architecture
- FEAT-004: Mission score calculation
- FEAT-005: Results dashboard
- FEAT-006: PostgreSQL schema
- FEAT-007: FastAPI setup
- FEAT-008: Unit tests
- FEAT-009: GitHub Actions CI
- BUG-001: [Any bugs found and fixed]

**PR Requirements:**

- Every PR links an issue (e.g., "Closes #FEAT-001")
- Every issue has a linked PR
- Code review before merge

### Increment 1 Grading (out of 255 points)

| Item | Points |
|---|---|
| Progress Report | 20 |
| RD Document | 60 |
| IT Document | 40 |
| Video | 20 |
| Source Code (Features) | 100 |
| Source Code (Quality) | 10 |
| Teammate Evaluations | 5 |
| **TOTAL** | **255** |

**To Get an "A":** ~215+ points (84%+)

---

# INCREMENT 2: PROPAGATION LOGIC

## Increment 2 Goals

By Mar 23 @ 11:59pm, you must have:

✅ Two more attack scenarios (link degradation, insider tampering)
✅ Advanced propagation logic (CIA-aware)
✅ Criticality ranking
✅ Scenario library
✅ Improved results explanation
✅ All documentation (RD v2, IT v2 complete)
✅ Demo video (compare 2 attacks)
✅ 70%+ test coverage
✅ Progress report

## What to Build

### Component 1: Link Degradation Scenario

**User Story:**

- As a mission planner, I can simulate the degradation of a communication link and see how it affects the mission

**Features:**

- User selects source and target component
- Availability is reduced for target component
- Compromise does NOT spread (unlike node compromise)
- Only the target component is affected

**Implementation:**

```python
def run_link_degradation_scenario(self, source_id, target_id):
    affected = {target_id}
    
    baseline_score = self._calculate_mission_score([])
    compromised_score = self._calculate_mission_score([target_id])
    
    explanation = f"Link from {source_id} → {target_id} degraded. "
    explanation += f"Availability loss for {target_id}. "
    explanation += f"Score: {baseline_score}% → {compromised_score}%"
    
    return {
        "scenario_type": "link_degradation",
        "baseline_score": baseline_score,
        "compromised_score": compromised_score,
        "affected_components": list(affected),
        "explanation": explanation,
    }
```

### Component 2: Insider Tampering Scenario

**User Story:**

- As a mission planner, I can simulate an insider directly tampering with a component and see the integrity impact

**Features:**

- User selects a component
- Insider directly modifies/corrupts the component
- Integrity is lost; effects propagate downstream
- Similar to node compromise but emphasizes "insider" threat

**Implementation:**

```python
def run_insider_tampering_scenario(self, component_id):
    affected = {component_id}
    
    # Find downstream dependencies
    descendants = nx.descendants(self.graph, component_id)
    affected.update(descendants)
    
    baseline_score = self._calculate_mission_score([])
    compromised_score = self._calculate_mission_score(list(affected))
    
    explanation = f"Component {component_id} tampered by insider. "
    if descendants:
        explanation += f"Integrity loss propagated to: {descendants}. "
    explanation += f"Score: {baseline_score}% → {compromised_score}%"
    
    return {
        "scenario_type": "insider_tampering",
        "baseline_score": baseline_score,
        "compromised_score": compromised_score,
        "affected_components": list(affected),
        "explanation": explanation,
    }
```

### Component 3: CIA-Aware Propagation

**Concept:** Compromise propagates differently based on CIA (Confidentiality, Integrity, Availability) requirements:

- **Integrity Loss:** Spreads to components depending on correct data
- **Availability Loss:** Spreads to components needing continuous connection
- **Confidentiality Loss:** Spreads to components handling sensitive data

**Implementation (Simplified for Increment 2):**

```python
def propagate_with_cia_awareness(graph, compromised_node, impact_type):
    """
    Propagate based on CIA requirements of flows.
    
    Args:
        impact_type: "integrity", "availability", or "confidentiality"
    """
    affected = {compromised_node}
    
    for successor in nx.descendants(graph, compromised_node):
        # Get the edge data between compromised node and successor
        edge_data = graph.get_edge_data(compromised_node, successor)
        
        if edge_data:
            cia_req = edge_data.get('cia_requirement')
            
            # Only propagate if the impact matches the requirement
            if cia_req == impact_type:
                affected.add(successor)
    
    return affected
```

### Component 4: Criticality Ranking

**User Story:**

- As a mission planner, I can see which components are most critical to mission success

**Features:**

- Rank all components by criticality
- Show top 5 components
- Criticality is based on:
  - In-degree (how many other components depend on it)
  - Explicit criticality field (user-assigned 1-10)
  - Impact if failed

**Algorithm:**

```python
def rank_criticality(self, affected_components=None):
    """
    Rank components by criticality.
    Criticality = in_degree + explicit_criticality
    """
    scores = {}
    
    for node_id in self.graph.nodes():
        in_degree = self.graph.in_degree(node_id)
        comp_data = self.components.get(node_id, {})
        explicit = comp_data.get('criticality', 5)
        
        scores[node_id] = in_degree + explicit
    
    # Sort descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {
            "component_id": node_id,
            "component_name": self.components[node_id]['name'],
            "criticality_score": score,
            "affected": node_id in (affected_components or set())
        }
        for node_id, score in ranked[:5]
    ]
```

### Component 5: Scenario Library

**User Story:**

- As a mission planner, I can save attack scenarios and run them again later

**Features:**

- Save button in results panel
- Scenario appears in dropdown (default scenarios + saved)
- Saved scenarios pre-fill all fields

**Database:**

```sql
CREATE TABLE attack_scenarios (
    id SERIAL PRIMARY KEY,
    architecture_id INTEGER REFERENCES architectures(id),
    name VARCHAR(255),
    scenario_type VARCHAR(100),
    target_component_id INTEGER,
    is_saved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API:**

- POST /architectures/{id}/scenarios – save scenario
- GET /architectures/{id}/scenarios – list saved scenarios
- DELETE /architectures/{id}/scenarios/{scenario_id} – delete scenario

### Component 6: Enhanced Results Explanation

**Features:**

- Text explanation of attack propagation
- Attack path (step-by-step):
  - Component X compromised (integrity loss)
  - CommsLink Y affected (receives bad data)
  - Control Z degraded (makes bad decisions)
- Visual highlighting of attack path in diagram (optional for Inc 2)

**Output Format:**

```json
{
  "scenario_type": "node_compromise",
  "target_component_id": 1,
  "baseline_score": 100,
  "compromised_score": 60,
  "affected_components": [1, 2, 3],
  "attack_path": [
    "Step 1: Sensor-1 compromised (integrity loss)",
    "Step 2: CommsLink-1 receives corrupted data",
    "Step 3: Control-2 makes decisions on bad data",
    "Step 4: Mission objective degraded"
  ],
  "explanation": "Node 1 compromise propagated to nodes 2 and 3, reducing mission success from 100% to 60%."
}
```

## Increment 2 Deliverables

### 1. Source Code

**Key Additions:**

- `backend/simulator.py` – Link degradation, insider tampering, CIA-aware propagation, criticality ranking
- `backend/scenarios.py` – Scenario management logic
- `frontend/scenario-selector.tsx` – UI for scenario type selection
- `backend/test_scenarios.py` – Unit tests for all 3 scenarios
- Updated `backend/main.py` – New endpoints for scenarios

**Acceptance Criteria:**

- [ ] All 3 scenarios working
- [ ] Propagation logic correct (verified by tests)
- [ ] Criticality ranking displayed
- [ ] Scenarios can be saved/loaded
- [ ] Results show attack path
- [ ] 70%+ test coverage
- [ ] GitHub Actions CI passing

### 2. RD Document (v2)

**File:** `docs/RD.docx`

**New/Updated Sections:**

**Functional Requirements – Add:**

- REQ-009: Run link degradation scenario
- REQ-010: Run insider tampering scenario
- REQ-011: Display criticality ranking
- REQ-012: Save/load attack scenarios
- REQ-013: Display attack path explanation

**Use Cases – Expand with full descriptions:**

- UC-001: Build Architecture (add alternate flows)
- UC-002: Run Simulation (add all 3 scenarios)
- UC-003: View Results (with attack path)
- UC-004: Manage Scenarios (NEW)
- UC-005: Compare Scenarios (NEW - for Inc 3)

**Each use case should have:**

- Main flow (step-by-step)
- Alternate flows
- Preconditions
- Postconditions
- Acceptance criteria

**Design Updates:**

- Updated sequence diagram (shows all 3 scenarios)
- Updated class diagram (add Scenario, AttackPath classes)

**Total Length:** 8-10 pages

### 3. IT Document (v2)

**File:** `docs/IT.docx`

**ALL Sections Required:**

**Architecture & Technology** – Same as v1

**Testing Strategy (NEW)**

- Unit tests: 8-10 test cases
- Coverage metrics: 70%+ target
- Integration tests: end-to-end simulator
- Manual test cases (UI)

**API Specification (NEW)**

- Full OpenAPI/Swagger docs
- Endpoints:
  - POST /architectures
  - GET /architectures/{id}
  - POST /architectures/{id}/simulate
  - POST /architectures/{id}/scenarios
  - GET /architectures/{id}/scenarios
- Request/response schemas

**Database Schema (NEW)**

- ER diagram
- All tables with field descriptions
- Relationships & constraints

**Known Issues & Future Work (NEW)**

- Any known bugs
- Performance optimizations for future

**Total Length:** 4-5 pages

### 4. Demo Video

**Length:** 5-7 minutes

**Content:**

```
0:00-0:30 – RECAP
"In Increment 1, we built the foundation. 
 Now we're adding realistic attack scenarios."

0:30-1:30 – DEMO: Node Compromise
"First attack: compromise a sensor. Watch how it propagates."
[Show running attack, score drops, affected components highlighted]

1:30-2:30 – DEMO: Link Degradation
"Second attack: degrade a communication link. 
 Different effect than node compromise."
[Show second attack, different components affected]

2:30-3:30 – COMPARISON
"Here's the key insight: different attacks have different impacts. 
 Sensor compromise → cascades downstream. 
 Link degradation → only affects target. 
 We can use this to prioritize mitigations."

3:30-4:30 – CRITICALITY RANKING
"This component (Control-2) is the most critical.
 If it fails, the mission fails. So we prioritize protecting it."

4:30-5:30 – IMPROVEMENTS FROM INC 1
"Since Increment 1, we've added:
- Link degradation scenario
- Insider tampering scenario
- CIA-aware propagation
- Criticality ranking
- Scenario library
- Better result explanations"

5:30-6:30 – PLAN FOR INCREMENT 3
"In Increment 3:
- Mitigation suggester
- Clone & compare (test hardening)
- Polish & 85% test coverage"

6:30-7:00 – CLOSING
```

### 5. Progress Report

**File:** `docs/Progress_Report_Increment_2.docx`

**Key Additions from Inc 1:**

- New features implemented (3 scenarios, criticality, etc.)
- Test coverage improvements (60% → 70%+)
- Documentation completeness
- Challenges faced in propagation logic
- Individual contributions breakdown

### 6. GitHub Issues & PRs

**New Issues (minimum 10):**

- FEAT-010: Link degradation scenario
- FEAT-011: Insider tampering scenario
- FEAT-012: CIA-aware propagation
- FEAT-013: Criticality ranking
- FEAT-014: Scenario library (save/load)
- FEAT-015: Attack path explanation
- FEAT-016: Scenario selector UI
- FEAT-017: Test expansion to 70%
- FEAT-018: API documentation
- BUG-00X: [Any bugs found]

### Increment 2 Grading (out of 255 points)

Same as Increment 1. Grading focuses on:

- Quality of new features
- Test coverage improvements
- Documentation completeness
- Individual contributions

---

# INCREMENT 3: POLISH & MITIGATIONS

## Increment 3 Goals

By **Apr 27 @ 11:59pm**, you must have:

- ✅ Mitigation suggester
- ✅ Clone & compare feature
- ✅ Full UI polish
- ✅ 85%+ test coverage
- ✅ Complete RD v3 (with traceability matrix)
- ✅ Complete IT v3 (all sections + deployment)
- ✅ Final demo video (baseline → attack → mitigate → improved)
- ✅ Final progress report
- ✅ LIVE CLASS PRESENTATION

## What to Build

### Component 1: Mitigation Suggester

**User Story:**

- As a mission planner, I can see recommended mitigations based on the attack results

**Features:**

- Simple rule-based suggestions
- Based on attack results and graph analysis
- Suggestions appear in results panel

**Rules:**

```python
def suggest_mitigations(simulation_result, graph):
    """
    Suggest mitigations based on attack results.
    """
    suggestions = []
    affected = simulation_result['affected_components']
    
    # Rule 1: Single point of failure
    for node_id in affected:
        in_degree = graph.in_degree(node_id)
        if in_degree == 0 and len(affected) > 1:
            suggestions.append(
                f"Component {node_id} is a single point of failure. "
                f"Recommendation: Add redundant path."
            )
    
    # Rule 2: Mission-critical components affected
    for node_id in affected:
        if node_id in get_mission_critical_nodes(graph):
            suggestions.append(
                f"Mission-critical component {node_id} affected. "
                f"Recommendation: Add input validation gate."
            )
    
    # Rule 3: Cascade detected
    if len(affected) > 3:
        suggestions.append(
            "Large cascade detected (>3 components). "
            "Recommendation: Implement network segmentation to limit blast radius."
        )
    
    return suggestions
```

**Display:**

```
Mitigation Recommendations:
• Component 1 is a single point of failure → Add redundancy
• Mission-critical component 2 affected → Add validation
• Cascade detected → Implement segmentation
```

### Component 2: Clone & Compare Feature

**User Story:**

- As a mission planner, I can clone my architecture, add mitigations, and compare the results

**Features:**

- "Clone Architecture" button creates a copy
- User can modify the cloned version (add redundancy, validation gates, etc.)
- Run same attack on both
- Show side-by-side comparison with improvement %

**UI Layout:**

```
BASELINE ARCHITECTURE          HARDENED ARCHITECTURE
[Diagram A]                    [Diagram B]

Baseline Mission Score: 100%   Hardened Mission Score: 100%

Run "Sensor-1 Compromise"

Results:
[Baseline]                     [Hardened]
Score: 60% (40% loss)          Score: 85% (15% loss)

Improvement: +25 percentage points
```

**Implementation:**

```python
@app.post("/architectures/{arch_id}/clone")
def clone_architecture(arch_id: int):
    """Clone an architecture for comparison"""
    original = get_architecture(arch_id)
    cloned = {
        "name": original['name'] + " (Hardened)",
        "components": original['components'].copy(),
        "flows": original['flows'].copy(),
    }
    return create_architecture(cloned)

@app.get("/architectures/compare")
def compare_architectures(baseline_id: int, hardened_id: int, scenario_id: int):
    """Run same scenario on both architectures"""
    baseline_result = run_simulation(baseline_id, scenario_id)
    hardened_result = run_simulation(hardened_id, scenario_id)
    
    improvement = hardened_result['score'] - baseline_result['score']
    
    return {
        "baseline": baseline_result,
        "hardened": hardened_result,
        "improvement_percentage": improvement,
    }
```

### Component 3: UI Polish

**Features to Add:**

- Delete component button (right-click or toolbar)
- Edit component properties (name, criticality, type)
- Edit flow properties (data type, CIA requirement, latency)
- Undo/redo (optional, low priority)
- Dark mode toggle (optional, low priority)
- Error handling (clear error messages)
- Loading states (spinners during simulation)
- Keyboard shortcuts (delete key = delete selected)

**Code Quality:**

- Remove console.log statements
- Remove commented-out code
- Refactor long functions
- Add TypeScript types everywhere
- Add JSDoc comments

### Component 4: Enhanced Testing (85%+ Coverage)

**Target:** 85% code coverage (from 70%)

**New Tests to Add:**

```python
# Additional tests for mitigation logic
def test_mitigation_suggestion_single_point_of_failure():
    """Verify single point of failure detection"""
    
def test_mitigation_suggestion_mission_critical():
    """Verify mission-critical component detection"""
    
def test_clone_architecture():
    """Verify cloning creates exact copy"""
    
def test_compare_same_scenario():
    """Verify comparison produces correct improvement %"""
    
# Edge cases
def test_empty_architecture():
    """Simulator handles empty graph"""
    
def test_isolated_node():
    """Isolated node doesn't propagate"""
    
def test_large_graph_performance():
    """100-node graph simulates in <1000ms"""
```

## Increment 3 Deliverables

### 1. Source Code

**Key Additions:**

- `backend/mitigation.py` – Mitigation suggester logic
- `backend/compare.py` – Compare scenarios logic
- `frontend/clone-compare.tsx` – UI for cloning & comparison
- `frontend/mitigation-panel.tsx` – Display mitigation suggestions
- Enhanced `backend/main.py` – Clone & compare endpoints
- `backend/test_mitigations.py` – Tests for mitigation logic
- `backend/test_compare.py` – Tests for comparison logic

**Acceptance Criteria:**

- [ ] Mitigation suggester working
- [ ] Clone & compare feature working
- [ ] UI polished (no debug code)
- [ ] 85%+ test coverage
- [ ] GitHub Actions CI passing
- [ ] Docker runs cleanly (docker-compose up)
- [ ] All features working end-to-end

### 2. RD Document (v3)

**File:** `docs/RD.docx`

**New/Updated Sections:**

**Functional Requirements – Add final requirements:**

- REQ-014: Clone architecture
- REQ-015: Compare scenarios
- REQ-016: Suggest mitigations
- REQ-017: Edit component properties
- REQ-018: Delete components/flows

**Traceability Matrix (NEW & REQUIRED)**

```
REQ-001 | Add Components | FEAT-001 | test_add_component | ✓
REQ-002 | Draw Flows | FEAT-002 | test_draw_flow | ✓
REQ-003 | Save Architecture | FEAT-003 | test_save | ✓
...
(Maps every requirement to GitHub issue, code, and tests)
```

**Complete Use Cases**

- UC-001 through UC-006
- Each with full descriptions

**Final Design**

- Complete architecture diagram
- Complete class diagram
- State diagram (architecture states)

**Total Length:** 12-15 pages

### 3. IT Document (v3)

**File:** `docs/IT.docx`

**ALL Sections Updated:**

**Architecture** – Same as v2

**Testing Strategy – COMPLETE**

- Unit test results: 85%+ coverage
- Test breakdown by module
- Integration test results
- Manual testing checklist
- Test execution time benchmarks

**API Specification – COMPLETE**

- All endpoints documented
- Request/response examples
- Error handling

**Database Schema – COMPLETE**

- ER diagram
- Indexes for performance
- Backup strategy

**Deployment Guide (REQUIRED - CRITICAL)**

- **Live Deployment URLs:**
  - Frontend: https://your-project.vercel.app
  - Backend API: https://your-project.onrender.com
  - API Docs: https://your-project.onrender.com/docs
- Complete Vercel setup instructions
- Complete Render setup instructions
- PostgreSQL configuration on Render
- Environment variables needed (with placeholders, not secrets)
- CORS configuration for production
- Local: docker-compose up (for development)
- Database initialization & migrations
- Troubleshooting common issues

**Known Issues & Future Work (NEW)**

- List any remaining bugs
- Performance optimizations for future
- Potential enhancements
- Technical debt

**Performance Benchmarks (NEW)**

- 50-node simulation: XXms
- 100-node simulation: XXms
- Save/load time: XXms
- UI response time: XXms

**Total Length:** 6-8 pages

### 4. Final Demo Video

**Length:** 5-7 minutes

**Narrative Structure (IMPORTANT):**

```
0:00-0:30 – OPENING & SCENARIO
"We're demonstrating how our simulator helps mission planners 
 evaluate resilience. Here's our LIVE DEPLOYED application."
[Open browser to https://your-project.vercel.app - NOT localhost!]
[Show architecture: 3-5 key components]

0:30-1:30 – BASELINE UNDER ATTACK
"Let's attack the Sensor node."
[Run attack]
"Mission score drops to 30%. The system fails because critical 
 components depend on the sensor."
[Show affected components, criticality ranking]

1:30-2:30 – MITIGATION ANALYSIS
"What do we do? The system suggests mitigations."
[Show suggestions: add redundancy, add validation]

2:30-3:30 – HARDEN THE SYSTEM
"We clone the architecture and add the suggested mitigations."
[Show cloning, adding redundant sensor, adding validation gate]
"Now we have two sensors and input validation before control."

3:30-4:30 – HARDENED UNDER SAME ATTACK
"Let's run the exact same attack on the hardened architecture."
[Run same attack]
"Mission score stays at 85%. The attack doesn't succeed because 
 we have redundancy and validation."

4:30-5:30 – COMPARISON & INSIGHTS
[Show side-by-side comparison]
"Baseline: 30% mission success.
 Hardened: 85% mission success.
 Improvement: +55 percentage points.
 
 This is the kind of analysis a mission planner needs: 
 concrete, quantified impact of architectural decisions."

5:30-6:30 – REFLECTIONS
"Over 15 weeks, we built a full-stack application that demonstrates:
- Systems thinking
- Cyber resilience concepts
- Defense-relevant problem domain
- Professional software engineering practices
- LIVE WEB DEPLOYMENT with cloud hosting

Challenges: React Flow learning curve, propagation logic correctness, cloud deployment configuration
Solutions: Code review, extensive testing, documentation, proper CORS setup

This project taught us how to think about mission assurance."

6:30-7:00 – CLOSING
"Full code on GitHub: [link]
 🌐 LIVE DEPLOYMENT:
   - Frontend: https://your-project.vercel.app
   - Backend API: https://your-project.onrender.com/docs
 Thanks for watching."
```

**Recording Tips:**

- **IMPORTANT: Demo the LIVE deployed version, not localhost!**
- Speak clearly and confidently
- Use a script so you don't ramble
- Do 2-3 takes and pick the best
- Show code briefly if time allows
- Emphasize the "mission assurance" angle
- End strong: why this matters to defense industry

### 5. Final Progress Report

**File:** `docs/Progress_Report_Increment_3.docx`

**Sections:**

- Summary: Full semester reflection
- What Was Accomplished in Increment 3
- Overall Project Status: 100% complete
- Challenges & Lessons Learned
- Individual Contributions (All 3 increments):
  - Person 1: Frontend features, UI polish, X commits, Y LOC
  - Person 2: Backend logic, simulator, X commits, Y LOC
  - Person 3: Database design, persistence, X commits, Y LOC
  - Person 4: Testing, CI/CD, docs, X commits, Y LOC

### 6. GitHub Issues & PRs

**Final Issues (minimum 10):**

- FEAT-019: Mitigation suggester
- FEAT-020: Clone architecture
- FEAT-021: Compare scenarios
- FEAT-022: Edit component properties
- FEAT-023: Delete components/flows
- FEAT-024: UI polish & refinement
- FEAT-025: Test expansion to 85%
- BUG-00X: [Any final bugs fixed]

### Increment 3 Grading (out of 255 points)

Same as Increments 1 & 2, with emphasis on:

- Code quality & polish
- Test coverage (85%+)
- Documentation completeness (traceability matrix)
- Overall project maturity
- **🌐 Live deployment working and accessible**

---

# WEB DEPLOYMENT GUIDE

## 🌐 Deployment Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION DEPLOYMENT                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    HTTPS    ┌──────────────────────┐    │
│   │   Browser    │◄───────────►│   Vercel CDN         │    │
│   │   (User)     │             │   (Next.js Frontend) │    │
│   └──────────────┘             └──────────┬───────────┘    │
│                                           │                  │
│                                    API Calls                 │
│                                           │                  │
│                                           ▼                  │
│                                ┌──────────────────────┐     │
│                                │   Render.com         │     │
│                                │   (FastAPI Backend)  │     │
│                                └──────────┬───────────┘     │
│                                           │                  │
│                                           ▼                  │
│                                ┌──────────────────────┐     │
│                                │   Render PostgreSQL  │     │
│                                │   (Database)         │     │
│                                └──────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Why This Architecture:**
- **Vercel**: Best-in-class Next.js hosting, automatic HTTPS, global CDN, free tier perfect for capstone
- **Render**: Easy Python/FastAPI deployment, managed PostgreSQL included, free tier available
- **Total Cost**: $0 (using free tiers)

---

## 📋 Deployment Prerequisites

Before deploying, ensure you have:

- [ ] GitHub repository with working code (all tests passing locally)
- [ ] Environment variables documented
- [ ] GitHub account connected to both Vercel and Render
- [ ] Local development working end-to-end

---

## 🚀 Step 1: Deploy Frontend to Vercel

### 1.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize Vercel to access your GitHub account
4. Complete account setup

### 1.2 Import Your Project

1. From Vercel dashboard, click "Add New..." → "Project"
2. Select your GitHub repository
3. Vercel auto-detects Next.js - accept the defaults
4. Configure Environment Variables:

```plaintext
NEXT_PUBLIC_API_URL=https://your-project.onrender.com
```

5. Click "Deploy"

### 1.3 Configure Build Settings

Vercel should auto-detect, but verify these settings:

```yaml
Framework Preset: Next.js
Build Command: npm run build (or yarn build)
Output Directory: .next
Install Command: npm install (or yarn install)
```

### 1.4 Verify Deployment

1. Wait for build to complete (2-3 minutes)
2. Click the generated URL (e.g., `your-project.vercel.app`)
3. Verify the frontend loads (backend won't work yet)

---

## 🚀 Step 2: Deploy Backend to Render

### 2.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started" → "GitHub"
3. Authorize Render to access your GitHub repository
4. Complete account setup

### 2.2 Create PostgreSQL Database

1. From Render dashboard, click "New +" → "PostgreSQL"
2. Configure:

```yaml
Name: mission-security-db
Database: mission_security
User: (auto-generated)
Region: Oregon (US West) - closest to Vercel
PostgreSQL Version: 15
Plan: Free
```

3. Click "Create Database"
4. Wait for creation (1-2 minutes)
5. **Copy the "Internal Database URL"** - you'll need this

### 2.3 Create Web Service for FastAPI

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:

```yaml
Name: mission-security-api
Region: Oregon (US West) - same as database
Branch: main
Root Directory: backend (or wherever your FastAPI code lives)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

4. Add Environment Variables:

```plaintext
DATABASE_URL=[Paste Internal Database URL from step 2.2]
ALLOWED_ORIGINS=https://your-project.vercel.app
PYTHON_VERSION=3.11
```

5. Click "Create Web Service"

### 2.4 Verify Backend Deployment

1. Wait for build to complete (5-10 minutes on free tier)
2. Visit `https://your-project.onrender.com/docs`
3. You should see the FastAPI Swagger documentation
4. Test a simple endpoint (e.g., health check)

---

## 🚀 Step 3: Connect Frontend to Backend

### 3.1 Update Vercel Environment Variables

1. Go to Vercel dashboard → Your Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL`:

```plaintext
NEXT_PUBLIC_API_URL=https://your-project.onrender.com
```

3. Click "Save"

### 3.2 Redeploy Frontend

1. Go to Deployments tab
2. Click "..." on latest deployment → "Redeploy"
3. Wait for deployment (1-2 minutes)

### 3.3 Update Backend CORS

1. Go to Render dashboard → Your Web Service → Environment
2. Ensure `ALLOWED_ORIGINS` includes your Vercel URL:

```plaintext
ALLOWED_ORIGINS=https://your-project.vercel.app
```

3. The service will automatically redeploy

---

## 🔧 Step 4: Configure CORS in FastAPI

Update your FastAPI `main.py` to handle production CORS:

```python
# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mission Security Simulator API")

# Get allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Your Vercel frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": os.getenv("ENVIRONMENT", "development")}
```

---

## 🔧 Step 5: Configure Next.js API Calls

Update your Next.js API configuration:

```typescript
// frontend/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchFromAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}
```

---

## ✅ Step 6: End-to-End Testing

### 6.1 Test the Full Flow

1. Open your Vercel URL in browser
2. Create a new architecture
3. Add components and data flows
4. Save the architecture
5. Run an attack simulation
6. Verify results display correctly

### 6.2 Deployment Checklist

```markdown
## Pre-Deployment Checklist
- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] CORS configured for production URLs
- [ ] Database migrations ready

## Vercel (Frontend)
- [ ] GitHub repo connected
- [ ] Build successful
- [ ] Environment variables set
- [ ] HTTPS working
- [ ] No console errors

## Render (Backend)
- [ ] GitHub repo connected
- [ ] Build successful
- [ ] Environment variables set
- [ ] PostgreSQL created
- [ ] Database connected
- [ ] /docs endpoint accessible

## Integration
- [ ] Frontend can reach backend
- [ ] Database operations work
- [ ] Attack simulation completes
- [ ] All features functional

## Final Verification
- [ ] Test in Chrome, Firefox, Safari
- [ ] Test on mobile device
- [ ] No CORS errors in console
- [ ] Performance acceptable
```

---

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:

### Vercel Auto-Deploy
- Every push to `main` triggers a new deployment
- Preview deployments created for pull requests
- Instant rollback available

### Render Auto-Deploy
- Every push to `main` triggers a new deployment
- Can be disabled during development
- Manual deployment also available

### Recommended Workflow

```
1. Develop locally
2. Test locally (all tests pass)
3. Push to feature branch
4. Create Pull Request
5. Vercel creates preview deployment
6. Review and test preview
7. Merge to main
8. Both Vercel and Render auto-deploy
9. Verify production
```

---

## 🛠️ Troubleshooting Common Issues

### Frontend Not Loading

**Symptom:** Vercel deployment succeeds but page is blank

**Solutions:**
- Check browser console for errors
- Verify build output in Vercel logs
- Check that `NEXT_PUBLIC_API_URL` is set correctly

### CORS Errors

**Symptom:** "Access-Control-Allow-Origin" errors in console

**Solutions:**
- Verify `ALLOWED_ORIGINS` environment variable on Render
- Ensure the Vercel URL is spelled correctly (no trailing slash)
- Check FastAPI CORS middleware configuration

### Database Connection Failed

**Symptom:** Backend returns 500 errors, logs show connection refused

**Solutions:**
- Use Internal Database URL (not External) for Render-to-Render connections
- Verify `DATABASE_URL` environment variable is set
- Check PostgreSQL is running (Render dashboard shows status)

### Slow Cold Starts

**Symptom:** First request takes 30+ seconds

**Explanation:** Free tier services "sleep" after inactivity

**Solutions:**
- This is normal for free tier
- Warn professor/grader about initial delay
- Consider upgrading to paid tier for demo day ($7/month)

### Build Failures

**Symptom:** Deployment fails during build step

**Solutions:**
- Check build logs for specific error
- Ensure all dependencies in requirements.txt/package.json
- Verify Python/Node version matches local development

---

## 📝 README Updates for Deployment

Add this section to your project README:

```markdown
## 🌐 Live Deployment

**Frontend (Vercel):** https://your-project.vercel.app

**Backend API (Render):** https://your-project.onrender.com

**API Documentation:** https://your-project.onrender.com/docs

### Note on Cold Starts
The backend uses Render's free tier, which may sleep after 15 minutes of inactivity.
The first request after sleeping may take 30-60 seconds to respond.
Subsequent requests will be fast.

### Running Locally
See [Local Development Setup](#local-development-setup) below.
```

---

# COMMUNICATION & WORKFLOW

## 🗣️ Weekly Standup

**When:** Every Monday @ [specific time agreed by team]

**Duration:** 15-20 minutes

**Format:** Each person shares:

- What I completed last week
- What I'm working on this week
- Any blockers/help needed

**Platform:** Discord/Slack voice or text

## 💬 Daily Communication

**Channel:** Discord #general or #development

**Etiquette:**

- Questions answered within 4 hours
- Share progress daily (async okay)
- Code reviews get priority

## 🔗 GitHub Workflow

### Creating an Issue

**Title Format:** [FEAT/BUG/CHORE]-###: Brief description

**Example:** FEAT-001: Build React Flow diagram editor

**Description Template:**

```markdown
## Description
[What needs to be done?]

## Acceptance Criteria
- [ ] Can add components
- [ ] Components draggable
- [ ] Can draw edges

## Effort Estimate
~10 hours

## Assigned To
[Person]
```

### Creating a Pull Request

**Branch Name:** feat/diagram-editor or fix/propagation-bug

**PR Description:**

```markdown
## What Changed
[Brief summary]

## Closes
Closes #FEAT-001

## Changes
- [ ] Added React Flow component
- [ ] Integrated with backend API
- [ ] Added unit tests

## Testing
[How did you test this?]

## Screenshots/Demo
[If applicable]
```

**Before Merge:**

- [ ] At least 1 code review approval
- [ ] GitHub Actions CI passing
- [ ] No merge conflicts
- [ ] Test coverage maintained

## 📋 Code Review Guidelines

**Every PR requires:**

- Code review by another team member
- Approval (at least 1 person)
- CI/CD passing (GitHub Actions green)

**What to look for:**

- Does it solve the issue?
- Is code readable?
- Are there tests?
- Any performance concerns?
- Any security issues?

**Review Comments:**

- Be constructive
- Suggest improvements
- Ask questions if unclear
- Approve when satisfied

## 📊 Git Commit Messages

**Format:** [TYPE] Brief description

**Types:**

- [FEAT] – New feature
- [FIX] – Bug fix
- [TEST] – Test additions
- [DOCS] – Documentation
- [REFACTOR] – Code cleanup
- [CHORE] – Build, config, etc.

**Examples:**

```
[FEAT] Add React Flow diagram editor
[FIX] Fix propagation logic for cascades
[TEST] Add unit tests for mission score calculation
[DOCS] Update RD with new use cases
[REFACTOR] Extract simulator logic to separate class
```

## 📁 File Structure & Naming

### Frontend

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx (main page)
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── DiagramEditor.tsx
│   │   ├── ResultsDashboard.tsx
│   │   ├── ScenarioSelector.tsx
│   │   ├── MitigationPanel.tsx
│   │   └── ComparisonView.tsx
│   ├── hooks/
│   │   ├── useArchitecture.ts
│   │   └── useSimulation.ts
│   ├── types/
│   │   └── index.ts (TypeScript interfaces)
│   └── utils/
│       └── api.ts (API calls)
```

### Backend

```
backend/
├── main.py (FastAPI app)
├── models.py (SQLAlchemy ORM)
├── schema.sql (PostgreSQL schema)
├── simulator.py (Core logic)
├── mitigation.py (Mitigation suggester)
├── routes/
│   ├── architectures.py
│   ├── simulations.py
│   └── scenarios.py
├── tests/
│   ├── test_simulator.py
│   ├── test_mitigation.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

# GRADING & ABET OUTCOMES

## 📊 Point Distribution

**Total Points:** 765 (3 increments × 255)

**Each Increment (255 points):**

- Progress Report: 20 pts
- RD Document: 60 pts
- IT Document: 40 pts
- Video: 20 pts
- Source Code (Features): 100 pts
- Source Code (Quality): 10 pts
- Teammate Evaluations: 5 pts

**Final Grade:**

- 90%+ (215+ pts) = A
- 80%+ (200+ pts) = B
- 70%+ (185+ pts) = C
- <70% = F

## 🎯 ABET Outcomes

Your project is graded on **THREE ABET outcomes:**

### 1. Teamwork (Average of A, D, F, H, K, M, O, R, T)

- Working effectively in a 4-person team
- Contributing equally
- Communicating clearly
- Supporting each other

**How to Demonstrate:**

- Clear individual contributions in progress reports
- GitHub commits tied to your name
- Participate in code reviews
- Honest teammate evaluations

### 2. Software Analysis & Development (Average of B, C, F, I, J, M, P, Q, T)

- Analyzing requirements
- Designing systems
- Implementing features
- Testing thoroughly

**How to Demonstrate:**

- RD document shows deep understanding of requirements
- IT document shows thoughtful tech choices
- Code is clean, well-tested
- Design evolves based on learnings

### 3. Communication – Technical Writing (Average of A, B, C, H, I, J, O, P, Q)

- Writing clear documentation
- Presenting ideas effectively
- Explaining technical concepts

**How to Demonstrate:**

- RD/IT documents are well-written
- Progress reports detail what you did
- Demo videos are clear and compelling
- Traceability matrix shows connections

## ✅ Grading Rubric (Typical)

| Score | Grade | ABET Rating |
|---|---|---|
| 85-100% | A | Highly Effective |
| 70-84% | B/C+ | Effective |
| <70% | C-/F | Ineffective |

**To Pass:** Must be "Effective" or better on ALL THREE ABET outcomes

---

# WEEKLY CHECKLISTS

## 📋 Increment 1 Weekly Checklist

### Week 3 (Feb 2-8)

**Frontend (Person 1):**

- [ ] React Flow component initializes
- [ ] Add component buttons work
- [ ] Canvas displays nodes
- [ ] Can drag nodes around
- [ ] Test on localhost:3000
- [ ] Commit to feature branch

**Backend (Person 2):**

- [ ] FastAPI app runs on localhost:8000
- [ ] Health check endpoint works
- [ ] Swagger docs accessible
- [ ] Can define routes
- [ ] Commit to feature branch

**Database (Person 3):**

- [ ] PostgreSQL running in Docker
- [ ] Schema created
- [ ] SQLAlchemy models defined
- [ ] Can connect to database
- [ ] Commit schema and models

**Testing/DevOps (Person 4):**

- [ ] GitHub Actions workflow created
- [ ] pytest installed
- [ ] Docker Compose runs all services
- [ ] CI/CD pipeline triggered
- [ ] All commits have messages

**All:**

- [ ] Weekly standup completed
- [ ] No merge conflicts
- [ ] Code reviewed by 1 person
- [ ] Issues linked to PRs

### Week 4 (Feb 9-15)

**Frontend (Person 1):**

- [ ] Draw edges between nodes
- [ ] Delete edge functionality
- [ ] Component properties editor
- [ ] Save architecture button (calls API)
- [ ] Error handling for bad inputs

**Backend (Person 2):**

- [ ] MissionArchitectureSimulator class complete
- [ ] node_compromise_scenario working
- [ ] Mission score calculation correct
- [ ] /simulate endpoint returns JSON
- [ ] Tests written (3+ test cases)

**Database (Person 3):**

- [ ] POST /architectures endpoint working
- [ ] Architecture saves to DB
- [ ] GET /architectures/{id} returns data
- [ ] Foreign keys correct
- [ ] Tests for save/load

**Testing/DevOps (Person 4):**

- [ ] pytest running and passing
- [ ] Coverage report generated
- [ ] GitHub Actions running on every PR
- [ ] Start RD document v1
- [ ] 60% coverage target achieved

**All:**

- [ ] Code synced to main
- [ ] Integration test (end-to-end save → load)
- [ ] No bugs blocking next week

### Week 5 (Feb 16-22)

**Frontend (Person 1):**

- [ ] Results dashboard UI complete
- [ ] Recharts bar chart working
- [ ] Affected components table
- [ ] Criticality ranking table
- [ ] Load architecture feature

**Backend (Person 2):**

- [ ] Propagation logic refined
- [ ] Criticality ranking working
- [ ] API returns all required fields
- [ ] Edge cases handled

**Database (Person 3):**

- [ ] Simulation results saved to DB
- [ ] Queries optimized
- [ ] No N+1 problems
- [ ] Data integrity verified

**Testing/DevOps (Person 4):**

- [ ] 60%+ coverage achieved
- [ ] RD v1 complete (5-6 pages)
- [ ] IT v1 complete (1.5-2 pages)
- [ ] Progress report drafted
- [ ] Demo video script ready

**All:**

- [ ] All GitHub Issues assigned
- [ ] All PRs reviewed & merged
- [ ] Code ready for submission

### Week 6 (Feb 23) – SUBMISSION

**All:**

- [ ] Final code cleanup
- [ ] Final tests passing
- [ ] RD.docx uploaded to /docs
- [ ] IT.docx uploaded to /docs
- [ ] Progress Report uploaded to /docs
- [ ] Demo video recorded and linked
- [ ] All team members submit Teammate Evaluation forms
- [ ] Final commit message: "[SUBMIT] Increment 1 - Feb 23"

## 📋 Increment 2 Weekly Checklist

### Weeks 8-11 (Feb 24 - Mar 22)

**Week 8:**

- [ ] Link degradation scenario implemented
- [ ] Insider tampering scenario implemented
- [ ] Tests written for both scenarios
- [ ] Scenario selector UI added
- [ ] 4+ new GitHub Issues created

**Week 9:**

- [ ] Criticality ranking working
- [ ] Propagation logic refactored for CIA awareness
- [ ] Results explanation panel improved
- [ ] RD document updated
- [ ] 70%+ coverage approaching

**Week 10:**

- [ ] Scenario library save/load working
- [ ] Scenario management UI complete
- [ ] IT document v2 complete
- [ ] Demo video script written
- [ ] All 70%+ coverage achieved

**Week 11:**

- [ ] UI polished
- [ ] All bugs fixed
- [ ] Demo video recorded
- [ ] Final progress report
- [ ] Ready for submission

## 📋 Increment 3 Weekly Checklist

### Weeks 13-17 (Mar 24 - Apr 27)

**Week 13:**

- [ ] Mitigation suggester logic implemented
- [ ] Clone architecture feature added
- [ ] Backend endpoints for clone/compare added
- [ ] Tests for mitigations written

**Week 14:**

- [ ] Clone & compare UI complete
- [ ] Side-by-side comparison view working
- [ ] Improvement % calculated correctly
- [ ] RD updated with new use cases
- [ ] 🌐 Create Vercel account & connect GitHub
- [ ] 🌐 Create Render account & connect GitHub

**Week 15:**

- [ ] UI polish complete
- [ ] Delete/edit features complete
- [ ] 85%+ test coverage achieved
- [ ] RD v3 complete with traceability matrix
- [ ] IT v3 complete with deployment guide
- [ ] 🌐 Configure CORS for production URLs
- [ ] 🌐 Set up environment variables for production
- [ ] 🌐 Begin backend deployment to Render

**Week 16:**

- [ ] Final bug fixes
- [ ] Code cleanup
- [ ] Demo video recorded (using LIVE deployed app!)
- [ ] Progress report finalized
- [ ] 🌐 Frontend deployed to Vercel (public URL working)
- [ ] 🌐 Backend deployed to Render (API accessible)
- [ ] 🌐 PostgreSQL database created on Render
- [ ] 🌐 End-to-end testing on live deployment
- [ ] 🌐 Live URLs documented in README

**Week 17:**

- [ ] Final submission by Apr 27 @ 11:59pm
- [ ] All team members submit Teammate Evals
- [ ] Live class presentation prepared
- [ ] Practice demo run-through
- [ ] 🌐 Verify live deployment still working
- [ ] 🌐 Submit live URLs with Canvas submission
- [ ] 🌐 Demo uses live deployment (NOT localhost)

---

# QUICK REFERENCE

## Key Links & Resources

- Canvas: [your course link]
- GitHub: [your repo link]
- Discord: [invite link]
- Proposal Template: (from Canvas)
- RD Template: (from Canvas)
- IT Template: (from Canvas)
- Progress Report Template: (from Canvas)

## 🌐 Deployment Links (Update After Deploy)

- **Live Frontend:** https://your-project.vercel.app
- **Live Backend API:** https://your-project.onrender.com
- **API Documentation:** https://your-project.onrender.com/docs

## Tech Stack Quick Links

- Next.js: https://nextjs.org/
- React Flow: https://reactflow.dev/
- FastAPI: https://fastapi.tiangolo.com/
- NetworkX: https://networkx.org/
- PostgreSQL: https://www.postgresql.org/
- Docker: https://www.docker.com/

## 🌐 Deployment Platform Links

- Vercel (Frontend Hosting): https://vercel.com/
- Render (Backend + Database): https://render.com/
- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs

## Documentation to Read

- FastAPI Tutorial
- React Flow Examples
- SQLAlchemy ORM
- pytest Best Practices
- **Vercel Next.js Deployment Guide**
- **Render FastAPI Deployment Guide**

---

# FINAL NOTES

## Success Metrics

You've succeeded when:

- ✅ All code is clean, tested, and deployed
- ✅ All documentation is complete and accurate
- ✅ Team members communicate regularly
- ✅ Each person contributes equally
- ✅ Demo video tells a compelling story
- ✅ Project demonstrates defense industry relevance
- ✅ 🌐 **Live deployment accessible at public URLs**
- ✅ 🌐 **Frontend hosted on Vercel**
- ✅ 🌐 **Backend API hosted on Render**
- ✅ 🌐 **Database hosted on Render PostgreSQL**
- ✅ You're proud of what you've built

## Common Pitfalls to Avoid

- ❌ Don't: Start coding before designing
- ✅ Do: Plan first, code second

- ❌ Don't: Wait until last minute to write docs
- ✅ Do: Update RD/IT as you build

- ❌ Don't: Ignore code reviews
- ✅ Do: Review each other's code rigorously

- ❌ Don't: Assume everyone understands the plan
- ✅ Do: Communicate clearly and often

- ❌ Don't: Skip testing
- ✅ Do: Test constantly (unit, integration, manual)

- ❌ Don't: Wait until Week 17 to deploy
- ✅ Do: Start deployment setup in Week 14, deploy in Week 15-16

- ❌ Don't: Demo using localhost
- ✅ Do: Demo the LIVE deployed application

- ❌ Don't: Forget to configure CORS for production
- ✅ Do: Test production URLs end-to-end before demo

## Questions to Ask Yourself

- Is my code readable to someone else?
- Have I tested edge cases?
- Did I document my decisions?
- Am I contributing equally?
- Does the product solve the stated problem?
- Would I be proud to show this in an interview?
- 🌐 **Is our live deployment working right now?**
- 🌐 **Did we test the production URLs today?**

---
