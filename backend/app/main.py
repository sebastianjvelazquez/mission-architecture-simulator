"""
app/main.py

Re-exports the FastAPI application from app.core.main for convenience.
This allows importing as `from app.main import app` which is the standard pattern.
"""

from app.core.main import _parse_allowed_origins, app

__all__ = ["app", "_parse_allowed_origins"]
