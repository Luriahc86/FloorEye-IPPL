from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from ultralytics import YOLO
import cv2
import numpy as np
import time

MODEL_PATH = "best.pt"

# Load model once (startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.time()
    print("[ML] Loading YOLO model...")
    app.state.model = YOLO(MODEL_PATH)
    print(f"[ML] Model loaded in {time.time() - start:.2f}s")
    yield
    print("[ML] Shutdown ML service")

app = FastAPI(
    title="FloorEye ML Service",
    version="1.0",
    lifespan=lifespan
)

# CORS (allow backend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Health Check
# ---------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ml"}

# ---------------------------
# Detection Endpoint
# ---------------------------
@app.post("/detect")
async def detect_floor(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        # Decode image
        img = cv2.imdecode(
            np.frombuffer(image_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        if img is None:
            return {"error": "Invalid image"}

        # Run inference
        model = app.state.model
        results = model(img)[0]

        # Process result
        is_dirty = len(results.boxes) > 0
        confidence = (
            float(results.boxes.conf.max())
            if is_dirty else 0.0
        )

        return {
            "is_dirty": is_dirty,
            "confidence": round(confidence, 3),
            "detections": len(results.boxes)
        }

    except Exception as e:
        print(f"[ERROR] ML detect: {e}")
        return {"error": str(e)}
