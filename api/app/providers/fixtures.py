"""Adaptadores fixture (E8): respuestas FICTICIAS, etiquetadas como tales.

Se usan cuando no hay credencial del proveedor. Nunca deben presentarse
como consultas reales: source="fixture" y marcador FICTICIO en los datos.
"""

from typing import Any

from app.providers.base import (
    DocumentType,
    LookupInput,
    LookupResult,
    ProviderHealth,
    ResultStatus,
)

_FICTICIO = "FICTICIO — dato de prueba, NO es una consulta real"


def _fixture_data(document_type: DocumentType, input: LookupInput) -> dict[str, Any]:
    base: dict[str, Any] = {
        "advertencia": _FICTICIO,
        "tipo_documento": input.tipo_documento,
        "numero_documento": (
            f"***{input.numero_documento[-3:]}" if input.numero_documento else "***"
        ),
    }
    if document_type == DocumentType.ADRES_AFFILIATION_REPORT:
        base.update(
            {
                "nombre": "FICTICIO",
                "eps": "EPS-FICTICIA",
                "regimen": "contributivo",
                "estado_afiliacion": "activo",
                "tipo_afiliado": "cotizante",
                "fecha_afiliacion": "2020-01-01",
            }
        )
    elif document_type == DocumentType.SISBEN_IV_CERTIFICATE:
        base.update(
            {
                "grupo": "C",
                "subgrupo": "C3",
                "municipio": "Andes",
                "departamento": "Antioquia",
            }
        )
    elif document_type == DocumentType.RUI_CERTIFICATE:
        base.update(
            {
                "clasificacion_rui": "grupo-2",
                "informacion_hogar": {"integrantes": 4},
            }
        )
    return base


class FixtureProvider:
    """Proveedor de prueba: siempre responde datos ficticios etiquetados."""

    live = False

    def __init__(self, document_type: DocumentType, name: str = "fixture") -> None:
        self.document_type = document_type
        self.name = name

    async def lookup(self, input: LookupInput) -> LookupResult:
        if input.document_type != self.document_type:
            raise ValueError("Tipo documental no coincide con el proveedor")
        # Convención de prueba: documento terminado en 0 => no encontrado
        if input.numero_documento.strip().endswith("0"):
            return LookupResult(
                document_type=self.document_type,
                status=ResultStatus.NOT_FOUND,
                data={"advertencia": _FICTICIO},
                source="fixture",
            )
        return LookupResult(
            document_type=self.document_type,
            status=ResultStatus.DATA_RETRIEVED,
            data=_fixture_data(self.document_type, input),
            source="fixture",
        )

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name, document_type=self.document_type, ok=True, detail="fixture activo"
        )
