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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))

app = FastAPI(
    title="FloorEye ML Service - Live Camera",
    description="Real-time YOLO inference for live camera frames (base64)",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FrameRequest(BaseModel):
    """Request model for live camera frame"""
    image: str  # base64 encoded JPEG image (without data:image prefix)


class Detection(BaseModel):
    """Single detection result"""
    class_id: int
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]


class DetectionResponse(BaseModel):
    """Response model for detection"""
    status: str  # "CLEAN" or "DIRTY"
    is_dirty: bool
    max_confidence: float
    detections: list[Detection]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "FloorEye ML Service",
        "version": "2.0",
        "mode": "live_camera_only",
        "endpoints": ["/health", "/detect-frame"]
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml", "mode": "live_camera"}


@app.post("/detect-frame", response_model=DetectionResponse)
async def detect_frame(request: FrameRequest):
    """
    Detect dirty floor from live camera frame.
    
    Accepts base64-encoded JPEG image from frontend camera.
    NO file upload, NO webcam access, ONLY base64 frames.
    
    Args:
        request: FrameRequest with base64 image
    
    Returns:
        DetectionResponse with status and detections
    """
    try:
        # Decode base64 to bytes
        # Remove data URL prefix if present
        image_b64 = request.image
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_b64)
        
        # Decode to OpenCV image (in-memory)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        logger.info(f"Processing frame: shape={frame.shape}, dtype={frame.dtype}")
        
        # Run YOLO detection
        is_dirty, max_confidence, detections_data = detect(
            frame, 
            conf_threshold=CONF_THRESHOLD,
            return_detections=True
        )
        
        # Build response
        status = "DIRTY" if is_dirty else "CLEAN"
        
        detections = [
            Detection(
                class_id=d["class_id"],
                class_name=d["class_name"],
                confidence=round(d["confidence"], 3),
                bbox=[round(x, 2) for x in d["bbox"]]
            )
            for d in detections_data
        ]
        
        logger.info(f"Detection result: {status}, confidence={max_confidence:.3f}, detections={len(detections)}")
        
        return DetectionResponse(
            status=status,
            is_dirty=is_dirty,
            max_confidence=round(max_confidence, 3),
            detections=detections
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))  # HuggingFace uses 7860
    uvicorn.run(app, host="0.0.0.0", port=port)
