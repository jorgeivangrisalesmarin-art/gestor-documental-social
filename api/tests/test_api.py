"""Pruebas de integración de la API: E1–E5, E8, E13–E16, E18."""

CSV_VALIDO = (
    "tipo_documento,numero_documento,adres,sisben_iv,rui,autorizacion_confirmada,referencia_autorizacion\n"
    "CC,123456789,true,false,false,true,oficio-001\n"
    "CC,222222222,true,true,false,true,oficio-002\n"
    "CC,111110,true,false,false,true,oficio-003\n"  # fixture: termina en 0 => NOT_FOUND
)

CSV_SIN_AUTORIZACION = (
    "tipo_documento,numero_documento,adres,sisben_iv,rui,autorizacion_confirmada,referencia_autorizacion\n"
    "CC,999888777,true,false,false,false,\n"
    "CC,123456789,true,false,false,true,oficio-010\n"
)

CSV_COLUMNAS_MALAS = "cedula,nombre\nCC,123\n"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_providers_fixture_mode(client):
    resp = client.get("/health/providers")
    assert resp.status_code == 200
    tipos = {p["document_type"] for p in resp.json()["providers"]}
    assert len(tipos) == 3  # los tres tipos documentales cubiertos


def test_login_credenciales_invalidas(client):
    resp = client.post(
        "/auth/login", json={"email": "admin@test.local", "password": "incorrecta-1"}
    )
    assert resp.status_code == 401


def test_me_sin_token_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_con_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_lookup_sin_autorizacion_422(client, auth_headers):
    """E5: la consulta exige autorizacion_confirmada=true y finalidad."""
    resp = client.post(
        "/api/v1/lookups",
        json={
            "tipo_documento": "CC",
            "numero_documento": "123456789",
            "document_types": ["ADRES_AFFILIATION_REPORT"],
            "finalidad": "atención al ciudadano",
            "autorizacion_confirmada": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_lookup_fixture_completo(client, auth_headers):
    """E5+E8: consulta exitosa en modo fixture marcada como ficticia."""
    resp = client.post(
        "/api/v1/lookups",
        json={
            "tipo_documento": "CC",
            "numero_documento": "123456789",
            "document_types": ["ADRES_AFFILIATION_REPORT", "SISBEN_IV_CERTIFICATE"],
            "finalidad": "atención al ciudadano en ventanilla",
            "autorizacion_confirmada": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    jobs = resp.json()
    assert len(jobs) == 2
    assert {j["document_type"] for j in jobs} == {
        "ADRES_AFFILIATION_REPORT",
        "SISBEN_IV_CERTIFICATE",
    }
    for job in jobs:
        assert job["status"] == "COMPLETED"
        assert job["source"] == "fixture"
        assert job["result"]["live"] is False
        assert "FICTICIO" in job["result"]["data"]["advertencia"]


def test_lookup_documento_no_encontrado(client, auth_headers):
    """E5: NOT_FOUND como estado, no como error 500."""
    resp = client.post(
        "/api/v1/lookups",
        json={
            "tipo_documento": "CC",
            "numero_documento": "777770",
            "document_types": ["RUI_CERTIFICATE"],
            "finalidad": "atención al ciudadano en ventanilla",
            "autorizacion_confirmada": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()[0]["status"] == "NOT_FOUND"


def test_lookup_tipo_documental_invalido(client, auth_headers):
    resp = client.post(
        "/api/v1/lookups",
        json={
            "tipo_documento": "CC",
            "numero_documento": "123456789",
            "document_types": ["SISBEN_PUNTAJE"],  # no existe
            "finalidad": "atención al ciudadano",
            "autorizacion_confirmada": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_batch_flujo_completo(client, auth_headers):
    """E13–E16: carga, validación, procesamiento y estados por documento."""
    upload = client.post(
        "/api/v1/batches",
        files={"file": ("lote.csv", CSV_VALIDO.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert upload.status_code == 201, upload.text
    batch = upload.json()
    assert batch["validation_errors"] == []
    assert batch["total_records"] == 3

    proc = client.post(f"/api/v1/batches/{batch['id']}/process", headers=auth_headers)
    assert proc.status_code == 200, proc.text
    resultado = proc.json()
    assert resultado["status"] in ("COMPLETED", "PARTIAL_SUCCESS")
    # 3 filas => 4 jobs documentales (la fila 2 pide adres + sisben_iv)
    assert resultado["processed_records"] == 4
    estados = {j["status"] for j in resultado["jobs"]}
    assert "COMPLETED" in estados
    assert "NOT_FOUND" in estados  # el que termina en 0

    status = client.get(f"/api/v1/batches/{batch['id']}", headers=auth_headers)
    assert status.status_code == 200
    assert status.json()["processed_records"] == 4


def test_batch_sin_autorizacion_se_excluye(client, auth_headers):
    """E15: registro sin autorización se excluye con motivo, no se procesa."""
    upload = client.post(
        "/api/v1/batches",
        files={"file": ("lote2.csv", CSV_SIN_AUTORIZACION.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert upload.status_code == 201, upload.text
    batch = upload.json()
    excluidos = [j for j in batch["jobs"] if j["status"] == "EXCLUDED"]
    assert len(excluidos) == 1
    assert excluidos[0]["error_code"] == "SIN_AUTORIZACION"
    assert batch["total_records"] == 2


def test_batch_columnas_invalidas_422(client, auth_headers):
    """E13: faltan columnas mínimas => 422 con mensaje claro."""
    upload = client.post(
        "/api/v1/batches",
        files={"file": ("mal.csv", CSV_COLUMNAS_MALAS.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert upload.status_code == 422
    assert "columnas obligatorias" in upload.json()["detail"]


def test_batch_reproceso_409(client, auth_headers):
    upload = client.post(
        "/api/v1/batches",
        files={"file": ("lote3.csv", CSV_VALIDO.encode(), "text/csv")},
        headers=auth_headers,
    )
    batch_id = upload.json()["id"]
    client.post(f"/api/v1/batches/{batch_id}/process", headers=auth_headers)
    resp = client.post(f"/api/v1/batches/{batch_id}/process", headers=auth_headers)
    assert resp.status_code == 409
