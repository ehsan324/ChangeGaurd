from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Check liveness/readniess and its dependencies
    """
    settings = get_settings()
    return {"status": "ok",
            "service": "ChangeGaurd",
            "env": settings.app_env}