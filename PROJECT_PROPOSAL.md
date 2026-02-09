# CEN 4090L: Software Engineering Lab
## Florida State University
## Group Project Proposal

---

## 1. Project Title

**Mission-System Security Architecture Simulator**

---

## 2. Brief Overview of What You Are Proposing

We are developing a web application that enables mission planners and security analysts to model system architectures, simulate cyber-attacks, and evaluate mission impact. Users can visually design mission systems with interconnected components (sensors, communication links, compute nodes), run attack scenarios (node compromise, link degradation, insider threats), and assess how attacks propagate through dependencies to degrade mission success. The application will provide real-time visualization of attack propagation, calculate mission degradation scores, and suggest architectural mitigations such as redundancy and network segmentation. This will be deployed as a publicly accessible web application with a modern frontend and robust backend API.

---

## 3. Motivation

Mission assurance and cybersecurity resilience are critical concerns for defense and critical infrastructure systems. Current tools for security architecture analysis are either too complex for rapid prototyping or lack visual, interactive capabilities. We want to develop this project because it addresses a real-world need in the defense industry while providing us hands-on experience with full-stack development, graph algorithms, cloud deployment, and security concepts. This project will serve as a portfolio piece demonstrating our ability to build production-ready applications that solve complex problems. Additionally, it gives us valuable experience with modern DevOps practices and cloud deployment platforms that are essential skills for software engineering careers.

---

## 4. Features to be Implemented and Types of Users

**Primary User Type: System Architect / Security Analyst**
- All users have the same access level (no authentication required for MVP)
- Future versions may include admin roles for managing saved architectures

### Core Features

**4.1 Visual Architecture Editor**
- Drag-and-drop interface to create system diagrams
- Add/remove components (sensors, compute nodes, communication links, control systems)
- Define component properties: criticality level (1-10), CIA requirements (Confidentiality, Integrity, Availability), operational state
- Draw connections/dependencies between components
- Save and load architecture designs from database

**4.2 Attack Scenario Simulation**
- Node Compromise Scenario: Simulate attacker compromising specific components
- Link Degradation Scenario: Model communication link failures or jamming
- Insider Threat Scenario: Simulate insider tampering with component data/integrity
- Configure attack parameters (severity, affected components)
- Run multiple scenarios on the same architecture

**4.3 Impact Analysis & Visualization**
- Real-time propagation visualization showing how attacks spread through dependencies
- Calculate mission degradation score (0-100%) based on critical component failures
- Display compromised CIA properties for each affected component
- Generate criticality tables ranking most vulnerable components
- Interactive charts showing attack timeline and cascade effects

**4.4 Scenario Management**
- Save simulation scenarios to database
- Load and replay previous scenarios
- Clone scenarios for comparison ("what-if" analysis)
- Export results as JSON/CSV

**4.5 Mitigation Recommendations**
- Automated analysis of architecture vulnerabilities
- Suggest mitigations: redundancy, network segmentation, input validation, access controls
- Allow users to apply mitigations and re-run scenarios to measure effectiveness
- Compare mission scores before/after mitigation

**4.6 Results Dashboard**
- Mission success/failure score with visual indicators
- List of compromised components with propagation paths
- Graph-based visualization of attack flow
- Downloadable reports

---

## 5. Risk / Challenges

**Technical Challenges:**
- Graph Algorithm Complexity: Implementing accurate attack propagation through dependency chains requires sophisticated graph traversal algorithms (BFS/DFS) and may encounter edge cases with circular dependencies
- Performance: Large architectures (100+ nodes) may cause performance issues in simulation and visualization; will need optimization strategies
- Real-time Visualization: Synchronizing backend simulation state with frontend React Flow animations smoothly could be challenging
- Learning Curve: Team members may need to learn new technologies (React Flow, NetworkX, FastAPI) which could slow initial progress

**Deployment Challenges:**
- Database Persistence: Free-tier PostgreSQL on Render has storage limits; need to manage data growth
- CORS Configuration: Ensuring frontend on Vercel can communicate with backend on Render without security issues
- Environment Variables: Properly managing secrets and API keys across local and production environments

**Team Coordination Risks:**
- Integration Issues: Frontend, backend, and database components must integrate smoothly; poor communication could cause blockers
- Unequal Workload: Some features may take longer than expected, creating workload imbalances
- Schedule Conflicts: Academic calendars, exams, and other commitments could impact availability

**Scope Management:**
- Feature Creep: Project has many possible extensions (ML-based attack prediction, multi-user collaboration, advanced visualizations); must stay focused on core features
- Time Constraints: 3-month timeline with 3 major increments requires strict prioritization

**Mitigation Strategies:**
- Weekly team standups to catch integration issues early
- Incremental delivery with testing at each stage
- Clear API contracts defined upfront
- Fallback to simpler algorithms if performance issues arise
- Buffer time in schedule for unexpected delays

---

## 6. Existing Related Projects

**Similar Applications**

