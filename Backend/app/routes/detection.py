import logging
import requests
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.utils.config import YOLO_SERVICE_URL

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):

    if not YOLO_SERVICE_URL:
        raise HTTPException(
            status_code=500,
            detail="YOLO_SERVICE_URL not configured"
        )

    try:
        # Read uploaded image
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file")

        # Send to HF ML service
        response = requests.post(
            YOLO_SERVICE_URL,
            files={
                "file": (
                    file.filename or "frame.jpg",
                    image_bytes,
                    file.content_type or "image/jpeg",
                )
            },
            timeout=30,
        )

        # Handle HF error explicitly
        if response.status_code != 200:
            logger.error(
                f"HF ERROR {response.status_code}: {response.text}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"HF ERROR {response.status_code}"
            )

        # Parse HF response
        data = response.json()

        detections = data.get("detections", [])
        count = data.get("count", 0)

        # Get max confidence
        max_confidence = 0.0
        for det in detections:
            max_confidence = max(
                max_confidence,
                float(det.get("confidence", 0.0))
            )

        # Business logic
        is_dirty = count > 0

        # Final response (Frontend-compatible)
        return {
            "is_dirty": is_dirty,
            "confidence": round(max_confidence, 3),
            "count": count,
        }

    except HTTPException:
        raise

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to reach ML service: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reach ML service"
        )

    except Exception as e:
        logger.exception("Detection failed")
        raise HTTPException(
            status_code=500,
            detail="Detection failed"
        )
