from fastapi import APIRouter
from datetime import datetime, timezone
from app.core.config import settings

router = APIRouter(tags=["Salud"])

@router.get("/health", summary="Chequeo de salud del servicio")
async def health_check():
    """Retorna el estado operativo, versión y timestamp UTC del backend."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
