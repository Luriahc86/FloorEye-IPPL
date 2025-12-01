import cv2
from ultralytics import YOLO

MODEL_PATH = "computer_vision/models/best.pt"
print(f"[INFO] Loading YOLO model from {MODEL_PATH}")

model = YOLO(MODEL_PATH)

def detect_dirty_floor(frame, conf_threshold: float = 0.25, debug: bool = False) -> bool:
    """
    Deteksi lantai kotor menggunakan YOLOv8 lokal.
    Mengembalikan True jika ditemukan objek dengan class 'dirty' atau 'kotor'.
    """
    try:
        results = model(frame)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id].lower()

            if debug:
                print(f"[DEBUG] Deteksi: {label} ({conf:.2f})")

            if conf >= conf_threshold:
                if "dirty" in label or "kotor" in label:
                    return True

        return False

    except Exception as e:
        print("[ERROR] YOLO detection error:", e)
        return False
