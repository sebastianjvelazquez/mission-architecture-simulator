# Setup Guide

## Prerequisites

- **Git**: Version control
- **Docker Desktop**: Containerization (optional but recommended)
- **Node.js 18+**: Frontend development
- **Python 3.11+**: Backend development
- **PostgreSQL**: Database (via Docker or local install)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd mission-architecture-simulator
```

2. Start all services:
```bash
docker-compose up
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Local Development Setup

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:3000

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will run on http://localhost:8000

### Database Setup

Using Docker:
```bash
docker run --name mission-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mission_simulator -p 5432:5432 -d postgres:15-alpine
```

Or install PostgreSQL locally and create the database:
```sql
CREATE DATABASE mission_simulator;
```

## Environment Variables

Create a `.env` file in the root directory:
```
# Backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mission_simulator
ENVIRONMENT=development

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Verify Installation

Run the test suite:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are in use, modify `docker-compose.yml` or change the ports in your local setup.

### Database Connection Issues
Ensure PostgreSQL is running and the `DATABASE_URL` is correct.

### Module Not Found
Run `pip install -r requirements.txt` or `npm install` again.
