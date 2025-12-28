"""
Background monitoring service for camera surveillance.

NOTE:
- RTSP / OpenCV capture is NOT supported in Railway backend.
- This monitor is intentionally idle-safe.
- Actual detection should be triggered by:
  - browser live camera
  - edge device
  - separate CV microservice
"""

import time
import logging
from threading import Event
from typing import Dict, List

from app.utils.config import ENABLE_DB
from app.store.db import get_connection

logger = logging.getLogger(__name__)

# =========================
# Optional email service
# =========================
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except Exception as e:
    EMAIL_AVAILABLE = False
    logger.warning(f"Email service not available: {e}")


# =========================
# Database helpers
# =========================
def get_cameras() -> List[Dict]:
    """
    Fetch active cameras from database.

    NOTE:
    Cameras are informational only in Railway backend.
    """
    if not ENABLE_DB:
        return []

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM cameras WHERE aktif = 1"
        )
        return cursor.fetchall()

    except Exception:
        logger.exception("Failed to fetch cameras")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_active_email_recipients() -> List[str]:
    """Fetch active email recipients."""
    if not ENABLE_DB or not EMAIL_AVAILABLE:
        return []

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT email FROM email_recipients WHERE active = 1"
        )
        rows = cursor.fetchall()
        return [r["email"] for r in rows]

    except Exception:
        logger.exception("Failed to fetch email recipients")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================
# Monitor loop (IDLE SAFE)
# =========================
def monitor_loop(stop_event: Event):
    """
    Background monitoring loop.

    This loop is intentionally IDLE to avoid:
    - OpenCV dependency
    - RTSP connections
    - heavy CPU usage

    Railway backend MUST remain lightweight.
    """
    logger.warning(
        "[MONITOR] Background monitoring running in IDLE mode. "
        "RTSP capture is disabled by design."
    )

    while not stop_event.is_set():
        # Placeholder for future extensions:
        # - heartbeat logging
        # - health ping
        # - metrics
        time.sleep(30)

    logger.info("[MONITOR] Stopped gracefully")
