import time
import threading
import cv2
import os
import numpy as np
from store.db import get_connection
from services.email_service import send_email
from computer_vision.detector import detect_dirty_floor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "..", "assets", "saved_images")
os.makedirs(SAVE_DIR, exist_ok=True)

NOTIFY_INTERVAL = int(os.getenv("NOTIFY_INTERVAL", "60"))

def get_cameras():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cameras WHERE aktif = 1")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_active_email_recipients():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r["email"] for r in rows]
    except Exception as e:
        print(f"[ERROR] get_active_email_recipients: {e}")
        return []

def monitor_loop(stop):
    last_notif = {}
    print("[INFO] Monitor thread started")

    while not stop.is_set():
        try:
            cams = get_cameras()
            emails = get_active_email_recipients()

            print(f"[DEBUG] Found {len(cams)} cameras, {len(emails)} email recipients")

            for cam in cams:
                cam_id = cam["id"]
                rtsp = cam["link"]

                now = time.time()
                if now - last_notif.get(cam_id, 0) < NOTIFY_INTERVAL:
                    continue

                print(f"[DEBUG] Processing camera {cam_id}: {rtsp}")
                cap = cv2.VideoCapture(rtsp)
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    print(f"[WARN] No frame from camera {cam_id}")
                    continue

                detected = detect_dirty_floor(frame, debug=False)
                print(f"[DEBUG] Camera {cam_id} dirty={detected}")

                if detected:
                    filename = f"cam{cam_id}_{int(time.time())}.jpg"
                    filepath = os.path.join(SAVE_DIR, filename)
                    cv2.imwrite(filepath, frame)
                    print(f"[INFO] Saved image: {filepath}")

                    if emails:
                        print(f"[INFO] Sending alert to {len(emails)} recipients")
                        ok = send_email(
                            f"[FloorEye] Lantai Kotor Terdeteksi ({cam['nama']})",
                            f"Otomatis mendeteksi lantai kotor pada kamera {cam['nama']} pada {time.strftime('%Y-%m-%d %H:%M:%S')}.",
                            emails,
                            [filepath]
                        )
                        print(f"[INFO] Email send result: {ok}")
                    else:
                        print("[WARN] No active email recipients; skipping notification")

                    last_notif[cam_id] = now
        except Exception as e:
            print(f"[ERROR] monitor_loop: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(5)
