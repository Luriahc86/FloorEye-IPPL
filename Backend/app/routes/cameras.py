"""Camera management routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.store.db import get_connection
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)
router = APIRouter()


class CameraCreate(BaseModel):
    nama: str
    lokasi: Optional[str] = ""
    link: str
    aktif: Optional[bool] = True


@router.get("/")
def list_cameras():
    """List all cameras."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cameras ORDER BY id DESC")
        data = cursor.fetchall()
        return data
    except Exception as e:
        logger.error(f"list_cameras error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def create_camera(payload: CameraCreate):
    """Create a new camera."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cameras (nama, lokasi, link, aktif)
            VALUES (%s, %s, %s, %s)
            """,
            (payload.nama, payload.lokasi, payload.link, int(payload.aktif)),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "message": "Camera created"
        }
    except Exception as e:
        logger.error(f"create_camera error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{cam_id}")
def delete_camera(cam_id: int):
    """Delete a camera."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cameras WHERE id = %s", (cam_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Camera not found")

        return {"message": "Camera deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_camera error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.patch("/{cam_id}")
def update_camera(cam_id: int, body: Dict[str, Any]):
    """Update camera fields."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    if not body:
        raise HTTPException(status_code=400, detail="No fields to update")

    allowed_fields = {"aktif", "nama", "link", "lokasi"}
    invalid_fields = set(body.keys()) - allowed_fields
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields: {', '.join(invalid_fields)}"
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for field, value in body.items():
            cursor.execute(
                f"UPDATE cameras SET {field} = %s WHERE id = %s",
                (int(value) if field == "aktif" else value, cam_id),
            )

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Camera not found")

        return {"message": "Camera updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"update_camera error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
