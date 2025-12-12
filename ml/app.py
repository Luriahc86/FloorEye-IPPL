from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os

from detector import detect

CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))

app = FastAPI(
    title="FloorEye ML Service",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ml"}

@app.post("/detect")
async def detect_floor(image: UploadFile = File(...)):
    image_bytes = await image.read()

    frame = cv2.imdecode(
        np.frombuffer(image_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    try:
        is_dirty, confidence = detect(frame, conf_threshold=CONF_THRESHOLD)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    return {
        "is_dirty": is_dirty,
        "confidence": round(confidence, 3),
        "conf_threshold": CONF_THRESHOLD,
    }
