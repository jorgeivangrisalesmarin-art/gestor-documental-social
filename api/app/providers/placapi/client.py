"""Cliente HTTP compartido de PlacApi (x-api-key, servidor a servidor).

PlacApi no habilita CORS: solo puede llamarse desde backend (docs oficiales).
Contratos pendientes de confirmar con los resultados del sondeo T001.
"""

from typing import Any

import httpx

from app.config import get_settings
from app.providers.base import (
    ProviderError,
    ProviderNotFound,
    ProviderPaymentRequired,
    ProviderRateLimited,
    ProviderServerError,
    ProviderUnauthorized,
    with_retries,
)

_TIMEOUT = httpx.Timeout(15.0)


def _map_status(status_code: int, body: str) -> ProviderError:
    if status_code in (401, 403):
        return ProviderUnauthorized(f"PlacApi auth {status_code}")
    if status_code == 402:
        return ProviderPaymentRequired("PlacApi sin créditos")
    if status_code == 404:
        return ProviderNotFound("PlacApi no encontrado")
    if status_code == 429:
        return ProviderRateLimited("PlacApi rate limit")
    return ProviderServerError(f"PlacApi error {status_code}: {body[:200]}")


class PlacApiError(ProviderError):
    code = "PLACAPI_ERROR"


async def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST a PlacApi con reintentos 429/5xx (E7) y errores tipados (E6)."""
    settings = get_settings()
    url = f"{settings.placapi_base_url.rstrip('/')}/{path.lstrip('/')}"

    async def _once() -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"x-api-key": settings.placapi_api_key},
            )
        if resp.status_code >= 400:
            raise _map_status(resp.status_code, resp.text)
        return resp.json()

    try:
        return await with_retries(_once)
    except httpx.TimeoutException as e:
        raise ProviderServerError(f"PlacApi timeout: {e}") from e
    except httpx.HTTPError as e:
        raise ProviderServerError(f"PlacApi error de red: {e}") from e
