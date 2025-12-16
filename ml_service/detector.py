"""YOLO detector for dirty floor detection (CPU-only, HF/Railway safe)."""
import os
import threading
import logging
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger("flooreye-detector")

_model = None
_lock = threading.Lock()


def _get_model():
    global _model
    if _model is not None:
        return _model

    with _lock:
        if _model is not None:
            return _model

        model_path = os.getenv("MODEL_PATH", "models/best.pt")
        if not os.path.exists(model_path):
            raise RuntimeError(f"Model not found: {model_path}")

        logger.info(f"🔄 Loading YOLO model: {model_path}")
        model = YOLO(model_path)
        model.to("cpu")

        # warmup ringan
        try:
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            model(dummy, verbose=False)
        except Exception:
            pass

        _model = model
        logger.info("✅ YOLO ready (CPU)")
        return _model


def detect(frame, conf_threshold=0.25, return_detections=False):
    model = _get_model()
    result = model(frame, verbose=False)[0]

    max_conf = 0.0
    detections = []

    if result.boxes is None:
        return (False, 0.0, []) if return_detections else (False, 0.0)

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = result.names[cls_id].lower()

        is_dirty = conf >= conf_threshold and (
            "dirty" in label or "kotor" in label
        )

        if is_dirty:
            max_conf = max(max_conf, conf)

        if return_detections and conf >= conf_threshold:
            detections.append({
                "class_id": cls_id,
                "class_name": result.names[cls_id],
                "confidence": conf,
                "bbox": box.xyxy[0].cpu().numpy().tolist(),
            })

    return (
        (max_conf > 0, max_conf, detections)
        if return_detections
        else (max_conf > 0, max_conf)
    )
