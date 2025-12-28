import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.store.database import get_engine, get_db as get_session, init_engine
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)


def get_connection() -> Connection:
    if not ENABLE_DB:
        raise RuntimeError("Database not configured (ENABLE_DB=False)")

    engine = get_engine()
    if engine is None:
        init_engine()
        engine = get_engine()
    
    if engine is None:
        raise RuntimeError("Failed to initialize database engine")

    return engine.connect()


@contextmanager
def get_db_connection():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None) -> list:
    with get_db_connection() as conn:
        if params:
            result = conn.execute(text(query), dict(zip([f"p{i}" for i in range(len(params))], params)))
        else:
            result = conn.execute(text(query))
        return result.fetchall()


def execute_insert(query: str, params: tuple) -> int:
    with get_db_connection() as conn:
        named_query = query
        named_params = {}
        for i, param in enumerate(params):
            placeholder = f":p{i}"
            named_query = named_query.replace("%s", placeholder, 1)
            named_params[f"p{i}"] = param
        
        result = conn.execute(text(named_query), named_params)
        conn.commit()
        return result.lastrowid


def execute_update(query: str, params: tuple) -> int:
    with get_db_connection() as conn:
        named_query = query
        named_params = {}
        for i, param in enumerate(params):
            placeholder = f":p{i}"
            named_query = named_query.replace("%s", placeholder, 1)
            named_params[f"p{i}"] = param
        
        result = conn.execute(text(named_query), named_params)
        conn.commit()
        return result.rowcount


def is_db_available() -> bool:
    if not ENABLE_DB:
        return False

    try:
        with get_db_connection() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB availability check failed: {e}")
        return False
