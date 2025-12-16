"""YOLO detector for dirty floor detection (HF stable, best.pt)."""
import os
import threading
import logging

from ultralytics import YOLO  # ✅ YOLO di-import JELAS di atas (aman, belum load model)

logger = logging.getLogger("flooreye-detector")

_model = None
_model_lock = threading.Lock()


def _get_model():
    """
    Lazy-load YOLO model (best.pt) on first use.
    Safe for Hugging Face (CPU-only).
    """
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        # 🔒 FIXED: pakai best.pt
        model_path = os.getenv("MODEL_PATH", "models/best.pt")

        if not os.path.exists(model_path):
            raise RuntimeError(f"YOLO model not found: {model_path}")

        logger.info(f"🔄 Loading YOLO model from {model_path}")

        # ✅ Model baru di-load DI SINI (bukan saat import file)
        _model = YOLO(model_path)
        _model.to("cpu")  # HF = CPU only

        # 🔥 Warmup ringan (aman)
        try:
            import numpy as np
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            _model(dummy, verbose=False)
            logger.info("🔥 YOLO warmup completed")
        except Exception:
            logger.warning("Warmup skipped")

        logger.info(f"✅ YOLO model loaded successfully: {model_path}")
        return _model


def detect(frame, conf_threshold=0.25, return_detections=False):
    """
    Run YOLO inference on an OpenCV frame.

    Returns:
        (is_dirty, max_confidence[, detections])
    """
    model = _get_model()
    results = model(frame, verbose=False)[0]

    max_conf = 0.0
    detections = []

    if results.boxes is None:
        if return_detections:
            return False, 0.0, []
        return False, 0.0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results.names[cls_id].lower()

        is_dirty_detection = (
            conf >= conf_threshold
            and ("dirty" in label or "kotor" in label)
        )

        if is_dirty_detection:
            max_conf = max(max_conf, conf)

        if return_detections and conf >= conf_threshold:
            bbox = box.xyxy[0].cpu().numpy().tolist()
            detections.append({
                "class_id": cls_id,
                "class_name": results.names[cls_id],
                "confidence": conf,
                "bbox": bbox,
                "is_dirty": is_dirty_detection,
            })

    is_dirty = max_conf > 0

    if return_detections:
        return is_dirty, max_conf, detections
    return is_dirty, max_conf
