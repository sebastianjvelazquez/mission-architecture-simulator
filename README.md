# Mission Architecture Simulator

[![CI Pipeline](https://github.com/sebastianjvelazquez/mission-architecture-simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/sebastianjvelazquez/mission-architecture-simulator/actions/workflows/ci.yml)

Mission Architecture Simulator is a full-stack web application for modeling mission systems, simulating cyber compromise scenarios, and visualizing how failures propagate through dependent components.

The project is built as a portfolio-grade security engineering tool: users can draw an architecture, save it to a production database, run simulations against saved systems, and review mission impact through a dashboard.

![Mission Architecture Simulator dashboard](Demo%20Mission%20Architecture%20Simulator.png)

## Live Deployment

| Service | URL |
| --- | --- |
| Frontend | https://mission-architecture-simulator-ynfm.vercel.app |
| Backend API | https://mission-architecture-simulator.onrender.com |
| API Docs | https://mission-architecture-simulator.onrender.com/docs |
| Demo Video | https://youtu.be/gMlu0X0HnO0 |

Note: Render free-tier services may cold start after inactivity. The first request can take longer than normal.

## What It Does

- Build mission architectures with sensors, compute nodes, communications links, control systems, storage, and external dependencies.
- Save and load architectures through a FastAPI backend backed by PostgreSQL.
- Run node compromise simulations against saved architectures.
- Calculate baseline and compromised mission scores.
- Trace affected components and attack propagation paths.
- Rank components by criticality to help prioritize hardening.
- Review results in a dashboard with charts and affected/unaffected component tables.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Next.js, React, TypeScript, React Flow, Recharts, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Pydantic, NetworkX |
| Database | PostgreSQL |
| Testing | pytest, pytest-cov, ESLint |
| DevOps | Docker Compose, GitHub Actions |
| Deployment | Vercel frontend, Render backend, Render PostgreSQL |

## Architecture

```text
Browser
  -> Next.js frontend on Vercel
  -> FastAPI backend on Render
  -> PostgreSQL database on Render
```

The frontend stores each diagram node with a stable `component_id`. The backend persists those components in PostgreSQL, reconstructs the saved graph for simulation, and uses NetworkX to model downstream propagation.

## Repository Structure

```text
.
|-- frontend/              # Next.js application
|   |-- app/               # App Router pages
|   |-- components/        # Navbar, editor, and dashboard components
|   `-- public/            # Images and static assets
|-- backend/               # FastAPI service
|   |-- app/api/           # Architecture and scenario routes
|   |-- app/core/          # App setup, config, and simulator endpoint
|   |-- app/models/        # SQLAlchemy and Pydantic models
|   `-- tests/             # Backend test suite
|-- docs/                  # Requirements, testing, database, and deployment docs
|-- scripts/               # Utility scripts
`-- docker-compose.yml     # Local full-stack environment
```

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker Desktop, if using the full local stack
- PostgreSQL, if running the backend without Docker

### 1. Clone the Repository

```bash
git clone https://github.com/sebastianjvelazquez/mission-architecture-simulator.git
cd mission-architecture-simulator
```

### 2. Configure Environment Variables

Create backend and frontend environment files from the examples or set the variables directly in your shell.

Backend:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mission_simulator
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

Frontend:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run with Docker Compose

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Run Services Manually

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Testing and Quality

Backend tests:

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

CI runs on GitHub Actions for backend tests, frontend lint/build, and backend linting with `flake8`, `black`, and `isort`.

## API Highlights

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Backend liveness check |
| `GET /health/db` | Database connectivity check |
| `GET /docs` | Swagger/OpenAPI documentation |
| `POST /architectures` | Save an architecture |
| `GET /architectures` | List saved architectures |
| `GET /architectures/{id}` | Load a saved architecture |
| `PUT /architectures/{id}` | Update an architecture |
| `DELETE /architectures/{id}` | Delete an architecture |
| `POST /architectures/{id}/simulate` | Run a simulation |

## Deployment Notes

Production uses:

- Vercel with Root Directory set to `frontend`
- Render Web Service with Root Directory set to `backend`
- Render PostgreSQL for persistence

Important environment variables:

Frontend on Vercel:

```bash
NEXT_PUBLIC_API_URL=https://mission-architecture-simulator.onrender.com
```

Backend on Render:

```bash
DATABASE_URL=<Render internal PostgreSQL URL>
ENVIRONMENT=production
ALLOWED_ORIGINS=https://mission-architecture-simulator-ynfm.vercel.app
```

## Documentation

Additional project documentation is in `docs/`:

- `docs/DEPLOYMENT.md`
- `docs/DATABASE.md`
- `docs/TESTING.md`
- `docs/TRACEABILITY.md`
- `docs/RD_v3.md`
- `docs/IT_v3.md`

## Project Status

Current capabilities are focused on architecture persistence, node compromise simulation, mission impact scoring, and dashboard visualization. Planned future improvements include additional attack scenarios, richer mitigation scoring, authentication, and expanded frontend test coverage.
