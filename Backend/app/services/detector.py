"""
⚠️ DEPRECATED - DO NOT USE ⚠️

This file has been removed as part of the Railway/HuggingFace separation.

Railway backend MUST NOT perform ML inference locally.
All YOLO detection is handled by the HuggingFace ML service.

If you see this error, you have old code trying to import from this module.

SOLUTION:
- Use call_ml_service() from app/routes/detection.py instead
- Forward image bytes to YOLO_SERVICE_URL (HuggingFace)
- Do NOT import YOLO or cv2 in Railway backend

See: Backend/ARCHITECTURE.md for details
"""

def get_model():
    raise RuntimeError(
        "DEPRECATED: Local YOLO inference is not allowed in Railway backend. "
        "Use HuggingFace ML service instead (YOLO_SERVICE_URL)."
    )

def detect_dirty_floor(*args, **kwargs):
    raise RuntimeError(
        "DEPRECATED: Local YOLO inference is not allowed in Railway backend. "
        "Use call_ml_service() from app/routes/detection.py instead."
    )
