"""Background monitoring service for camera surveillance."""
import time
import cv2
import logging
import requests
from threading import Event
from typing import Dict, List

from app.utils.config import ML_URL, NOTIFY_INTERVAL, ENABLE_DB
from app.store.db import get_connection

logger = logging.getLogger(__name__)

# Email service import (optional)
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logger.warning("Email service not available")


def call_ml_service(frame) -> Dict:
    """Call ML service for detection."""
    try:
        _, jpg = cv2.imencode(".jpg", frame)
        resp = requests.post(
            ML_URL,
            files={"file": jpg.tobytes()},
            timeout=10,
        )
        return resp.json()
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
    
    This function runs in a background thread and periodically checks
    cameras for dirty floor detection. Never crashes the server.
    
    Args:
        stop_event: Threading event to signal shutdown
    """
    logger.info("[MONITOR] Started")
    last_notif: Dict[int, float] = {}
    
    while not stop_event.is_set():
        try:
            if not ENABLE_DB:
                logger.warning("[MONITOR] DB not enabled, sleeping...")
                time.sleep(30)
                continue
            
            cams = get_cameras()
            emails = get_active_email_recipients()
            
        except Exception as e:
            logger.error(f"[MONITOR] Failed fetching cameras/emails: {e}")
            time.sleep(5)
            continue
        
        for cam in cams:
            try:
                cam_id = cam["id"]
                rtsp = cam["link"]
                
                # Rate limiting
                now = time.time()
                if now - last_notif.get(cam_id, 0) < NOTIFY_INTERVAL:
                    continue
                
                # Capture frame
                cap = cv2.VideoCapture(rtsp)
                ret, frame = cap.read()
                cap.release()
                
                if not ret:
                    logger.warning(f"[MONITOR] Failed to read from camera {cam_id}")
                    continue
                
                # Detect via ML service
                result = call_ml_service(frame)
                is_dirty = result.get("is_dirty", False)
                confidence = result.get("confidence", 0.0)
                
                if not is_dirty:
                    continue
                
                logger.info(f"[MONITOR] Dirty floor detected on camera {cam_id}, confidence: {confidence}")
                
                # Encode frame to JPEG bytes
                _, jpg = cv2.imencode(".jpg", frame)
                image_bytes = jpg.tobytes()
                
                # Store in database
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO floor_events
                        (source, is_dirty, confidence, image_data, notes)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            f"camera_{cam_id}",
                            1,
                            confidence,
                            image_bytes,
                            f"Detected by monitor camera {cam_id}",
                        ),
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    logger.error(f"[MONITOR] Failed to store detection: {e}")
                
                # Send email notification
                if emails and EMAIL_AVAILABLE:
                    try:
                        send_email(
                            f"[FloorEye] Lantai Kotor ({cam['nama']})",
                            f"Terdeteksi lantai kotor.\\nConfidence: {confidence}",
                            emails,
                        )
                    except Exception as e:
                        logger.error(f"[MONITOR] Failed to send email: {e}")
                
                last_notif[cam_id] = now
                
            except Exception as e:
                cam_id = cam.get("id", "unknown") if isinstance(cam, dict) else "unknown"
                logger.error(f"[MONITOR] Error processing camera {cam_id}: {e}")
                continue
        
        time.sleep(5)
    
    logger.info("[MONITOR] Stopped")
