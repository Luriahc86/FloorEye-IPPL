"""
⚠️ LEGACY DATABASE ACCESS ⚠️

This module exists ONLY for backward compatibility.
DO NOT use this in new code.

Use:
    app.store.database (SQLAlchemy)
for all new database access.
"""

import mysql.connector
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


def get_connection():
    """
    Legacy MySQL connection.
    Used only by routes that have not been migrated to SQLAlchemy yet.
    """
    if not ENABLE_DB:
        raise RuntimeError("Database not configured (ENABLE_DB=False)")

    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
    except Exception as e:
        logger.error(f"Legacy DB connection failed: {e}")
        raise RuntimeError(f"Failed to connect to database: {e}")


def is_db_available() -> bool:
    """
    Legacy DB availability check.
    """
    if not ENABLE_DB:
        return False

    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
