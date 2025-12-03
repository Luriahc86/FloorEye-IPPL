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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "..", "assets", "saved_images")
os.makedirs(SAVE_DIR, exist_ok=True)

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

    detected = detect_dirty_floor(frame, debug=False)

    filename = f"upload_{int(time.time())}.jpg"
    path = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(path, frame)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO floor_events (source,is_dirty,image_path) VALUES (%s,%s,%s)",
        ("upload", int(detected), path),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"detected": detected, "image_path": path}
