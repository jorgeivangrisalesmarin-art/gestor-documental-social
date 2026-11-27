"""Registro de proveedores por tipo documental (ADR-0003).

Sin PLACAPI_API_KEY => fixtures (E8). Cambiar de proveedor es tocar solo aquí.
"""

from app.config import get_settings
from app.providers.base import DocumentType, ProviderHealth
from app.providers.fixtures import FixtureProvider
from app.providers.placapi.adapters import (
    PlacApiEpsProvider,
    PlacApiRuiProvider,
    PlacApiSisbenProvider,
)

_PLACAPI = {
    DocumentType.ADRES_AFFILIATION_REPORT: PlacApiEpsProvider,
    DocumentType.SISBEN_IV_CERTIFICATE: PlacApiSisbenProvider,
    DocumentType.RUI_CERTIFICATE: PlacApiRuiProvider,
}


def build_providers() -> dict[DocumentType, object]:
    """Instancia el proveedor activo por tipo documental según configuración."""
    settings = get_settings()
    providers: dict[DocumentType, object] = {}
    for dtype, cls in _PLACAPI.items():
        if settings.providers_live:
            providers[dtype] = cls()
        else:
            providers[dtype] = FixtureProvider(dtype)
    return providers


async def providers_health() -> list[ProviderHealth]:
    providers = build_providers()
    return [await p.health_check() for p in providers.values()]  # type: ignore[attr-defined]
