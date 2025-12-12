from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from ultralytics import YOLO
import cv2
import numpy as np
import time
import os

from detector import detect_dirty_floor

MODEL_PATH = os.getenv("MODEL_PATH", "models/yolov8n.pt")
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.time()
    print(f"[ML] Loading YOLO model from {MODEL_PATH}")
    app.state.model = YOLO(MODEL_PATH)
    print(f"[ML] Model loaded in {time.time() - start:.2f}s")
    yield
    print("[ML] Shutdown ML service")


app = FastAPI(
    title="FloorEye ML Service",
    version="1.0",
    lifespan=lifespan
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
async def detect_floor(file: UploadFile = File(...)):
    image_bytes = await file.read()

    frame = cv2.imdecode(
        np.frombuffer(image_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )

    if frame is None:
        raise HTTPException(400, "Invalid image")

    model = app.state.model
    results = model(frame, verbose=False)[0]

    is_dirty, confidence = detect_dirty_floor(
        results,
        conf_threshold=CONF_THRESHOLD
    )

    return {
        "is_dirty": is_dirty,
        "confidence": round(confidence, 3),
        "conf_threshold": CONF_THRESHOLD,
    }
