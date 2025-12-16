"""Detection routes for image and frame processing."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import base64
import cv2
import numpy as np
import logging
import os
import requests
import tempfile

from app.utils.config import ENABLE_DB, ML_URL
from app.store.db import get_connection

logger = logging.getLogger(__name__)

router = APIRouter()

# Try to import email service
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


class FramePayload(BaseModel):
    image_base64: str
    notes: str | None = None


def decode_b64(b64: str) -> bytes:
    """Decode base64 string (with or without data URL prefix)."""
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


def call_ml_service(image_bytes: bytes):
    """Call ML service for detection."""
    try:
        resp = requests.post(
            ML_URL,
            files={"file": image_bytes},
            timeout=30,
        )
        return resp.json()
    except Exception as e:
        logger.error(f"ML service call failed: {e}")
        raise HTTPException(status_code=500, detail=f"ML service unavailable: {e}")


def get_all_recipients():
    """Get active email recipients."""
    if not ENABLE_DB:
        return []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.error(f"Failed to get email recipients: {e}")
        return []


def send_alert_email(image_bytes: bytes, confidence: float, source: str):
    """Send alert email with image attachment."""
    if not EMAIL_AVAILABLE:
        return
    
    recipients = get_all_recipients()
    if not recipients:
        return
    
    # Create temporary file for attachment
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_bytes)
        temp_path = tmp.name
    
    try:
        send_email(
            subject="⚠️ FloorEye Alert: Area Kotor Terdeteksi",
            body=f"Sistem mendeteksi area kotor ({source}).\\nConfidence: {confidence:.2f}",
            to_list=recipients,
            attachments=[temp_path],
        )
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    """
    Detect dirty floor from uploaded image file.
    
    Calls ML service, stores result in DB (if enabled), sends email alert.
    """
    try:
        raw = await file.read()
        
        # Call ML service
        result = call_ml_service(raw)
        detected = bool(result.get("is_dirty", False))
        confidence = float(result.get("confidence", 0.0))
        
        event_id = None
        event_data = {
            "is_dirty": detected,
            "confidence": confidence,
            "source": "upload",
        }
        
        # Store in DB if enabled
        if ENABLE_DB:
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute(
                    """
                    INSERT INTO floor_events (source, is_dirty, confidence, image_data)
                    VALUES (%s, %s, %s, %s)
                    """,
                    ("upload", int(detected), float(confidence), raw),
                )
                conn.commit()
                event_id = cursor.lastrowid
                
                cursor.execute(
                    "SELECT id, source, is_dirty, confidence, created_at FROM floor_events WHERE id = %s",
                    (event_id,),
                )
                event = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if event:
                    event_data = {
                        "id": event["id"],
                        "is_dirty": bool(event["is_dirty"]),
                        "confidence": float(event["confidence"]),
                        "created_at": event["created_at"].isoformat() if event["created_at"] else None,
                        "source": "upload",
                    }
            except Exception as e:
                logger.error(f"Failed to store detection in DB: {e}")
        
        # Send email alert
        if detected:
            send_alert_email(raw, confidence, source="upload")
        
        return event_data
    
    except Exception as e:
        logger.error(f"detect_image error: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")


@router.post("/frame")
async def detect_frame(payload: FramePayload):
    """
    Detect dirty floor from base64-encoded frame.
    
    Typically used by frontend webcam capture.
    """
    try:
        # Decode image
        image_bytes = decode_b64(payload.image_base64)
        
        # Call ML service
        result = call_ml_service(image_bytes)
        detected = bool(result.get("is_dirty", False))
        confidence = float(result.get("confidence", 0.0))
        
        event_id = None
        event_data = {
            "is_dirty": detected,
            "confidence": confidence,
            "source": "camera",
            "notes": payload.notes,
        }
        
        # Store in DB if enabled
        if ENABLE_DB:
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute(
                    """
                    INSERT INTO floor_events (source, is_dirty, confidence, image_data, notes)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    ("camera", int(detected), float(confidence), image_bytes, payload.notes),
                )
                conn.commit()
                event_id = cursor.lastrowid
                
                cursor.execute(
                    "SELECT id, source, is_dirty, confidence, created_at FROM floor_events WHERE id = %s",
                    (event_id,),
                )
                event = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if event:
                    event_data = {
                        "id": event["id"],
                        "is_dirty": bool(event["is_dirty"]),
                        "confidence": float(event["confidence"]),
                        "created_at": event["created_at"].isoformat() if event["created_at"] else None,
                        "source": "camera",
                        "notes": payload.notes,
                    }
            except Exception as e:
                logger.error(f"Failed to store detection in DB: {e}")
        
        # Send email alert
        if detected:
            send_alert_email(image_bytes, confidence, source="camera")
        
        return event_data
    
    except Exception as e:
        logger.error(f"detect_frame error: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")
