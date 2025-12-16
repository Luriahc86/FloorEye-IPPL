"""YOLO detector for dirty floor detection."""
import os
import threading
import logging

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()


def _get_model():
    """
    Lazy-load YOLO model on first use.
    
    NOTE: ultralytics is intentionally imported ONLY inside this function.
    """
    global _model
    if _model is not None:
        return _model
    
    with _model_lock:
        if _model is not None:
            return _model
        
        model_path = os.getenv("MODEL_PATH", "models/yolov8n.pt")
        logger.info(f"Loading YOLO model from {model_path}")
        
        from ultralytics import YOLO  # lazy import
        
        _model = YOLO(model_path)
        logger.info("YOLO model loaded successfully")
        return _model


def _detect_dirty_floor_from_results(results, conf_threshold=0.25):
    """
    Extract dirty floor detection from YOLO results.
    
    Returns:
        (is_dirty: bool, confidence: float)
    """
    max_conf = 0.0
    
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results.names[cls_id].lower()
        
        if conf >= conf_threshold and ("dirty" in label or "kotor" in label):
            max_conf = max(max_conf, conf)
    
    return max_conf > 0, max_conf


def detect(frame, conf_threshold=0.25):
    """
    Run YOLO inference on an OpenCV frame.
    
    Args:
        frame: OpenCV image (numpy array)
        conf_threshold: Confidence threshold for detection
    
    Returns:
        (is_dirty: bool, confidence: float)
    """
    model = _get_model()
    results = model(frame, verbose=False)[0]
    return _detect_dirty_floor_from_results(results, conf_threshold=conf_threshold)
