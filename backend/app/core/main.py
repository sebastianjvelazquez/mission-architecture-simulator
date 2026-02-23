"""FastAPI application entry point."""

import logging
import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.database import check_connection, init_db
from app.api.architectures import router as architectures_router

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


@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
    logger.info(
        "%s %s completed in %.1f ms (status=%d)",
        request.method,
        request.url.path,
        elapsed_ms,
        response.status_code,
    )
    return response


app.include_router(architectures_router)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Unhandled database error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected database error occurred."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )


@app.get("/health")
async def health_check():
    db_ok = check_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "unavailable",
    }