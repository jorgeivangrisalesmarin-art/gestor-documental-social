"""Pruebas del contrato de proveedores: fixtures (E8), reintentos y errores (E6, E7)."""

import pytest

from app.providers.base import (
    DocumentType,
    LookupInput,
    ProviderRateLimited,
    ProviderUnauthorized,
    with_retries,
)
from app.providers.fixtures import FixtureProvider
from app.providers.placapi.adapters import (
    PlacApiEpsProvider,
    PlacApiRuiProvider,
    PlacApiSisbenProvider,
)


@pytest.fixture
def eps_fixture():
    return FixtureProvider(DocumentType.ADRES_AFFILIATION_REPORT)


async def test_fixture_encuentra_persona(eps_fixture):
    result = await eps_fixture.lookup(
        LookupInput(DocumentType.ADRES_AFFILIATION_REPORT, "CC", "123456789")
    )
    assert result.status.value == "DATA_RETRIEVED"
    assert result.source == "fixture"
    assert "FICTICIO" in result.data["advertencia"]


async def test_fixture_no_encontrado_termina_en_0(eps_fixture):
    result = await eps_fixture.lookup(
        LookupInput(DocumentType.ADRES_AFFILIATION_REPORT, "CC", "111110")
    )
    assert result.status.value == "NOT_FOUND"


async def test_fixture_sisben_y_rui():
    s = FixtureProvider(DocumentType.SISBEN_IV_CERTIFICATE)
    r = FixtureProvider(DocumentType.RUI_CERTIFICATE)
    rs = await s.lookup(LookupInput(DocumentType.SISBEN_IV_CERTIFICATE, "CC", "123456789"))
    rr = await r.lookup(LookupInput(DocumentType.RUI_CERTIFICATE, "CC", "123456789"))
    assert rs.data["grupo"] == "C"
    assert "clasificacion_rui" in rr.data


def test_tipos_documentales_separados():
    """Los tres tipos existen como valores independientes (regla del brief §3)."""
    assert {t.value for t in DocumentType} == {
        "ADRES_AFFILIATION_REPORT",
        "SISBEN_IV_CERTIFICATE",
        "RUI_CERTIFICATE",
    }


async def test_reintento_en_rate_limit_luego_exito():
    llamadas = {"n": 0}

    async def flaky():
        llamadas["n"] += 1
        if llamadas["n"] < 2:
            raise ProviderRateLimited("429")
        return "ok"

    assert await with_retries(flaky, max_retries=2, backoff_seconds=0.01) == "ok"
    assert llamadas["n"] == 2


async def test_sin_reintento_en_401():
    llamadas = {"n": 0}

    async def unauthorized():
        llamadas["n"] += 1
        raise ProviderUnauthorized("401")

    with pytest.raises(ProviderUnauthorized):
        await with_retries(unauthorized, max_retries=2, backoff_seconds=0.01)
    assert llamadas["n"] == 1  # E6: sin reintento


def test_placapi_adapters_paths_verificados():
    """Endpoints verificados en docs vivas 2026-11-26: eps, sisben, rui separados."""
    assert PlacApiEpsProvider().path == "eps"
    assert PlacApiSisbenProvider().path == "sisben"
    assert PlacApiRuiProvider().path == "rui"
