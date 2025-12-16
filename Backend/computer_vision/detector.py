"""Utilities for detecting dirty floor patches using a Ultralytics YOLOv8 model."""

from ultralytics import YOLO

MODEL_PATH = "computer_vision/models/best.pt"
_model = None


def get_model():
    global _model
    if _model is None:
        print(f"[INFO] Loading YOLO model from {MODEL_PATH}")
        _model = YOLO(MODEL_PATH)
    return _model


def detect_dirty_floor(frame, conf_threshold: float = 0.25, debug: bool = False):
    try:
        model = get_model()
        results = model(frame)[0]

        max_conf = 0.0
        names = getattr(model, "names", {})

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            label = (
                names.get(cls_id, str(cls_id))
                if isinstance(names, dict)
                else str(cls_id)
            ).lower()

            if debug:
                print(f"[DEBUG] Deteksi: {label} ({conf:.2f})")

            if conf >= conf_threshold and ("dirty" in label or "kotor" in label):
                max_conf = max(max_conf, conf)

        return (max_conf > 0, max_conf)

    except Exception as exc:
        print("[ERROR] YOLO detection error:", exc)
        return (False, 0.0)
