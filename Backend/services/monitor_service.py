import time
import cv2
import os
import requests
from store.db import get_connection
from services.email_service import send_email

ML_URL = os.getenv("ML_URL", "http://ml:8000/detect")
NOTIFY_INTERVAL = int(os.getenv("NOTIFY_INTERVAL", "60"))

def call_ml(frame):
    _, jpg = cv2.imencode(".jpg", frame)
    resp = requests.post(
        ML_URL,
        files={"file": jpg.tobytes()},
        timeout=10,
    )
    return resp.json()

def get_cameras():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cameras WHERE aktif = 1")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_active_email_recipients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r["email"] for r in rows]

def monitor_loop(stop):
    last_notif = {}
    print("[MONITOR] Started")

    while not stop.is_set():
        cams = get_cameras()
        emails = get_active_email_recipients()

        for cam in cams:
            cam_id = cam["id"]
            rtsp = cam["link"]

            now = time.time()
            if now - last_notif.get(cam_id, 0) < NOTIFY_INTERVAL:
                continue

            cap = cv2.VideoCapture(rtsp)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                continue

            result = call_ml(frame)
            is_dirty = result.get("is_dirty", False)
            confidence = result.get("confidence", 0.0)

            if not is_dirty:
                continue

            _, jpg = cv2.imencode(".jpg", frame)
            image_bytes = jpg.tobytes()

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO floor_events
                (source, is_dirty, confidence, image_data, notes)
                VALUES (%s,%s,%s,%s,%s)
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

            if emails:
                send_email(
                    f"[FloorEye] Lantai Kotor ({cam['nama']})",
                    f"Terdeteksi lantai kotor.\nConfidence: {confidence}",
                    emails,
                )

            last_notif[cam_id] = now

        time.sleep(5)
