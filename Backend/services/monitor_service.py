import time
import cv2
import os
import requests
from store.db import get_connection
from services.email_service import send_email

ML_URL = os.getenv("ML_URL", "http://ml:8000/detect")
NOTIFY_INTERVAL = int(os.getenv("NOTIFY_INTERVAL", "60"))

<<<<<<< HEAD
def call_ml(frame):
    _, jpg = cv2.imencode(".jpg", frame)
    resp = requests.post(
        ML_URL,
        files={"file": jpg.tobytes()},
        timeout=10,
    )
    return resp.json()
=======
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(BACKEND_DIR, "assets", "saved_images")
os.makedirs(SAVE_DIR, exist_ok=True)

def save_frame_as_jpeg(frame, prefix: str):
    filename = f"{prefix}_{int(time.time())}.jpg"
    file_path = os.path.join(SAVE_DIR, filename)
    ok = cv2.imwrite(file_path, frame)
    if not ok:
        raise RuntimeError("Gagal menyimpan gambar")
    return file_path
>>>>>>> dev

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
        try:
            cams = get_cameras()
            emails = get_active_email_recipients()
        except Exception as e:
            print(f"[MONITOR][ERROR] Failed fetching cameras/emails: {e}")
            time.sleep(5)
            continue

        for cam in cams:
            try:
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

<<<<<<< HEAD
                if not is_dirty:
                    continue
=======
                if detected:
                    # Encode frame ke JPEG bytes untuk disimpan ke database
                    _, frame_bytes = cv2.imencode('.jpg', frame)
                    image_data = frame_bytes.tobytes()
                    image_path = None
                    try:
                        image_path = save_frame_as_jpeg(frame, f"camera_{cam_id}")
                    except Exception as e:
                        print(f"[ERROR] Failed saving image to disk: {e}")

                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO floor_events (source,is_dirty,confidence,image_data,image_path,notes) VALUES (%s,%s,%s,%s,%s,%s)",
                            (f"camera_{cam_id}", int(detected), float(confidence), image_data, image_path, f"Detected by monitor on camera {cam_id}"),
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Failed insert detection to DB: {e}")
>>>>>>> dev

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
            except Exception as e:
                cam_id = cam.get("id", "unknown") if isinstance(cam, dict) else "unknown"
                print(f"[MONITOR][ERROR] Camera {cam_id}: {e}")
                continue

        time.sleep(5)
