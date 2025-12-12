from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from store.db import get_connection

router = APIRouter()


# =========================
# Schemas
# =========================
class CameraCreate(BaseModel):
    nama: str
    lokasi: Optional[str] = ""
    link: str
    aktif: Optional[bool] = True


# =========================
# Routes
# =========================
@router.get("/")
def list_cameras():
    """List all cameras."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cameras ORDER BY id DESC")
        data = cursor.fetchall()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def create_camera(payload: CameraCreate):
    """Create a new camera."""
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{cam_id}")
def delete_camera(cam_id: int):
    """Delete a camera."""
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.patch("/{cam_id}")
def update_camera(cam_id: int, body: Dict[str, Any]):
    """Update camera fields."""
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
