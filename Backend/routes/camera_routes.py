from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from store.db import get_connection

router = APIRouter()

class CameraCreate(BaseModel):
    nama: str
    lokasi: Optional[str] = ""
    link: str
    aktif: Optional[bool] = True

@router.get("/")
def list_cameras():
    """List all cameras."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cameras ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@router.post("/")
def create_camera(payload: CameraCreate):
    """Create a new camera."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cameras (nama, lokasi, link, aktif) VALUES (%s, %s, %s, %s)",
        (payload.nama, payload.lokasi, payload.link, int(payload.aktif)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, "message": "Camera created"}

@router.delete("/{cam_id}")
def delete_camera(cam_id: int):
    """Delete a camera."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cameras WHERE id = %s", (cam_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Camera deleted"}

@router.patch("/{cam_id}")
def update_camera(cam_id: int, body: dict):
    """Update camera status or fields."""
    if not body:
        raise HTTPException(400, "No fields to update")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if "aktif" in body:
        cursor.execute(
            "UPDATE cameras SET aktif = %s WHERE id = %s",
            (int(body["aktif"]), cam_id),
        )
    if "nama" in body:
        cursor.execute(
            "UPDATE cameras SET nama = %s WHERE id = %s",
            (body["nama"], cam_id),
        )
    if "link" in body:
        cursor.execute(
            "UPDATE cameras SET link = %s WHERE id = %s",
            (body["link"], cam_id),
        )
    if "lokasi" in body:
        cursor.execute(
            "UPDATE cameras SET lokasi = %s WHERE id = %s",
            (body["lokasi"], cam_id),
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Camera updated"}
