"""
FloorEye YOLO Detector + FastAPI Service
CPU-only, HuggingFace & Railway stable
"""

# =========================
# Imports
# =========================
import os
import threading
import logging
import base64

import cv2
import numpy as np
from ultralytics import YOLO

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flooreye-ml")


# =========================
# Config
# =========================
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))
MODEL_PATH = os.getenv("MODEL_PATH", "models/best.pt")


# =========================
# YOLO Lazy Loader (Thread-safe)
# =========================
_model = None
_lock = threading.Lock()


def _get_model():
    """
    Lazy-load YOLO model (CPU only).
    Safe for Hugging Face / Railway.
    """
    global _model

    if _model is not None:
        return _model

    with _lock:
        if _model is not None:
            return _model

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"Model not found: {MODEL_PATH}")

        logger.info(f"🔄 Loading YOLO model from {MODEL_PATH}")
        _model = YOLO(MODEL_PATH)
        _model.to("cpu")

        # Warmup (important for first request latency)
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        _model(dummy, verbose=False)

        logger.info("✅ YOLO ready (CPU)")
        return _model


# =========================
# Detection Logic
# =========================
def detect(frame, conf_threshold=0.25, return_detections=False):
    model = _get_model()
    result = model(frame, verbose=False)[0]

    max_conf = 0.0
    detections = []

    if result.boxes is None:
        return (False, 0.0, []) if return_detections else (False, 0.0)

    for box in result.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        label = result.names[cls].lower()

        is_dirty = conf >= conf_threshold and ("dirty" in label or "kotor" in label)
        if is_dirty:
            max_conf = max(max_conf, conf)

        if return_detections and conf >= conf_threshold:
            detections.append({
                "class_id": cls,
                "class_name": result.names[cls],
                "confidence": conf,
                "bbox": box.xyxy[0].tolist(),
            })

    return (max_conf > 0, max_conf, detections) if return_detections else (max_conf > 0, max_conf)


# =========================
# FastAPI App
# =========================
app = FastAPI(
    title="FloorEye ML Service",
    version="2.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Schemas
# =========================
class FrameRequest(BaseModel):
    image: str  # base64 image


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: list[float]


class DetectionResponse(BaseModel):
    status: str
    is_dirty: bool
    max_confidence: float
    detections: list[Detection]


# =========================
# Routes
# =========================
@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/detect-frame", response_model=DetectionResponse)
async def detect_frame(req: FrameRequest):
    if not req.image:
        raise HTTPException(status_code=400, detail="Empty image")

    try:
        img_b64 = req.image.split(",", 1)[-1]
        frame = cv2.imdecode(
            np.frombuffer(base64.b64decode(img_b64), np.uint8),
            cv2.IMREAD_COLOR,
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image")

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image data")

    is_dirty, max_conf, dets = detect(frame, CONF_THRESHOLD, True)

    return DetectionResponse(
        status="DIRTY" if is_dirty else "CLEAN",
        is_dirty=is_dirty,
        max_confidence=round(max_conf, 3),
        detections=[
            Detection(
                class_id=d["class_id"],
                class_name=d["class_name"],
                confidence=round(d["confidence"], 3),
                bbox=[round(x, 2) for x in d["bbox"]],
            )
            for d in dets
        ],
    )


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
