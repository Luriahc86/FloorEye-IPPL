"""YOLO detector for dirty floor detection with detailed results."""
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
        
        model_path = os.getenv("MODEL_PATH", "yolov8n.pt")  # Auto-download if not exists
        logger.info(f"Loading YOLO model from {model_path}")
        
        from ultralytics import YOLO  # lazy import
        
        _model = YOLO(model_path)
        logger.info(f"YOLO model loaded successfully: {model_path}")
        return _model


def detect(frame, conf_threshold=0.25, return_detections=False):
    """
    Run YOLO inference on an OpenCV frame.
    
    Args:
        frame: OpenCV image (numpy array)
        conf_threshold: Confidence threshold for detection
        return_detections: If True, return detailed detection list
    
    Returns:
        If return_detections=False:
            (is_dirty: bool, max_confidence: float)
        If return_detections=True:
            (is_dirty: bool, max_confidence: float, detections: list)
    """
    model = _get_model()
    results = model(frame, verbose=False)[0]
    
    max_conf = 0.0
    detections = []
    
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results.names[cls_id].lower()
        
        # Check if this is a dirty/kotor detection
        is_dirty_detection = conf >= conf_threshold and ("dirty" in label or "kotor" in label)
        
        if is_dirty_detection:
            max_conf = max(max_conf, conf)
        
        # Collect all detections if requested
        if return_detections and conf >= conf_threshold:
            bbox = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
            detections.append({
                "class_id": cls_id,
                "class_name": results.names[cls_id],
                "confidence": conf,
                "bbox": bbox,
                "is_dirty": is_dirty_detection
            })
    
    is_dirty = max_conf > 0
    
    if return_detections:
        return is_dirty, max_conf, detections
    else:
        return is_dirty, max_conf
