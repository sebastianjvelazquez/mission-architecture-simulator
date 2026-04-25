"""
app/core/main.py  (or app/main.py — matches your project layout)

"""

from __future__ import annotations

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.architectures import router as architectures_router
from app.api.mitigations import router as mitigations_router
from app.api.scenarios import results_router as simulation_results_router
from app.api.scenarios import router as scenarios_router
from app.core.config import get_settings
from app.core.simulate import router as simulate_router
from app.database import check_connection

settings = get_settings()

app = FastAPI(
    title="Mission Security Simulator API",
    description=(
        "Backend for the Mission-System Security Architecture Simulator. "
        "Increment 3 adds clone, mitigations, and compare endpoints."
    ),
    version="0.3.0",
)

# CORS middleware
# get_allowed_origins() merges ALLOWED_ORIGINS + FRONTEND_URL so you only
# need to set FRONTEND_URL=https://your-app.vercel.app on Render.

allowed_origins: List[str] = settings.get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes — ORDER MATTERS for /architectures/compare vs /{architecture_id}
# 1. Mitigations router first — contains GET /architectures/compare which
#    must be matched before the /{architecture_id} catch-all below.
app.include_router(mitigations_router)

# 2. Standard CRUD router (POST, GET list, GET by id, PUT, DELETE).
app.include_router(architectures_router)

# 3. Scenario persistence and simulation results.
app.include_router(scenarios_router)
app.include_router(simulation_results_router)

# 4. Simulation execution endpoint.
app.include_router(simulate_router)


# Health check

@app.get("/health", tags=["ops"])
async def health_check():
    """
    Liveness + readiness check.

    Returns HTTP 200 when the application is running.  The db_ok field
    indicates whether the database is reachable; Render's health check
    only cares about the HTTP status code, but monitoring tools can
    inspect db_ok for deeper insight.
    """
    db_ok = check_connection()
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "db_ok": db_ok,
        "version": app.version,
    }