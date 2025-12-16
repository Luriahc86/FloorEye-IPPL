"""YOLO detector service with lazy singleton loading."""
import logging
import threading
from typing import Tuple

from app.utils.config import MODEL_PATH

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()


def get_model():
    """Lazy-load YOLO model on first use (thread-safe singleton)."""
    global _model
    if _model is not None:
        return _model
    
    with _model_lock:
        if _model is not None:
            return _model
        
        logger.info(f"Loading YOLO model from {MODEL_PATH}")
        from ultralytics import YOLO
        _model = YOLO(MODEL_PATH)
        logger.info("YOLO model loaded successfully")
        return _model


def detect_dirty_floor(frame, conf_threshold: float = 0.25) -> Tuple[bool, float]:
    """
    Detect dirty floor patches in a frame using YOLO.
    
    Args:
        frame: OpenCV image (numpy array)
        conf_threshold: Confidence threshold for detection
    
    Returns:
        (is_dirty: bool, max_confidence: float)
    """
    try:
        model = get_model()
        results = model(frame, verbose=False)[0]
        
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
            
            # Check for dirty/kotor labels
            if conf >= conf_threshold and ("dirty" in label or "kotor" in label):
                max_conf = max(max_conf, conf)
        
        return (max_conf > 0, max_conf)
    
    except Exception as exc:
        logger.error(f"YOLO detection error: {exc}")
        return (False, 0.0)
