from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import numpy as np
from ultralytics import YOLO

app = FastAPI()

# Load model (CPU only)
model = YOLO("models/best.pt")
model.to("cpu")

@app.get("/")
def root():
    return {"status": "ml_service running"}

@app.post("/detect/frame")
async def detect_frame(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        img = cv2.imdecode(
            np.frombuffer(img_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        if img is None:
            raise HTTPException(400, "Invalid image")

        results = model(img)
        return results[0].tojson()

    except Exception as e:
        raise HTTPException(500, str(e))
