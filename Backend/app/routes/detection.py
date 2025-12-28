import requests
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
        # Forward file ke HuggingFace (multipart)
        res = requests.post(
            YOLO_SERVICE_URL,
            files={
                "file": (
                    file.filename,
                    await file.read(),
                    file.content_type or "image/jpeg",
                )
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
