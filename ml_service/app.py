from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import numpy as np
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flooreye-ml")

app = FastAPI(title="FloorEye ML Service")

try:
    logger.info("Loading YOLO model...")
    model = YOLO("models/best.pt")
    model.to("cpu")
    logger.info("YOLO model loaded")
except Exception as e:
    logger.error(f"YOLO load failed: {e}")
    raise RuntimeError(e)


@app.get("/")
def root():
    return {"status": "ml_service running"}


@app.post("/detect/frame")
async def detect_frame(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(400, "Empty image")

        img = cv2.imdecode(
            np.frombuffer(image_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        if img is None:
            raise HTTPException(400, "Invalid image data")

        h, w, _ = img.shape
        if h < 50 or w < 50:
            raise HTTPException(400, "Image too small")

        img = cv2.resize(img, (640, 640))

        results = model(img, conf=0.25)

        detections = []
        boxes = results[0].boxes

        if boxes is not None:
            for box in boxes:
                detections.append({
                    "class_id": int(box.cls[0]),
                    "confidence": float(box.conf[0]),
                    "bbox": [float(x) for x in box.xyxy[0]]
                })

        return {
            "detections": detections,
            "count": len(detections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Detection error")
        raise HTTPException(status_code=500, detail=str(e))
