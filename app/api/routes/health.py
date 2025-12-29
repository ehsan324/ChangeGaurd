from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Check liveness/readniess and its dependencies
    """
    return {"status": "ok",
            "service": "ChangeGaurd",
            "env": settings.app_env}