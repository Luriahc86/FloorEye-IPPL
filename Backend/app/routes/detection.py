"""
Detection route - Proxy to HuggingFace ML Service.
Features:
- Send image to HuggingFace for detection
- Save detection result to database
- Send email notification if dirty floor detected
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
import logging
from typing import Optional

from app.utils.config import YOLO_SERVICE_URL, ENABLE_DB
from app.store.db import get_connection

logger = logging.getLogger(__name__)
router = APIRouter()

# =========================
# Email service (optional)
# =========================
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except Exception:
    EMAIL_AVAILABLE = False
    logger.warning("Email service not available")


# =========================
# Helper: Save to Database
# =========================
def save_detection_to_db(
    source: str,
    is_dirty: bool,
    confidence: float,
    image_data: Optional[bytes] = None,
    notes: Optional[str] = None,
) -> Optional[int]:
    """Save detection result to floor_events table."""
    if not ENABLE_DB:
        return None

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO floor_events (source, is_dirty, confidence, image_data, notes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (source, int(is_dirty), confidence, image_data, notes),
        )
        conn.commit()
        event_id = cursor.lastrowid
        logger.info(f"Saved detection event id={event_id}, is_dirty={is_dirty}")
        return event_id

    except Exception as e:
        logger.error(f"Failed to save detection: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================
# Helper: Get Active Recipients
# =========================
def get_active_recipients() -> list:
    """Fetch active email recipients from database."""
    if not ENABLE_DB:
        return []

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
        rows = cursor.fetchall()
        return [r["email"] for r in rows]

    except Exception as e:
        logger.error(f"Failed to fetch recipients: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================
# Helper: Send Notification
# =========================
def send_dirty_notification(confidence: float) -> dict:
    """Send email notification when dirty floor detected."""
    result = {
        "attempted": False,
        "success": False,
        "recipients": [],
        "error": None,
    }

    logger.info(f"[EMAIL] Starting notification, EMAIL_AVAILABLE={EMAIL_AVAILABLE}")

    if not EMAIL_AVAILABLE:
        result["error"] = "Email service not available"
        logger.warning("[EMAIL] Email service not available")
        return result

    recipients = get_active_recipients()
    logger.info(f"[EMAIL] Found {len(recipients)} active recipients: {recipients}")

    if not recipients:
        result["error"] = "No active email recipients"
        logger.info("[EMAIL] No active email recipients")
        return result

    result["attempted"] = True
    result["recipients"] = recipients

    try:
        success = send_email(
            subject="🚨 [FloorEye] Lantai Kotor Terdeteksi!",
            body=(
                f"FloorEye mendeteksi lantai kotor.\n\n"
                f"Confidence: {confidence * 100:.1f}%\n\n"
                f"Segera lakukan pembersihan.\n\n"
                f"- FloorEye System"
            ),
            to_list=recipients,
        )
        result["success"] = success
        logger.info(f"[EMAIL] Notification sent: success={success}")

    except Exception as e:
        result["error"] = str(e)
        logger.exception(f"[EMAIL] Failed to send notification: {e}")

    return result


# =========================
# Main Detection Route
# =========================
@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):
    """
    Detect floor condition from uploaded image.
    
    Flow:
    1. Send image to HuggingFace ML service
    2. Save result to database
    3. Send email notification if dirty
    4. Return result to frontend
    """
    try:
        # Read image bytes
        image_bytes = await file.read()

        # Send to HuggingFace ML
        res = requests.post(
            YOLO_SERVICE_URL,
            files={
                "file": (
                    file.filename or "frame.jpg",
                    image_bytes,
                    file.content_type or "image/jpeg",
                )
            },
            timeout=60,
        )

        if res.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"HF ERROR {res.status_code}: {res.text}",
            )

        # Parse result
        data = res.json()
        detections = data.get("detections", [])
        count = data.get("count", 0)

        max_conf = max(
            (d.get("confidence", 0.0) for d in detections),
            default=0.0,
        )

        is_dirty = count > 0

        # Save to database
        event_id = save_detection_to_db(
            source="live-camera",
            is_dirty=is_dirty,
            confidence=max_conf,
            image_data=image_bytes,
            notes=f"Detections: {count}",
        )

        # Send notification if dirty
        email_status = None
        if is_dirty:
            email_status = send_dirty_notification(max_conf)
            logger.info(f"[DETECT] Email status: {email_status}")

        return {
            "id": event_id,
            "is_dirty": is_dirty,
            "confidence": round(max_conf, 3),
            "count": count,
            "detections": detections,
            "email_status": email_status,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail=str(e))
