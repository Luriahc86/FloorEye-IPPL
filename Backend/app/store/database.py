"""
SQLAlchemy database configuration for FloorEye Backend.

Provides:
- Connection pooling (safe for Railway)
- Session management with proper cleanup
- Dependency injection for FastAPI routes
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.utils.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, ENABLE_DB

logger = logging.getLogger(__name__)

# SQLAlchemy Engine (only created if DB is configured)
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Build MySQL connection URL for SQLAlchemy.
    Uses PyMySQL driver for Railway compatibility.
    """
    return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def init_engine():
    """
    Initialize SQLAlchemy engine with connection pooling.
    Safe for Railway's transient network conditions.
    """
    global _engine, _SessionLocal
    
    if not ENABLE_DB:
        logger.warning("Database not configured - SQLAlchemy engine not initialized")
        return None
    
    if _engine is not None:
        return _engine
    
    try:
        database_url = get_database_url()
        
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,       # Verify connection before use
            pool_recycle=300,         # Recycle connections every 5 minutes
            pool_size=5,              # Maintain 5 connections in pool
            max_overflow=10,          # Allow up to 10 extra connections
            pool_timeout=30,          # Wait up to 30s for a connection
            echo=False,               # Set True for SQL logging in dev
        )
        
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine,
        )
        
        logger.info("SQLAlchemy engine initialized successfully")
        return _engine
    
    except Exception as e:
        logger.error(f"Failed to initialize SQLAlchemy engine: {e}")
        raise


def get_engine():
    """Get the SQLAlchemy engine, initializing if needed."""
    global _engine
    if _engine is None:
        init_engine()
    return _engine


def get_session_factory():
    """Get the session factory, initializing engine if needed."""
    global _SessionLocal
    if _SessionLocal is None:
        init_engine()
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    Usage in routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            result = db.execute(text("SELECT * FROM items"))
            return result.fetchall()
    
    The session is automatically closed after the request completes.
    """
    if not ENABLE_DB:
        raise RuntimeError("Database not configured")
    
    session_factory = get_session_factory()
    if session_factory is None:
        raise RuntimeError("Database session factory not initialized")
    
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test database connection by executing SELECT 1.
    Returns True if successful, False otherwise.
    """
    if not ENABLE_DB:
        return False
    
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
