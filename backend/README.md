# Backend

FastAPI service for the Mission Architecture Simulator.

The backend owns persistence, API validation, simulation orchestration, and database access. It stores mission architectures in PostgreSQL, reconstructs saved graphs for simulation, and returns mission impact results to the frontend.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- NetworkX
- pytest

## Run Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Default local API URL:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

## Environment Variables

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mission_simulator
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

## Tests

```bash
pytest tests/ -v --cov=app --cov-report=term
```

## Code Quality

```bash
flake8 app --count --max-line-length=100 --statistics
black --check app
isort --check-only app
```
