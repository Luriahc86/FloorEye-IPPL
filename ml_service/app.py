"""FloorEye ML Service - FastAPI app for YOLO inference only."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
import logging

from detector import detect

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

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
    """Health check endpoint."""
    return {"status": "healthy", "service": "ml"}


@app.post("/detect")
@app.post("/detect-image")
async def detect_floor(image: UploadFile = File(...)):
    """
    Detect dirty floor from uploaded image.
    
    Returns:
        {
            "is_dirty": bool,
            "confidence": float,
            "boxes": list  # optional, bounding box info
        }
    """
    try:
        image_bytes = await image.read()
        
        # Decode image
        frame = cv2.imdecode(
            np.frombuffer(image_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Run detection
        is_dirty, confidence = detect(frame, conf_threshold=CONF_THRESHOLD)
        
        return {
            "is_dirty": is_dirty,
            "confidence": round(confidence, 3),
            "conf_threshold": CONF_THRESHOLD,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
