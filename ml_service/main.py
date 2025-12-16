"""FloorEye ML Service - Live Camera Frame Inference API"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import os
import logging

from detector import detect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flooreye-ml")

CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))

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


class FrameRequest(BaseModel):
    image: str


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


@app.get("/")
def root():
    return {"status": "ok", "endpoints": ["/health", "/detect-frame"]}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/detect-frame", response_model=DetectionResponse)
async def detect_frame(req: FrameRequest):
    if not req.image:
        raise HTTPException(400, "Empty image")

    image_b64 = req.image.split(",", 1)[-1]
    try:
        img_bytes = base64.b64decode(image_b64)
        frame = cv2.imdecode(
            np.frombuffer(img_bytes, np.uint8),
            cv2.IMREAD_COLOR,
        )
    except Exception:
        raise HTTPException(400, "Invalid image")

    if frame is None:
        raise HTTPException(400, "Decode failed")

    is_dirty, max_conf, dets = detect(
        frame, CONF_THRESHOLD, return_detections=True
    )

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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
