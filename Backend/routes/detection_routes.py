from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import time
import base64
import cv2
import numpy as np
import os

from store.db import get_connection
from computer_vision.detector import detect_dirty_floor

router = APIRouter()

class FramePayload(BaseModel):
    image_base64: str
    notes: str | None = None

def decode_bytes(data):
    arr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def decode_b64(b64):
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)

@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    raw = await file.read()
    frame = decode_bytes(raw)

    detected, confidence = detect_dirty_floor(frame, debug=False)

    # Save image data to database (LONGBLOB), not file system
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO floor_events (source,is_dirty,confidence,image_data) VALUES (%s,%s,%s,%s)",
        ("upload", int(detected), float(confidence), raw),
    )
    conn.commit()
    event_id = cursor.lastrowid
    
    # Get the inserted event to return full data
    cursor.execute("SELECT id, source, is_dirty, confidence, created_at FROM floor_events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "id": event["id"],
        "is_dirty": bool(event["is_dirty"]),
        "confidence": float(event["confidence"]),
        "created_at": event["created_at"].isoformat() if event["created_at"] else None,
        "source": "upload",
    }

@router.post("/frame")
async def detect_frame(payload: FramePayload):
    """Detect from base64 encoded image frame."""
    try:
        image_bytes = decode_b64(payload.image_base64)
        frame = decode_bytes(image_bytes)

        detected, confidence = detect_dirty_floor(frame, debug=False)

        # Save image data to database (LONGBLOB), not file system
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO floor_events (source,is_dirty,confidence,image_data,notes) VALUES (%s,%s,%s,%s,%s)",
            ("camera", int(detected), float(confidence), image_bytes, payload.notes),
        )
        conn.commit()
        event_id = cursor.lastrowid
        
        # Get the inserted event to return full data
        cursor.execute("SELECT id, source, is_dirty, confidence, created_at FROM floor_events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        cursor.close()
        conn.close()

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
