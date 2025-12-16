"""Database connection utilities with graceful degradation."""
import mysql.connector
from mysql.connector import Error
from typing import Optional
import logging

from app.utils.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, ENABLE_DB

logger = logging.getLogger(__name__)


def get_connection():
    """
    Get MySQL database connection.
    
    Raises:
        RuntimeError if DB is not configured or connection fails.
    """
    if not ENABLE_DB:
        raise RuntimeError(
            "Database not configured. Set DB_HOST, DB_USER, and DB_NAME environment variables."
        )
    
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        return conn
    except Error as e:
        logger.error(f"Database connection failed: {e}")
        raise RuntimeError(f"Failed to connect to database: {e}")


def is_db_available() -> bool:
    """Check if database is available."""
    if not ENABLE_DB:
        return False
    
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
