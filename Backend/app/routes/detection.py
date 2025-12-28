from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
from app.utils.config import YOLO_SERVICE_URL

router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):
    
    try:
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
            raise HTTPException(
                status_code=502,
                detail=f"HF ERROR {res.status_code}: {res.text}",
            )

        data = res.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to reach ML service: {e}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    detections = data.get("detections", [])
    count = data.get("count", 0)

    max_conf = 0.0
    for d in detections:
        max_conf = max(max_conf, d.get("confidence", 0.0))

    is_dirty = count > 0

    return {
        "is_dirty": is_dirty,
        "confidence": round(max_conf, 3),
        "count": count,
        "detections": detections,
    }