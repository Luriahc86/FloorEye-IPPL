"""Health check route."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "backend"}
