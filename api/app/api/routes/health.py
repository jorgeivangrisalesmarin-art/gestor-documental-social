"""Health checks (E18): estado de la app y de los proveedores, sin secretos."""

from fastapi import APIRouter

from app.config import get_settings
from app.providers import providers_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": get_settings().app_env}


@router.get("/health/providers")
async def health_providers() -> dict:
    checks = await providers_health()
    return {
        "providers": [
            {
                "provider": h.provider,
                "document_type": h.document_type.value if h.document_type else None,
                "ok": h.ok,
                "detail": h.detail,
            }
            for h in checks
        ]
    }
