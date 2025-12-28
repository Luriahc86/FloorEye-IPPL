from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
from app.utils.config import YOLO_SERVICE_URL

router = APIRouter()  

@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):
    try:
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

        data = res.json()
        detections = data.get("detections", [])
        count = data.get("count", 0)

        max_conf = max(
            (d.get("confidence", 0.0) for d in detections),
            default=0.0,
        )

        return {
            "is_dirty": count > 0,
            "confidence": round(max_conf, 3),
            "count": count,
            "detections": detections,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
