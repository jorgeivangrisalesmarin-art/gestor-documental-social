"""Contrato DocumentProvider (ADR-0003) — el dominio solo ve este módulo.

Reglas de dependencia: los adaptadores transforman su respuesta cruda a
LookupResult; services NUNCA importan httpx ni modelos de proveedores.
"""

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol


class DocumentType(StrEnum):
    ADRES_AFFILIATION_REPORT = "ADRES_AFFILIATION_REPORT"
    SISBEN_IV_CERTIFICATE = "SISBEN_IV_CERTIFICATE"
    RUI_CERTIFICATE = "RUI_CERTIFICATE"


class ResultStatus(StrEnum):
    DATA_RETRIEVED = "DATA_RETRIEVED"
    NOT_FOUND = "NOT_FOUND"
    DOCUMENT_PENDING = "DOCUMENT_PENDING"
    MANUAL_ACTION_REQUIRED = "MANUAL_ACTION_REQUIRED"


@dataclass(frozen=True)
class LookupInput:
    document_type: DocumentType
    tipo_documento: str
    numero_documento: str


@dataclass
class LookupResult:
    document_type: DocumentType
    status: ResultStatus
    data: dict[str, Any]
    source: str
    consulted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ProviderHealth:
    provider: str
    document_type: DocumentType | None
    ok: bool
    detail: str


# ------------------------------------------------------------------ errores


class ProviderError(Exception):
    """Base de errores de proveedor, mapea 1:1 con códigos HTTP observados."""

    code = "PROVIDER_ERROR"


class ProviderUnauthorized(ProviderError):
    code = "PROVIDER_UNAUTHORIZED"  # 401/403 — no reintentar


class ProviderPaymentRequired(ProviderError):
    code = "PROVIDER_PAYMENT_REQUIRED"  # 402 — sin créditos, no reintentar


class ProviderNotFound(ProviderError):
    code = "PROVIDER_NOT_FOUND"  # 404 — persona/documento no encontrado


class ProviderRateLimited(ProviderError):
    code = "PROVIDER_RATE_LIMITED"  # 429 — reintentable


class ProviderServerError(ProviderError):
    code = "PROVIDER_SERVER_ERROR"  # 5xx — reintentable


class DocumentProvider(Protocol):
    name: str
    document_type: DocumentType
    live: bool  # False => fixture (respuesta ficticia, E8)

    async def lookup(self, input: LookupInput) -> LookupResult: ...

    async def health_check(self) -> ProviderHealth: ...


async def with_retries(
    fn: Callable[[], Awaitable[Any]],
    max_retries: int = 2,
    backoff_seconds: float = 1.0,
) -> Any:
    """Reintenta solo errores reintentables (429/5xx) con backoff (E7)."""
    attempts = 0
    while True:
        try:
            return await fn()
        except (ProviderRateLimited, ProviderServerError):
            attempts += 1
            if attempts > max_retries:
                raise
            delay = backoff_seconds * (2 ** (attempts - 1))
            last = time.monotonic() + delay
            while time.monotonic() < last:
                await _sleep_until(last)
        # 401/402/404 u otros: sin reintento (E6)


async def _sleep_until(until: float) -> None:
    import asyncio

    await asyncio.sleep(max(0.0, until - time.monotonic()))
