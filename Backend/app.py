from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from computer_vision.detector import detect_dirty_floor

from contextlib import asynccontextmanager
import os
import sys
import cv2
import numpy as np
import base64
from typing import List, Optional

from store.db import get_connection
import threading
import time
import requests


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RTSP_URL = os.path.join(BASE_DIR, "assets", "test_video.mp4")

# Notification configuration
NOTIFY_INTERVAL = int(os.environ.get("NOTIFY_INTERVAL", "60"))
FONNTE_API_KEY = os.environ.get("FONNTE_API_KEY", "mjXwZ3JHzXryywVcFMHL")
if not os.environ.get("FONNTE_API_KEY"):
    print("[WARN] FONNTE_API_KEY not set; using default key (may fail). Set env var FONNTE_API_KEY.")

if "linux" in sys.platform or os.environ.get("DISPLAY") is None:
    cv2.setUseOptimized(True)


# =================================================================
# MODELS
# =================================================================
class CameraFramePayload(BaseModel):
    image_base64: str
    notes: Optional[str] = None


class HistoryItem(BaseModel):
    id: int
    source: str
    is_dirty: bool
    confidence: Optional[float]
    notes: Optional[str]
    created_at: str


class WARecipientCreate(BaseModel):
    phone: str
    active: Optional[bool] = True


# =================================================================
# FASTAPI LIFESPAN
# =================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] FloorEye Backend Started")
    print(f"[INFO] Video Source (test): {RTSP_URL}")

    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_cameras_loop, args=(stop_event,), daemon=True)
    monitor_thread.start()

    yield

    print("[INFO] Server Shutdown")
    stop_event.set()
    monitor_thread.join(timeout=2)


