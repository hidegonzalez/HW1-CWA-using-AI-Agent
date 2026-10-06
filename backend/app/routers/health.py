from fastapi import APIRouter
from ..services.temperature_service import get_latest

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    try:
        stations, status, latest_time = await get_latest()
        return {
            "status": "ok",
            "cwa_cache_status": status,
            "latest_cwa_time": latest_time
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
