import requests
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
import logging

from app.utils.config import YOLO_SERVICE_URL

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):
    if not YOLO_SERVICE_URL:
        raise HTTPException(
            status_code=500,
            detail="YOLO_SERVICE_URL not configured"
        )

    try:
        # Read image & encode to base64
        image_bytes = await file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # Send JSON to HF (NOT multipart)
        res = requests.post(
            YOLO_SERVICE_URL,
            json={
                "image": image_b64
            },
            timeout=60,
        )

        if res.status_code != 200:
            logger.error(f"HF ERROR {res.status_code}: {res.text}")
            raise HTTPException(
                status_code=500,
                detail=f"HF ERROR {res.status_code}"
            )

        return res.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"HF request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reach ML service"
        )