app = FastAPI(
    title="FloorEye Backend",
    version="2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================================================
# IMAGE UTILS
# =================================================================
def decode_image_from_bytes(data: bytes):
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Gagal decode gambar")
    return img


def decode_image_from_base64(b64_string: str) -> bytes:
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    return base64.b64decode(b64_string)


# =================================================================
# DATABASE
# =================================================================
def insert_detection_to_db(source, is_dirty, image_path, confidence=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO floor_events (source, is_dirty, confidence, notes, image_path)
        VALUES (%s, %s, %s, %s, %s)
    """, (source, int(is_dirty), confidence, notes, image_path))

    conn.commit()
    new_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return new_id


def get_cameras_from_db():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nama, lokasi, link, aktif FROM cameras")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def get_active_wa_recipients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT phone FROM wa_recipients WHERE active = 1")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [r["phone"] for r in rows]


# =================================================================
# WHATSAPP (FONNTE)
# =================================================================
def send_whatsapp(phone: str, text: str):
    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_API_KEY}
    data = {"target": phone, "message": text}

    try:
        res = requests.post(url, headers=headers, data=data, timeout=15)
        code = getattr(res, "status_code", None)
        text_res = getattr(res, "text", "")
        print(f"[WA RESPONSE] status={code} body={text_res}")
        # interpret success
        if code and 200 <= code < 300:
            return True
        else:
            return False
    except Exception as e:
        print("[WA ERROR]", e)
        return False


# =================================================================
# CAMERA MONITORING LOOP
# =================================================================
def monitor_cameras_loop(stop_event):
    last_notification = {}
    print("[INFO] Camera monitor thread started")

    while not stop_event.is_set():
        try:
            cameras = get_cameras_from_db()
            wa_list = get_active_wa_recipients()

            for cam in cameras:
                if not cam["aktif"]:
                    continue

                cam_id = cam["id"]
                rtsp = cam["link"]
                src_name = cam["nama"] or f"camera_{cam_id}"

                now = time.time()
                if now - last_notification.get(cam_id, 0) < NOTIFY_INTERVAL:
                    continue

                cap = cv2.VideoCapture(rtsp)
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    print(f"[WARN] No frame from camera {cam_id}")
                    continue

                detected = detect_dirty_floor(frame, debug=False)

                if detected:
                    save_dir = os.path.join(BASE_DIR, "assets", "saved_images")
                    os.makedirs(save_dir, exist_ok=True)

                    filename = f"cam{cam_id}_{int(time.time())}.jpg"
                    file_path = os.path.join(save_dir, filename)
                    cv2.imwrite(file_path, frame)

                    insert_detection_to_db(
                        source=f"camera_{cam_id}",
                        is_dirty=True,
                        image_path=file_path,
                        confidence=None,
                        notes=f"Detected on camera {src_name}",
                    )

                    for phone in wa_list:
                        send_whatsapp(
                            phone,
                            f"⚠️ *Lantai kotor terdeteksi!*\nKamera: {src_name}\nWaktu: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        )

                    last_notification[cam_id] = now

        except Exception as e:
            print("[ERROR] monitor loop error:", e)

        time.sleep(5)


# =================================================================
# ROUTES
# =================================================================

@app.get("/")
def root():
    return {"message": "FloorEye backend berjalan 🚀", "status": "ok"}


@app.post("/wa-recipients")
def add_wa_recipient(payload: WARecipientCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO wa_recipients (phone, active) VALUES (%s, %s)",
        (payload.phone, int(payload.active))
    )
    conn.commit()

    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return {"id": new_id, "message": "Nomor WA ditambahkan"}


@app.get("/wa-recipients")
def get_wa_recipients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM wa_recipients ORDER BY id DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


@app.post("/test-wa")
def test_wa(payload: dict):
    """POST test WA. Payload: { "phone": "62812...", "message": "..." }
       If phone omitted, sends to active recipients from DB.
    """
    phone = payload.get("phone")
    message = payload.get("message", "[FloorEye] Test notifikasi WA")

    if not phone:
        try:
            phones = get_active_wa_recipients()
        except Exception as e:
            print("[ERROR] reading WA recipients:", e)
            raise HTTPException(status_code=500, detail="Failed reading recipients from DB")

        if not phones:
            return {"sent": False, "message": "No WA recipients configured"}

        results = {}
        for p in phones:
            ok = send_whatsapp(p, message)
            results[p] = ok

        return {"sent": any(results.values()), "results": results}
    else:
        ok = send_whatsapp(phone, message)
        return {"sent": ok, "phone": phone}


@app.get("/test-wa")
def test_wa_get():
    """Convenience GET for quick browser test: sends to active recipients."""
    try:
        phones = get_active_wa_recipients()
    except Exception as e:
        print("[ERROR] reading WA recipients:", e)
        raise HTTPException(status_code=500, detail="Failed reading recipients from DB")

    if not phones:
        return {"sent": False, "message": "No WA recipients configured"}

    results = {}
    for p in phones:
        ok = send_whatsapp(p, "[FloorEye] Test notifikasi WA (GET)")
        results[p] = ok

    return {"sent": any(results.values()), "results": results}


@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...), notes: Optional[str] = None):

    file_bytes = await file.read()
    frame = decode_image_from_bytes(file_bytes)

    is_dirty = detect_dirty_floor(frame, debug=False)

    save_dir = os.path.join(BASE_DIR, "assets", "saved_images")
    os.makedirs(save_dir, exist_ok=True)

    filename = f"upload_{int(time.time())}.jpg"
    file_path = os.path.join(save_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    new_id = insert_detection_to_db("upload", is_dirty, file_path, None, notes)

    return {
        "id": new_id,
        "source": "upload",
        "is_dirty": is_dirty,
        "notes": notes,
        "image_path": file_path,
        "message": "Deteksi berhasil"
    }


@app.post("/detect/frame")
async def detect_frame(payload: CameraFramePayload):

    image_bytes = decode_image_from_base64(payload.image_base64)
    frame = decode_image_from_bytes(image_bytes)

    is_dirty = detect_dirty_floor(frame, debug=False)

    save_dir = os.path.join(BASE_DIR, "assets", "saved_images")
    os.makedirs(save_dir, exist_ok=True)

    filename = f"camera_{int(time.time())}.jpg"
    file_path = os.path.join(save_dir, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    new_id = insert_detection_to_db("camera", is_dirty, file_path, None, payload.notes)

    return {
        "id": new_id,
        "source": "camera",
        "is_dirty": is_dirty,
        "notes": payload.notes,
        "image_path": file_path,
        "message": "Deteksi kamera disimpan"
    }


@app.get("/history", response_model=List[HistoryItem])
def get_history(limit: int = 50, offset: int = 0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, source, is_dirty, confidence, notes, created_at
        FROM floor_events
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))

    rows = cursor.fetchall()

    events = [
        HistoryItem(
            id=r["id"],
            source=r["source"],
            is_dirty=bool(r["is_dirty"]),
            confidence=r["confidence"],
            notes=r["notes"],
            created_at=r["created_at"].isoformat()
        )
        for r in rows
    ]

    cursor.close()
    conn.close()

    return events


@app.get("/image/{event_id}")
def get_image(event_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT image_path FROM floor_events WHERE id = %s", (event_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Gambar tidak ditemukan")

    file_path = row[0]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File fisik tidak ada")

    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type="image/jpeg")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
