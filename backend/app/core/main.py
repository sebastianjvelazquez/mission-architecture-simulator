"""
app/main.py

The FastAPI application entry point.

This file creates the app instance, registers middleware, and declares
the core /health endpoint. All other routes (simulate, architectures, etc.)
are defined in their own router files under app/routers/ and registered
here via app.include_router().

To run locally:
    uvicorn app.main:app --reload

The --reload flag watches for file changes and restarts automatically,
which is useful during development but should never be used in production.
"""

from typing import List

# FastAPI is the web framework. The app object created below is the ASGI
# application that uvicorn serves.
from fastapi import FastAPI

# CORSMiddleware handles the browser's Cross-Origin Resource Sharing preflight
# requests. Without it, the React frontend (running on localhost:3000) would be
# blocked by the browser when trying to call the API (running on localhost:8000).
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

# Load settings once at module level. get_settings() is cached with @lru_cache,
# so this does not create a new Settings object on every request.
settings = get_settings()

# Create the FastAPI application instance.
# title, description, and version all appear in the auto-generated Swagger UI
# at /docs and in the OpenAPI JSON at /openapi.json.
app = FastAPI(
    title="Mission Security Simulator API",
    description="Backend for the Mission-System Security Architecture Simulator.",
    version="0.1.0",
)


def _parse_allowed_origins(raw: str) -> List[str]:
    """
    Parse a comma-separated ALLOWED_ORIGINS string from .env into a list.

    The .env file stores origins as a single string because environment
    variables can only hold string values. This function splits that string
    into the list that CORSMiddleware expects.

    Examples:
        "http://localhost:3000"
            -> ["http://localhost:3000"]

        "http://localhost:3000, https://myapp.vercel.app"
            -> ["http://localhost:3000", "https://myapp.vercel.app"]

        "" (empty string)
            -> []  (the middleware fallback will kick in)
    """
    # Split on commas, strip whitespace from each piece, and drop empty strings.
    # The 'if origin.strip()' guard handles trailing commas and blank entries.
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


# Parse the origins once at startup rather than on every request.
allowed_origins = _parse_allowed_origins(settings.ALLOWED_ORIGINS)

# Register CORS middleware so the browser allows the frontend to call the API.
# This must be added before any routes are registered so middleware wraps all
# incoming requests.
app.add_middleware(
    CORSMiddleware,

    # If ALLOWED_ORIGINS was empty or blank in .env, fall back to localhost:3000
    # so local development always works even with a misconfigured .env file.
    allow_origins=allowed_origins or ["http://localhost:3000"],

    # Allow the browser to send cookies and Authorization headers cross-origin.
    # Required if we add session-based auth or JWT headers in a later increment.
    allow_credentials=True,

    # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.).
    # The OPTIONS method is used by the browser's CORS preflight check.
    allow_methods=["*"],

    # Allow all headers so the frontend can send Content-Type, Authorization,
    # and any custom headers without being blocked.
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Simple liveness check used by CI, monitoring, and Render health checks.

    Returns HTTP 200 whenever the application process is running and able to
    handle requests. If the app is crashed or deadlocked, this endpoint will
    not respond and the monitoring system will restart the pod.

    The environment field lets callers confirm they are hitting the right
    deployment (development vs staging vs production) without having to check
    environment variables manually.
    """
    # We return a plain dict here instead of a Pydantic model because this
    # endpoint is intentionally simple. FastAPI serializes dicts to JSON
    # automatically, so no extra model definition is needed.
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }