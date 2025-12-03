from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading

from routes.email_routes import router as email_router
from routes.detection_routes import router as detect_router
from services.monitor_service import monitor_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = threading.Event()
    t = threading.Thread(target=monitor_loop, args=(stop,), daemon=True)
    t.start()
    yield
    stop.set()
    t.join()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router, prefix="/email-recipients")
app.include_router(detect_router, prefix="/detect")

@app.get("/")
def root():
    return {"msg": "FloorEye Backend OK 🚀"}
