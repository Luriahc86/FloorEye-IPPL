"""Background monitoring service for camera surveillance."""
import time
import logging
import requests
import base64
from threading import Event
from typing import Dict, List

from app.utils.config import YOLO_SERVICE_URL, NOTIFY_INTERVAL, ENABLE_DB
from app.store.db import get_connection

logger = logging.getLogger(__name__)

# Email service import (optional)
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logger.warning("Email service not available")


def call_ml_service(image_bytes: bytes) -> Dict:
    """
    Call HuggingFace ML service for detection.
    
    Sends base64-encoded image to /detect-frame endpoint.
    """
    try:
        # Encode image bytes to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Send JSON payload to ML service
        resp = requests.post(
            YOLO_SERVICE_URL,
            json={"image": image_b64},
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()
        
        # Extract is_dirty and max_confidence
        return {
            "is_dirty": result.get("is_dirty", False),
            "confidence": result.get("max_confidence", 0.0)
        }
    except Exception as e:
        logger.error(f"ML service call failed: {e}")
        raise


def get_cameras() -> List[Dict]:
    """Fetch active cameras from database."""
    if not ENABLE_DB:
        return []
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cameras WHERE aktif = 1")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        logger.error(f"Failed to fetch cameras: {e}")
        return []


def get_active_email_recipients() -> List[str]:
    """Fetch active email recipients from database."""
    if not ENABLE_DB or not EMAIL_AVAILABLE:
        return []
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r["email"] for r in rows]
    except Exception as e:
        logger.error(f"Failed to fetch email recipients: {e}")
        return []


def monitor_loop(stop_event: Event):
    """
    Main monitoring loop for camera surveillance.
    
    ⚠️ WARNING: RTSP MONITORING DISABLED ⚠️
    
    This feature requires opencv (cv2.VideoCapture) to capture frames from RTSP cameras.
    Railway backend MUST NOT include opencv to keep Docker image lightweight.
    
    RTSP monitoring should be handled by:
    1. A separate microservice with opencv
    2. Edge devices that send frames to backend
    3. Browser-based camera capture (recommended)
    
    Args:
        stop_event: Threading event to signal shutdown
    """
    logger.warning("[MONITOR] RTSP camera monitoring is DISABLED - opencv not available in Railway backend")
    logger.warning("[MONITOR] Use browser-based camera capture or deploy separate RTSP monitoring service")
    
    # Sleep indefinitely until stop signal
    while not stop_event.is_set():
        time.sleep(30)
    
    logger.info("[MONITOR] Stopped")