**6.1 MITRE ATT&CK Navigator**
- Link: https://github.com/mitre-attack/attack-navigator
- Description: Web-based tool for visualizing MITRE ATT&CK frameworks
- Difference: ATT&CK Navigator focuses on threat intelligence and known attack patterns; our tool focuses on custom architecture modeling and mission impact simulation with propagation analysis

**6.2 Microsoft Threat Modeling Tool**
- Link: https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool
- Description: Desktop application for creating threat models and identifying security vulnerabilities
- Difference: Microsoft's tool is focused on software threat modeling during design phase; our tool simulates real-time attack propagation on operational mission systems and calculates quantitative mission degradation

**6.3 CISA Cyber Resilience Review (CRR)**
- Link: https://www.cisa.gov/cyber-resilience-review-crr
- Description: Questionnaire-based assessment for cybersecurity resilience
- Difference: CRR is a qualitative assessment framework; our tool provides visual, interactive, quantitative simulation of specific attack scenarios

**6.4 MulVAL (Multihost, Multistage Vulnerability Analysis)**
- Link: http://people.cs.ksu.edu/~xou/mulval/
- Description: Academic research tool for attack graph generation
- Difference: MulVAL is command-line based and research-oriented; our tool is web-based, user-friendly, and designed for rapid mission architecture prototyping

**Our Competitive Advantages:**
- Visual & Interactive: Modern React-based UI with drag-and-drop interface (vs. command-line or static diagrams)
- Mission-Focused: Calculates specific mission success metrics, not just vulnerability scores
- Web-Based & Free: Publicly deployed, no installation required, accessible from any device
- Real-Time Propagation: Shows cascading effects dynamically with animations
- Mitigation Testing: Users can test architectural changes and immediately see impact

---

## 7. Intended Platform / Programming Language

**Platform**
- Web Application (cross-platform, accessible via browser)
- Deployment: Cloud-hosted (Vercel for frontend, Render for backend)
- Local Development: Docker containers for consistent development environment

**Programming Languages & Frameworks**

Frontend:
- TypeScript (primary language)
- React (via Next.js 14 framework)
- HTML/CSS (via Tailwind CSS)

Backend:
- Python 3.11+
- FastAPI (web framework)

Database:
- SQL (PostgreSQL 15)

DevOps/Tooling:
- YAML (GitHub Actions CI/CD)
- Shell/Bash (deployment scripts)
- Dockerfile (containerization)

---

## 8. Third-Party Libraries / APIs to be Used

**Frontend Libraries**
- Next.js 14: React framework with server-side rendering and routing
- React Flow: Interactive node-based diagram editor library
- Recharts: Charting library for data visualization
- Tailwind CSS: Utility-first CSS framework for styling
- Axios: HTTP client for API requests

**Backend Libraries**
- FastAPI: Modern Python web framework for building APIs
- NetworkX: Python library for graph theory and network analysis (attack propagation algorithms)
- SQLAlchemy: SQL ORM for database operations
- Pydantic: Data validation using Python type annotations
- Uvicorn: ASGI server for running FastAPI
- psycopg2: PostgreSQL database adapter
- python-dotenv: Environment variable management
- pytest: Testing framework
- pytest-cov: Code coverage tool

**Database**
- PostgreSQL 15: Relational database management system
- Hosted on Render (free tier, managed PostgreSQL instance)

**DevOps & Deployment**
- Docker & Docker Compose: Containerization for local development
- GitHub Actions: CI/CD pipeline for automated testing and deployment
- Vercel: Frontend hosting platform (free tier)
- Render: Backend API and database hosting (free tier)

**Development Tools**
- Git & GitHub: Version control and collaboration
- VS Code: Recommended IDE
- Postman/Insomnia: API testing (optional)

**APIs & External Services**
- Vercel Deployment API: Automated frontend deployments
- Render API: Backend and database provisioning
- No external third-party APIs required for core functionality (self-contained application)

---

## 9. Team Members, Expertise, Project Responsibilities, and Team Organization

**Team Members**

| Name | FSU ID | Role Assignment |
|------|--------|----------------|
| Samson Shields | sjs23g | Frontend Lead |
| William Ohonba | weo24 | Backend/Simulation Lead & Database/Integration Lead |
| Daniel Gonzalez | dg23c | Backend/Simulation Lead & Database/Integration Lead |
| Sebastian Velazquez | sv24m | Testing/DevOps/Documentation Lead |

---

**Team Member Details**

**Samson Shields (sjs23g)**
- Role: Frontend Lead

- Expertise:
  - Programming Languages: C++, C#, python
  - Technologies/Frameworks: Typescript, Tailwind, Flask, Blazor
  - Tools: Microsoft Power Apps, Adobe Creative Cloud, Lansweeper
  - Other Skills: IT Support, Web Development, Sound Design

