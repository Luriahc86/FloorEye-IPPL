from fastapi import APIRouter
from app.store.database import test_connection
from app.utils.config import ENABLE_DB

router = APIRouter()


@router.get("/db-test")
def db_test():
    if not ENABLE_DB:
        return {
            "status": "disabled",
            "message": "Database not configured"
        }

    ok = test_connection()

    return {
        "status": "connected" if ok else "failed",
        "db_enabled": ENABLE_DB
    }
