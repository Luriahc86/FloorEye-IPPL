import os
import requests
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter()

HF_URL = os.getenv("HF_URL")

# =========================
# Detection Proxy Endpoint
# =========================
@router.post("/frame")
async def detect_frame(file: UploadFile = File(...)):
    # 🔒 Validasi config
    if not HF_URL:
        logger.error("HF_URL not configured")
        raise HTTPException(
            status_code=500,
            detail="ML service URL not configured"
        )

    try:
        # Baca file SEKALI
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty image"
            )

        # Kirim ke Hugging Face
        res = requests.post(
            HF_URL,
            files={"file": file_bytes},
            timeout=60
        )

        # ⛔ HF error → teruskan apa adanya
        if res.status_code != 200:
            logger.error(
                f"HF ERROR {res.status_code}: {res.text}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"HF ERROR {res.status_code}: {res.text}"
            )

        # ✅ Aman: return JSON HF
        try:
            return res.json()
        except Exception:
            # HF balikin non-JSON
            return {
                "raw": res.text
            }

    except HTTPException:
        raise
    except requests.exceptions.Timeout:
        logger.exception("HF request timeout")
        raise HTTPException(
            status_code=504,
            detail="ML service timeout"
        )
    except requests.exceptions.ConnectionError:
        logger.exception("HF connection error")
        raise HTTPException(
            status_code=503,
            detail="ML service unavailable"
        )
    except Exception as e:
        logger.exception("Detection proxy failed")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
