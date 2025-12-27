from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import numpy as np
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flooreye-ml")

app = FastAPI(title="FloorEye ML Service")

# =========================
# Load YOLO model (CPU only)
# =========================
try:
    logger.info("Loading YOLO model...")
    model = YOLO("models/best.pt")
    model.to("cpu")
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    raise RuntimeError("YOLO model initialization failed")

# =========================
# Health Check
# =========================
@app.get("/")
def root():
    return {"status": "ml_service running"}

# =========================
# Detection Endpoint
# =========================
@app.post("/detect/frame")
async def detect_frame(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        image = cv2.imdecode(
            np.frombuffer(image_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        results = model(image)

        # Return YOLO JSON result
        return results[0].tojson()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")
