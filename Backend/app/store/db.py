"""
SQLAlchemy database configuration for FloorEye Backend.

Features:
- MySQL (PyMySQL) compatible with Railway
- Connection pooling (cloud-safe)
- Lazy initialization
- FastAPI dependency support
- Health check utilities

This file is the SINGLE SOURCE OF TRUTH for database access.
Do NOT mix with raw mysql.connector in new code.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
import logging

from app.utils.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    ENABLE_DB,
)

logger = logging.getLogger(__name__)

# =========================
# Internal state
# =========================
_engine = None
_SessionLocal = None


# =========================
# URL builder
# =========================
def get_database_url() -> str:
    """
    Build MySQL connection URL for SQLAlchemy.

    Uses PyMySQL driver (recommended for Railway).
    Charset utf8mb4 avoids encoding issues.
    """
    return (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )


# =========================
# Engine initialization
# =========================
def init_engine():
    """
    Initialize SQLAlchemy engine with safe defaults for Railway.

    - pool_pre_ping prevents stale connections
    - pool_recycle avoids MySQL timeout issues
    - conservative pool sizing
    """
    global _engine, _SessionLocal

    if not ENABLE_DB:
        logger.warning("ENABLE_DB is False — database engine not initialized")
        return None

    if _engine is not None:
        return _engine

    try:
        database_url = get_database_url()

        _engine = create_engine(
            database_url,
            pool_pre_ping=True,   # Check connection health
            pool_recycle=300,     # Recycle connections every 5 minutes
            pool_size=5,          # Base pool size (Railway-safe)
            max_overflow=5,       # Allow short bursts
            pool_timeout=30,      # Wait max 30s for a connection
            echo=False,           # Set True only for debugging
            future=True,          # SQLAlchemy 2.x style
        )

        _SessionLocal = sessionmaker(
            bind=_engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        logger.info("SQLAlchemy engine initialized successfully")
        return _engine

    except Exception as e:
        logger.exception("Failed to initialize SQLAlchemy engine")
        raise RuntimeError(f"Database initialization failed: {e}") from e


# =========================
# Accessors
# =========================
def get_engine():
    """Get SQLAlchemy engine (initialize if needed)."""
    global _engine
    if _engine is None:
        init_engine()
    return _engine


def get_session_factory():
    """Get session factory (initialize engine if needed)."""
    global _SessionLocal
    if _SessionLocal is None:
        init_engine()
    return _SessionLocal


# =========================
# FastAPI dependency
# =========================
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            result = db.execute(text("SELECT * FROM items"))
            return result.fetchall()
    """
    if not ENABLE_DB:
        raise RuntimeError("Database not configured (ENABLE_DB=False)")

    session_factory = get_session_factory()
    if session_factory is None:
        raise RuntimeError("Database session factory not initialized")

    db: Session = session_factory()
    try:
        yield db
    finally:
        db.close()


# =========================
# Health check utilities
# =========================
def test_connection() -> bool:
    """
    Test database connection by executing SELECT 1.

    Returns:
        True if database is reachable, False otherwise.
    """
    if not ENABLE_DB:
        return False

    try:
        engine = get_engine()
        if engine is None:
            return False

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True

    except Exception:
        logger.exception("Database connection test failed")
        return False


def is_db_ready() -> bool:
    """
    Alias for test_connection().
    Useful for health endpoints.
    """
    return test_connection()
