from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import base64
import cv2
import numpy as np
import os
import tempfile

from store.db import get_connection
from computer_vision.detector import detect_dirty_floor
from services.email_service import send_email

router = APIRouter()


# =========================
# Schemas
# =========================
class FramePayload(BaseModel):
    image_base64: str
    notes: str | None = None


# =========================
# Helpers
# =========================
def decode_bytes(data: bytes):
    arr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def decode_b64(b64: str):
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


def get_all_recipients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in rows]


def send_alert_email(image_bytes: bytes, confidence: float, source: str):
    """Send alert email with temporary image attachment."""
    recipients = get_all_recipients()
    if not recipients:
        return

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_bytes)
        temp_path = tmp.name

    try:
        send_email(
            subject="⚠️ FloorEye Alert: Area Kotor Terdeteksi",
            body=f"Sistem mendeteksi area kotor ({source}).\nConfidence: {confidence:.2f}",
            to_list=recipients,
            attachments=[temp_path],
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================
# Routes
# =========================
@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    try:
        raw = await file.read()
        frame = decode_bytes(raw)

        detected, confidence = detect_dirty_floor(frame, debug=False)

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

        if detected:
            send_alert_email(raw, confidence, source="upload")

        return {
            "id": event["id"],
            "is_dirty": bool(event["is_dirty"]),
            "confidence": float(event["confidence"]),
            "created_at": event["created_at"].isoformat() if event["created_at"] else None,
            "source": "upload",
        }

    except Exception as e:
        print(f"[ERROR] detect_image: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")


@router.post("/frame")
async def detect_frame(payload: FramePayload):
    try:
        image_bytes = decode_b64(payload.image_base64)
        frame = decode_bytes(image_bytes)

        detected, confidence = detect_dirty_floor(frame, debug=False)

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

        if detected:
            send_alert_email(image_bytes, confidence, source="camera")

        return {
            "id": event["id"],
            "is_dirty": bool(event["is_dirty"]),
            "confidence": float(event["confidence"]),
            "created_at": event["created_at"].isoformat() if event["created_at"] else None,
            "source": "camera",
            "notes": payload.notes,
        }

    except Exception as e:
        print(f"[ERROR] detect_frame: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")
