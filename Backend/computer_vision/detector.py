from ultralytics import YOLO

MODEL_PATH = "computer_vision/models/yolov8n.pt"
_model = None

def get_model():
    global _model
    if _model is None:
        print(f"[INFO] Loading YOLOv8n model from {MODEL_PATH}")
        _model = YOLO(MODEL_PATH)
    return _model

def detect_dirty_floor(frame, conf_threshold: float = 0.25, debug: bool = False):
    """
    Deteksi lantai kotor menggunakan YOLOv8n
    Return: (is_dirty: bool, confidence: float)
    """
    try:
        model = get_model()
        results = model(frame, verbose=False)[0]
        max_conf = 0.0

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id].lower()

            if debug:
                print(f"[DEBUG] Deteksi: {label} ({conf:.2f})")

            if conf >= conf_threshold and ("dirty" in label or "kotor" in label):
                max_conf = max(max_conf, conf)

        return max_conf > 0, max_conf

    except Exception as e:
        print("[ERROR] YOLO detection error:", e)
        return False, 0.0