- Project Responsibilities:
  - Implement React Flow diagram editor with drag-and-drop functionality for adding/removing components
  - Build results dashboard with interactive charts using Recharts library
  - Create component attribute editor for modifying criticality levels and CIA requirements
  - Develop scenario library UI and scenario management interface
  - Implement clone & compare feature with side-by-side comparison views
  - Ensure UI polish and responsive design for production deployment
  - Create mitigation recommender UI for displaying and applying suggested mitigations

- Estimated Weekly Time Commitment: 12-15 hours/week

**William Ohonba (weo24)**
- Role: Backend/Simulation Lead & Database/Integration Lead

- Expertise:
  - Programming Languages: Python, C++, Java, Sql
  - Technologies/Frameworks: Spark
  - Tools: Ida Pro/ Ghidra
  - Other Skills: Data visualization

- Project Responsibilities:
  - Design and implement FastAPI endpoints and REST API architecture
  - Develop simulation engine with attack propagation algorithms using NetworkX
  - Implement all three attack scenarios (node compromise, link degradation, insider tampering)
  - Create mission scoring algorithms and criticality ranking logic
  - Design PostgreSQL database schema for architectures, components, flows, and scenarios
  - Develop SQLAlchemy ORM models and handle database migrations
  - Build mitigation suggester logic and clone/compare functionality
  - Configure CORS and production environment settings for deployment

- Estimated Weekly Time Commitment: 12-15 hours/week

**Daniel Gonzalez (dg23c)**
- Role: Backend/Simulation Lead & Database/Integration Lead

- Expertise:
  - Programming Languages: Python, Java, C++, Typescript, CSS
  - Technologies/Frameworks: Spring, Flask, .Net, MySQL,
  - Tools: Git, Docker, GitHub Actions
  - Other Skills: AGILE Methodologies, Extensive documentation, justification

- Project Responsibilities:
  - Collaborate on FastAPI endpoint implementation and API documentation (Swagger/OpenAPI)
  - Assist with graph algorithm implementation for CIA-aware propagation logic
  - Design and implement database persistence layer with save/load functionality
  - Create Pydantic validation models for data integrity
  - Optimize database queries for large architectures and implement caching strategies
  - Develop scenario storage and retrieval endpoints
  - Set up production PostgreSQL database on Render/Railway
  - Implement backend-database integration and handle data migrations

- Estimated Weekly Time Commitment: 12-15 hours/week

**Sebastian Velazquez (sv24m)**
- Role: Testing/DevOps/Documentation Lead

- Expertise:
  - Programming Languages:
  - Technologies/Frameworks:
  - Tools: Git,
  - Other Skills:

- Project Responsibilities:
  - Write and maintain comprehensive pytest unit tests targeting 60%+ → 70%+ → 85%+ coverage
  - Set up and manage GitHub Actions CI/CD pipeline for automated testing and deployment
  - Create and maintain Docker and Docker Compose configuration for local development
  - Conduct code reviews on all pull requests to ensure code quality
  - Write and maintain all project documentation (RD v1-v3, IT v1-v3, Progress Reports)
  - Record and produce demo videos for each increment
  - Deploy frontend to Vercel and backend to Render with proper environment configuration
  - Manage production environment, monitor deployments, and ensure end-to-end testing
  - Create traceability matrix and maintain API documentation

- Estimated Weekly Time Commitment: 12-15 hours/week

---

**Team Organization**

Team Structure:
- Collaborative Decision-Making: The team will operate with shared leadership. Major decisions (architecture choices, scope changes, deadline adjustments) will be made collectively during weekly meetings. Each team member is responsible for their domain but empowered to contribute ideas to other areas.

Task Delegation:
- Each team member is assigned a primary role (Frontend Lead, Backend Lead, Database Lead, DevOps Lead) with clear ownership
- Tasks are self-assigned based on role responsibilities and tracked via GitHub Issues
- Cross-functional code reviews ensure everyone understands all parts of the system
- Emergency reallocation of tasks if someone is blocked or overloaded

Communication:
- Primary Platform: iMessage (Discord or other form of communication might be added in the future)
- Weekly Standup Meeting: Every Monday in class
  - What did you complete this week?
  - What are you working on next?
  - Any blockers or help needed?
- GitHub: All code, issues, and pull requests tracked here
- Response Time Expectation: Team members should respond to messages within 24 hours

Meeting Cadence:
- Weekly Team Sync: Every Monday in class
- Ad-hoc Pair Programming: As needed when debugging integration issues
- Increment Review Meetings: Before each deadline (Feb 23, Mar 23, Apr 27) to review deliverables

Workflow:
- Version Control: Git with feature branches
- Branch Strategy: `main` branch for stable code, feature branches for development
- Pull Request Process: All code must be reviewed by at least one other team member before merging
- Testing: Each team member tests their own code locally before creating PR
- Documentation: Update README and inline comments as code is written

Conflict Resolution:
- Technical disagreements: Team vote or consult instructor/TA
- Personal conflicts: Address directly and professionally; escalate to instructor if needed
