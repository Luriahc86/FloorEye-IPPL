"""Database test route for connection verification."""
from fastapi import APIRouter, HTTPException
import logging

from app.utils.config import ENABLE_DB
from app.store.database import test_connection

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/db-test")
def db_test():
    """
    Test database connection.
    
    Returns:
        {"db": "connected"} if successful
        503 error if DB not configured or connection fails
    """
    if not ENABLE_DB:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Set DB_HOST, DB_USER, and DB_NAME."
        )
    
    try:
        if test_connection():
            return {"db": "connected"}
        else:
            raise HTTPException(
                status_code=503,
                detail="Database connection test failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"db_test error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database test failed: {e}"
        )
