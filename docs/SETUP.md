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

## Production Deployment

### Backend on Render

Use the root-level `render.yaml` file if you want Render to create the backend
service and PostgreSQL database from this repo automatically.

#### Option A: Blueprint Deploy from `render.yaml`

1. Push the repo to GitHub with `render.yaml` included.
2. In Render, choose **New +** → **Blueprint**.
3. Select this repository.
4. Render will detect:
   - a PostgreSQL database named `mission-architecture-simulator-db`
   - a web service named `mission-architecture-simulator-api`
5. Confirm the setup and deploy.
6. Wait for the backend deploy to finish.
7. Verify:
   - `https://<your-render-service>.onrender.com/health`
   - `https://<your-render-service>.onrender.com/docs`

The blueprint already configures:

- `DATABASE_URL` from the managed Render Postgres database
- `ENVIRONMENT=production`
- a pre-deploy command that runs:

```bash
python -c "from app.database import init_db; init_db()"
```

This creates the ORM-managed tables before the service starts.

#### Option B: Manual Render Setup

1. In Render, create a new **PostgreSQL** database.
2. Copy the **Internal Database URL**.
3. Create a new **Web Service** from this repository.
4. Use these settings:
   - **Root Directory:** `backend`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add these environment variables:
   - `DATABASE_URL=<your Render internal database URL>`
   - `ENVIRONMENT=production`
   - `ALLOWED_ORIGINS=http://localhost:3000`
6. Deploy the service.
7. Open the Render shell for the service and initialize the database:

```bash
python -c "from app.database import init_db; init_db()"
```

8. Verify:
   - `https://<your-render-service>.onrender.com/health`
   - `https://<your-render-service>.onrender.com/docs`

### Frontend on Vercel

Before deploying the frontend, deploy the backend first so you have the Render
API URL for `NEXT_PUBLIC_API_URL`.

1. In Vercel, create a new project from this repository.
2. Set **Root Directory** to `frontend`.
3. Keep the detected framework as **Next.js**.
4. Add this environment variable:

```bash
NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com
```

5. Deploy the project.
6. Copy the Vercel URL.
7. Go back to Render and update `ALLOWED_ORIGINS` to include both origins:

```bash
https://<your-vercel-project>.vercel.app,http://localhost:3000
```

8. Redeploy the backend if Render does not do so automatically after the env
   var update.
9. Verify the deployed frontend:
   - load the Vercel site
   - try saving an architecture
   - try loading an architecture
   - confirm the browser console shows no CORS errors

### Official References

- Vercel monorepo project setup: https://vercel.com/docs/monorepos/
- Vercel environment variables: https://vercel.com/docs/environment-variables/manage-across-environments
- Render docs: https://render.com/docs
- Render Blueprints: https://render.com/docs/infrastructure-as-code
- Render Blueprint spec: https://render.com/docs/blueprint-spec

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are in use, modify `docker-compose.yml` or change the ports in your local setup.

### Database Connection Issues
Ensure PostgreSQL is running and the `DATABASE_URL` is correct.

### Module Not Found
Run `pip install -r requirements.txt` or `npm install` again.
