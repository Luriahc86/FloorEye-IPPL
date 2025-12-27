from dotenv import load_dotenv
load_dotenv()  # Load .env file BEFORE other imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.detection_routes import router as detect_router
from routes.history_routes import router as history_router
from routes.email_routes import router as email_router

app = FastAPI(title="FloorEye Live Camera Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect_router, prefix="/detect", tags=["Detection"])

app.include_router(history_router, prefix="/history", tags=["History"])

app.include_router(email_router, prefix="/email-recipients", tags=["Email"])

@app.get("/")
def root():
    return {"msg": "FloorEye Backend OK ", "mode": "live-camera"}

@app.get("/health")
def health():
    return {"status": "healthy"}
