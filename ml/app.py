from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from ultralytics import YOLO
import cv2
import numpy as np
import time
import os

MODEL_PATH = os.getenv("MODEL_PATH", "computer_vision/models/best.pt")
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.time()
    print(f"[ML] Loading YOLO model from: {MODEL_PATH}")
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
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    try:
        model = app.state.model
        results = model(img)[0]

        is_dirty = False
        max_conf = 0.0
        dirty_boxes = 0

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = str(model.names.get(cls_id, "")).lower()

            if conf >= CONF_THRESHOLD and ("dirty" in label or "kotor" in label):
                is_dirty = True
                dirty_boxes += 1
                if conf > max_conf:
                    max_conf = conf

        return {
            "is_dirty": is_dirty,
            "confidence": round(max_conf, 3),
            "detections": dirty_boxes,
            "conf_threshold": CONF_THRESHOLD,
        }

    except Exception as e:
        print(f"[ERROR] ML detect: {e}")
        raise HTTPException(status_code=500, detail=str(e))
