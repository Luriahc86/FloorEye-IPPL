import os
import cv2
import base64
import numpy as np
import time
from store.db import get_connection
from computer_vision.detector import detect_dirty_floor

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "..", "assets", "saved_images")

os.makedirs(SAVE_DIR, exist_ok=True)


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
    except:
        raise ValueError("Base64 tidak valid")


# ==========================================
# Save image helper
# ==========================================

def save_image(image, prefix="image"):
    """Simpan gambar hasil deteksi ke folder assets/saved_images"""
    filename = f"{prefix}_{int(time.time())}.jpg"
    file_path = os.path.join(SAVE_DIR, filename)

    success = cv2.imwrite(file_path, image)
    if not success:
        raise RuntimeError("Gagal menyimpan gambar")

    return file_path


# ==========================================
# Database insert helper
# ==========================================

def insert_detection(source, is_dirty, image_path, notes=None, confidence=None):
    """Insert hasil deteksi ke DB"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO floor_events (source, is_dirty, confidence, notes, image_path)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (source, int(is_dirty), confidence, notes, image_path),
    )

    conn.commit()
    new_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return new_id


# ==========================================
# Detection main logic
# ==========================================

def process_image_upload(file_bytes, notes=None):
    """Proses deteksi dari upload file"""
    frame = decode_image_from_bytes(file_bytes)
    detected = detect_dirty_floor(frame, debug=False)

    image_path = save_image(frame, "upload")
    event_id = insert_detection("upload", detected, image_path, notes)

    return {
        "id": event_id,
        "source": "upload",
        "is_dirty": detected,
        "notes": notes,
        "image_path": image_path,
    }


def process_camera_frame(image_base64, notes=None):
    """Proses deteksi dari kamera (base64)"""
    image_bytes = decode_image_from_base64(image_base64)
    frame = decode_image_from_bytes(image_bytes)

    detected = detect_dirty_floor(frame, debug=False)

    image_path = save_image(frame, "camera")
    event_id = insert_detection("camera", detected, image_path, notes)

    return {
        "id": event_id,
        "source": "camera",
        "is_dirty": detected,
        "notes": notes,
        "image_path": image_path,
    }
