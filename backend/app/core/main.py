"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database import check_connection, init_db

logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(application: FastAPI):
    if check_connection():
        logger.info("Database connection established.")
        init_db()
    else:
        logger.warning("Database unavailable at startup. Endpoints needing DB will fail.")
    yield


app = FastAPI(
    title="Mission Security Simulator API",
    description="Backend for the Mission-System Security Architecture Simulator.",
    version="0.1.0",
    lifespan=lifespan,
)


def _parse_allowed_origins(raw: str) -> List[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


allowed_origins = _parse_allowed_origins(settings.ALLOWED_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    db_ok = check_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "unavailable",
    }