"""Database engine, session factory, and FastAPI dependency."""

import logging
import time
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.architecture import Base

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

_SLOW_QUERY_THRESHOLD_MS = 100


@event.listens_for(engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start_time"] = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    elapsed_ms = (
        time.perf_counter() - conn.info.pop("query_start_time", time.perf_counter())
    ) * 1000
    if elapsed_ms >= _SLOW_QUERY_THRESHOLD_MS:
        logger.warning(
            "Slow query (%.1f ms): %.200s",
            elapsed_ms,
            statement,
        )
    else:
        logger.debug("Query OK (%.1f ms)", elapsed_ms)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session per request, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables that don't already exist."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")


def check_connection() -> bool:
    """Return True if the database is reachable, False otherwise."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)
        return False
