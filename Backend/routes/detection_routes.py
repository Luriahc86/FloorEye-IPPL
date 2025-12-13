from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import cv2
import numpy as np
import io

from store.db import get_connection
from computer_vision.detector import detect_dirty_floor
from services.email_service import send_email

router = APIRouter()


class FramePayload(BaseModel):
    image_base64: str
    notes: str | None = None


def decode_b64(b64: str) -> bytes:
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


def decode_bytes(data: bytes):
    arr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def get_all_recipients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in rows]


@router.post("/frame")
async def detect_frame(payload: FramePayload):
    try:
        # Decode image
        image_bytes = decode_b64(payload.image_base64)
        frame = decode_bytes(image_bytes)

        detected, confidence = detect_dirty_floor(frame, debug=False)

        # Save event (NO image_path, NO file)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            INSERT INTO floor_events 
            (source, is_dirty, confidence, image_data, notes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                "camera",
                int(detected),
                float(confidence),
                image_bytes,   # BLOB ONLY
                payload.notes,
            ),
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

        # 🔥 SEND EMAIL (IN-MEMORY ATTACHMENT)
        if detected:
            recipients = get_all_recipients()
            print("[INFO] DIRTY FLOOR DETECTED, sending email:", recipients)

            send_email(
                subject="⚠️ FloorEye Alert: Area Kotor Terdeteksi",
                body=f"Sistem mendeteksi area kotor.\nConfidence: {confidence:.2f}",
                to_list=recipients,
                attachments=[
                    {
                        "filename": f"event_{event_id}.jpg",
                        "content": image_bytes,
                        "mime": "image/jpeg",
                    }
                ],
            )

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
        raise HTTPException(500, f"Detection failed: {str(e)}")
