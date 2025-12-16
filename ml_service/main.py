"""FloorEye ML Service - Live Camera Frame Inference API (HF Stable)"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import os
import logging

from detector import detect

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger("flooreye-ml")

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))

# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
app = FastAPI(
    title="FloorEye ML Service - Live Camera",
    description="YOLO inference for base64 live camera frames (Hugging Face)",
    version="2.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------
class FrameRequest(BaseModel):
    image: str  # base64 JPEG (with or without data:image prefix)


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


# -------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    logger.info("🚀 FloorEye ML Service started (Hugging Face)")
    logger.info(f"CONF_THRESHOLD={CONF_THRESHOLD}")


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "service": "FloorEye ML Service",
        "version": "2.1",
        "mode": "live_camera_only",
        "endpoints": ["/health", "/detect-frame"],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ml",
        "model_loaded": False,  # YOLO lazy-loaded
    }


@app.post("/detect-frame", response_model=DetectionResponse)
async def detect_frame(request: FrameRequest):
    try:
        if not request.image:
            raise HTTPException(status_code=400, detail="Empty image payload")

        image_b64 = request.image
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(image_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image")

        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        logger.info(f"Frame received: shape={frame.shape}")

        is_dirty, max_conf, detections_data = detect(
            frame,
            conf_threshold=CONF_THRESHOLD,
            return_detections=True,
        )

        status = "DIRTY" if is_dirty else "CLEAN"

        detections = [
            Detection(
                class_id=d["class_id"],
                class_name=d["class_name"],
                confidence=round(d["confidence"], 3),
                bbox=[round(x, 2) for x in d["bbox"]],
            )
            for d in detections_data
        ]

        logger.info(
            f"Result={status}, max_conf={max_conf:.3f}, detections={len(detections)}"
        )

        return DetectionResponse(
            status=status,
            is_dirty=is_dirty,
            max_confidence=round(max_conf, 3),
            detections=detections,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail="Detection failed")


# -------------------------------------------------------------------
# Entrypoint (Hugging Face)
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,  # HF FIXED PORT
        log_level="info",
    )
