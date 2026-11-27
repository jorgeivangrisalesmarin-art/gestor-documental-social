"""Adaptadores PlacApi: POST /api/eps, /api/sisben, /api/rui (endpoints verificados
en la documentación viva 2026-11-26; contratos finales a confirmar con T001).

Cada adaptador normaliza la respuesta cruda a LookupResult del dominio (ADR-0003).
"""

from typing import Any

from app.providers.base import (
    DocumentType,
    LookupInput,
    LookupResult,
    ProviderHealth,
    ResultStatus,
)
from app.providers.placapi.client import post_json


class _PlacApiProvider:
    """Base común de los adaptadores PlacApi."""

    live = True
    path: str = ""
    label: str = "placapi"

    def __init__(self, document_type: DocumentType) -> None:
        self.document_type = document_type

    async def lookup(self, input: LookupInput) -> LookupResult:
        if input.document_type != self.document_type:
            raise ValueError("Tipo documental no coincide con el proveedor")
        raw = await post_json(
            self.path,
            {"tipo_documento": input.tipo_documento, "numero_documento": input.numero_documento},
        )
        return self._normalize(raw)

    def _normalize(self, raw: dict[str, Any]) -> LookupResult:
        found = bool(raw.get("encontrado", raw.get("found", True)))
        data = {
            "advertencia": "Datos de proveedor privado; NO es un documento oficial.",
            "respuesta": raw,
        }
        if not found:
            status = ResultStatus.NOT_FOUND
        else:
            # Ninguno de los tres endpoints entrega PDF oficial hoy: DOCUMENT_PENDING (E9)
            status = ResultStatus.DOCUMENT_PENDING
        return LookupResult(
            document_type=self.document_type, status=status, data=data, source=self.label
        )

    async def health_check(self) -> ProviderHealth:
        # Health pasivo: no gastamos créditos con consultas; validamos presencia de key.
        ok = bool(get_api_key())
        return ProviderHealth(
            provider=self.label,
            document_type=self.document_type,
            ok=ok,
            detail="credencial configurada" if ok else "sin PLACAPI_API_KEY (usar fixtures)",
        )


def get_api_key() -> str:
    from app.config import get_settings

    return get_settings().placapi_api_key


class PlacApiEpsProvider(_PlacApiProvider):
    """ADRES / BDUA — POST /api/eps."""

    path = "eps"
    label = "placapi-eps"

    def __init__(self) -> None:
        super().__init__(DocumentType.ADRES_AFFILIATION_REPORT)


class PlacApiSisbenProvider(_PlacApiProvider):
    """SISBÉN IV (Ventanilla Social DNP) — POST /api/sisben."""

    path = "sisben"
    label = "placapi-sisben"

    def __init__(self) -> None:
        super().__init__(DocumentType.SISBEN_IV_CERTIFICATE)


class PlacApiRuiProvider(_PlacApiProvider):
    """RUI (Ventanilla Social DNP) — POST /api/rui."""

    path = "rui"
    label = "placapi-rui"

    def __init__(self) -> None:
        super().__init__(DocumentType.RUI_CERTIFICATE)
