import time
import logging
from threading import Event
from typing import Dict, List

from sqlalchemy import text
from app.utils.config import ENABLE_DB
from app.store.db import get_db_connection

logger = logging.getLogger(__name__)

try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except Exception as e:
    EMAIL_AVAILABLE = False
    logger.warning(f"Email service not available: {e}")


def get_cameras() -> List[Dict]:
    if not ENABLE_DB:
        return []

    try:
        with get_db_connection() as conn:
            result = conn.execute(text("SELECT * FROM cameras WHERE aktif = 1"))
            return [dict(row._mapping) for row in result.fetchall()]
    except Exception:
        logger.exception("Failed to fetch cameras")
        return []


def get_active_email_recipients() -> List[str]:
    if not ENABLE_DB or not EMAIL_AVAILABLE:
        return []

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT email FROM email_recipients WHERE active = 1")
            )
            rows = result.fetchall()
            return [r[0] for r in rows]
    except Exception:
        logger.exception("Failed to fetch email recipients")
        return []


def monitor_loop(stop_event: Event):
    logger.warning(
        "[MONITOR] Background monitoring running in IDLE mode. "
        "RTSP capture is disabled by design."
    )

    while not stop_event.is_set():
        time.sleep(30)

    logger.info("[MONITOR] Stopped gracefully")
