import cv2
import base64
import numpy as np
from store.db import get_connection
from computer_vision.detector import detect_dirty_floor


# ==========================================
# Image decoding utilities
# ==========================================

def decode_image_from_bytes(data: bytes):
    """Convert raw bytes to OpenCV image"""
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Gagal decode gambar dari bytes")

    return img


def decode_image_from_base64(b64_string: str):
    """Decode base64 (with or without prefix) into bytes"""
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    try:
        return base64.b64decode(b64_string)
    except Exception:
        raise ValueError("Base64 tidak valid")


# ==========================================
# Database insert helper
# ==========================================

def insert_detection(source, is_dirty, image_bytes, notes=None, confidence=None):
    """Insert hasil deteksi ke DB (image disimpan sebagai BLOB)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO floor_events
        (source, is_dirty, confidence, notes, image_data)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            source,
            int(is_dirty),
            confidence,
            notes,
            image_bytes,
        ),
    )

    conn.commit()
    event_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return event_id


# ==========================================
# Detection main logic
# ==========================================

def process_image_upload(file_bytes: bytes, notes=None):
    """Proses deteksi dari upload file"""
    frame = decode_image_from_bytes(file_bytes)
    is_dirty, confidence = detect_dirty_floor(frame, debug=False)

    event_id = insert_detection(
        source="upload",
        is_dirty=is_dirty,
        image_bytes=file_bytes,
        notes=notes,
        confidence=confidence,
    )

    return {
        "id": event_id,
        "source": "upload",
        "is_dirty": is_dirty,
        "confidence": confidence,
        "notes": notes,
    }


def process_camera_frame(image_base64: str, notes=None):
    """Proses deteksi dari kamera (base64)"""
    image_bytes = decode_image_from_base64(image_base64)
    frame = decode_image_from_bytes(image_bytes)

    is_dirty, confidence = detect_dirty_floor(frame, debug=False)

    event_id = insert_detection(
        source="camera",
        is_dirty=is_dirty,
        image_bytes=image_bytes,
        notes=notes,
        confidence=confidence,
    )

    return {
        "id": event_id,
        "source": "camera",
        "is_dirty": is_dirty,
        "confidence": confidence,
        "notes": notes,
    }
