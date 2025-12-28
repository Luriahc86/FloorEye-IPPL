"""
SQLAlchemy database configuration for FloorEye Backend.
Safe for Railway deployment.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Generator
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

_engine = None
_SessionLocal = None


def get_database_url() -> str:
    return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def init_engine():
    global _engine, _SessionLocal

    if not ENABLE_DB:
        logger.warning("Database disabled (ENABLE_DB=False)")
        return None

    if _engine is not None:
        return _engine

    try:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
        )

        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine,
        )

        logger.info("SQLAlchemy engine initialized")
        return _engine

    except Exception as e:
        logger.error(f"Failed to init DB engine: {e}")
        raise


def get_engine():
    if _engine is None:
        init_engine()
    return _engine


def get_db() -> Generator:
    if not ENABLE_DB:
        raise RuntimeError("Database not configured")

    if _SessionLocal is None:
        init_engine()

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    if not ENABLE_DB:
        return False

    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB test failed: {e}")
        return False
