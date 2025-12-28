from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
from app.utils.config import YOLO_SERVICE_URL

router = APIRouter()

@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):
    try:
        # ⬅️ FORWARD FILE LANGSUNG KE HF
        res = requests.post(
            YOLO_SERVICE_URL,
            files={
                "file": (
                    file.filename,
                    await file.read(),
                    file.content_type,
                )
            },
            timeout=60,
        )

        if res.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"HF ERROR {res.status_code}: {res.text}",
            )

        return res.json()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
