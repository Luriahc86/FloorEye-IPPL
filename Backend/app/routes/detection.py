from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import httpx
import logging
from typing import Optional

from app.utils.config import YOLO_SERVICE_URL, ENABLE_DB
from app.store.db import get_db_connection, is_db_available

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    from app.services.emailer import send_email, SMTP_ENABLED
    EMAIL_AVAILABLE = SMTP_ENABLED
    logger.info(f"Email service loaded. SMTP_ENABLED={SMTP_ENABLED}")
except Exception as e:
    EMAIL_AVAILABLE = False
    logger.warning(f"Email service not available: {e}")


def bg_save_detection(
    source: str,
    is_dirty: bool,
    confidence: float,
    image_data: Optional[bytes] = None,
    notes: Optional[str] = None,
):
    if not ENABLE_DB:
        return

    try:
        from sqlalchemy import text
        with get_db_connection() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO floor_events (source, is_dirty, confidence, image_data, notes)
                    VALUES (:source, :is_dirty, :confidence, :image_data, :notes)
                """),
                {
                    "source": source,
                    "is_dirty": int(is_dirty),
                    "confidence": confidence,
                    "image_data": image_data,
                    "notes": notes,
                }
            )
            conn.commit()
            logger.info(f"[BG] Saved detection: is_dirty={is_dirty}, conf={confidence:.2f}")

    except Exception as e:
        logger.error(f"[BG] Failed to save detection: {e}")


def get_active_recipients() -> list:
    if not ENABLE_DB:
        return []

    try:
        from sqlalchemy import text
        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT email FROM email_recipients WHERE active = 1")
            )
            rows = result.fetchall()
            return [r[0] for r in rows]

    except Exception as e:
        logger.error(f"Failed to fetch recipients: {e}")
        return []


def bg_send_notification(confidence: float):
    logger.info(f"[BG-EMAIL] Starting notification, EMAIL_AVAILABLE={EMAIL_AVAILABLE}")

    if not EMAIL_AVAILABLE:
        logger.warning("[BG-EMAIL] Email service not available")
        return

    recipients = get_active_recipients()
    logger.info(f"[BG-EMAIL] Found {len(recipients)} active recipients: {recipients}")

    if not recipients:
        logger.info("[BG-EMAIL] No active email recipients")
        return

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
        logger.info(f"[BG-EMAIL] Notification sent: success={success}")

    except Exception as e:
        logger.exception(f"[BG-EMAIL] Failed to send notification: {e}")


@router.post("/frame")
async def detect_frame(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        image_bytes = await file.read()
        logger.info(f"[DETECT] Received frame: {len(image_bytes)} bytes")

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                YOLO_SERVICE_URL,
                files={
                    "file": (
                        file.filename or "frame.jpg",
                        image_bytes,
                        file.content_type or "image/jpeg",
                    )
                },
            )

        if res.status_code != 200:
            logger.error(f"[DETECT] HF returned {res.status_code}: {res.text}")
            raise HTTPException(
                status_code=500,
                detail=f"HF ERROR {res.status_code}: {res.text}",
            )

        data = res.json()
        detections = data.get("detections", [])
        count = data.get("count", 0)

        max_conf = max(
            (d.get("confidence", 0.0) for d in detections),
            default=0.0,
        )

        is_dirty = count > 0
        logger.info(f"[DETECT] Result: is_dirty={is_dirty}, count={count}, conf={max_conf:.2f}")

        if background_tasks:
            background_tasks.add_task(
                bg_save_detection,
                source="live-camera",
                is_dirty=is_dirty,
                confidence=max_conf,
                image_data=image_bytes,
                notes=f"Detections: {count}",
            )

            if is_dirty:
                background_tasks.add_task(bg_send_notification, max_conf)

        return {
            "is_dirty": is_dirty,
            "confidence": round(max_conf, 3),
            "count": count,
            "detections": detections,
        }

    except HTTPException:
        raise
    except httpx.TimeoutException:
        logger.error("[DETECT] Timeout connecting to ML service")
        raise HTTPException(status_code=504, detail="ML service timeout")
    except Exception as e:
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail=str(e))
