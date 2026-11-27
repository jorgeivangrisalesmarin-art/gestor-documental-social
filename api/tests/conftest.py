"""Fixtures de pruebas: entorno aislado con sqlite de archivo y claves reales de test.

El entorno se configura ANTES de importar la app (config se lee en import).
"""

import os
import pathlib

_TEST_DB = pathlib.Path(__file__).parent / "gds_test.db"

os.environ.update(
    {
        "APP_ENV": "test",
        "DATABASE_URL": f"sqlite+aiosqlite:///{_TEST_DB}",
        "JWT_SECRET": "test-secret",
        # fernet key de prueba (solo tests)
        "DOC_ENCRYPTION_KEY": "pQPDG8yl5HHN9NB4jNBH3t_4xqCJ571o03UYv1BN5fQ=",
        "DOC_HMAC_KEY": "test-hmac-key",
        "SEED_ADMIN_EMAIL": "admin@test.local",
        "SEED_ADMIN_PASSWORD": "test-admin-1234",
        "PLACAPI_API_KEY": "",  # => fixtures (E8)
        "DOCUMENT_STORAGE_PATH": str(pathlib.Path(__file__).parent / "test_docs"),
    }
)

if _TEST_DB.exists():
    _TEST_DB.unlink()

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app as fastapi_app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token(client: TestClient) -> str:
    resp = client.post(
        "/auth/login",
        json={"email": "admin@test.local", "password": "test-admin-1234"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
