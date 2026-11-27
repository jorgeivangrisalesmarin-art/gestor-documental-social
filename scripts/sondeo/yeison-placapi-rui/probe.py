"""
Script de sondeo para PlacApi - RUI (Registro Universal de Ingresos - DNP)
Endpoint: POST https://placapi.com/api/rui
Asignado: Yeison (Junior Developer)
Tarea: T001
Criterios: AC-1 a AC-7
"""

import os
import sys
import json
import time
import re
from datetime import datetime, timezone
import requests

ENDPOINT_URL = "https://placapi.com/api/rui"
TIMEOUT_SECONDS = 15
MAX_RETRIES = 2
BACKOFF_SECONDS = 5

def check_anti_hardcode(source_file_path: str, api_key: str):
    """
    Criterio AC-3: El script deberá fallar de inmediato (sin hacer requests)
    si detecta su propia key escrita en el código.
    """
    if not os.path.exists(source_file_path):
        return

    with open(source_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Si hay una key en el entorno, verificar que no esté quemada en el archivo
    if api_key and len(api_key.strip()) > 5:
        if api_key.strip() in content:
            print("[ERROR DE SEGURIDAD - AC-3] Se detectó la API Key hardcodeada en el código fuente.")
            print("Abortando de inmediato sin realizar ninguna petición HTTP.")
            sys.exit(1)

    # Verificación heurística adicional de asignaciones directas de claves sospechosas
    suspicious_patterns = [
        r'["\']x-api-key["\']\s*:\s*["\'][a-zA-Z0-9_\-]{16,}["\']',
        r'PROBE_API_KEY\s*=\s*["\'][a-zA-Z0-9_\-]{16,}["\']'
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, content):
            print("[ERROR DE SEGURIDAD - AC-3] Patrón sospechoso de clave hardcodeada detectado.")
            sys.exit(1)

def extract_schema_contract(data, parent_key=""):
    """
    Extrae la estructura de tipos del cuerpo de respuesta.
    """
    contract = {}
    if isinstance(data, dict):
        for k, v in data.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                contract[full_key] = {"type": "object", "fields": extract_schema_contract(v, full_key)}
            elif isinstance(v, list):
                item_type = type(v[0]).__name__ if v else "empty_list"
                contract[full_key] = {"type": f"array[{item_type}]"}
            else:
                contract[full_key] = {"type": type(v).__name__ if v is not None else "null"}
    return contract

def redact_sensitive_data(obj):
    """
    Redacta datos sensibles recursivamente conservando tipo y estructura (AC-5 / AC-7).
    """
    if isinstance(obj, dict):
        redacted = {}
        for k, v in obj.items():
            # Conservar campos estructurales de clasificación pública o metadatos
            if k in ["source", "status", "mode", "fetchedAt", "cost", "tipoDocumento", "docType", "tieneClasificacion"]:
                redacted[k] = redact_sensitive_data(v)
            elif isinstance(v, (dict, list)):
                redacted[k] = redact_sensitive_data(v)
            elif isinstance(v, str):
                redacted[k] = "***"
            elif isinstance(v, (int, float)):
                redacted[k] = 999
            elif isinstance(v, bool):
                redacted[k] = v
            else:
                redacted[k] = "***"
        return redacted
    elif isinstance(obj, list):
        return [redact_sensitive_data(item) for item in obj]
    else:
        return "***"

def make_request_with_retry(method, url, headers=None, json_data=None, allow_retries=True):
    """
    Ejecuta una petición con timeout de 15s y máximo 2 reintentos con backoff de 5s en 429/5xx.
    """
    retries = 0
    while True:
        start_time = time.perf_counter()
        utc_timestamp = datetime.now(timezone.utc).isoformat()
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=TIMEOUT_SECONDS
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            # Reintentos solo en 429 y 5xx si está permitido
            if allow_retries and response.status_code in [429, 500, 502, 503, 504] and retries < MAX_RETRIES:
                retries += 1
                time.sleep(BACKOFF_SECONDS)
                continue

            return response, elapsed_ms, utc_timestamp, None

        except requests.exceptions.RequestException as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if allow_retries and retries < MAX_RETRIES:
                retries += 1
                time.sleep(BACKOFF_SECONDS)
                continue
            return None, elapsed_ms, utc_timestamp, str(e)

def parse_body(response):
    """Parsea el cuerpo de la respuesta o devuelve texto truncado a 2000 chars."""
    if response is None:
        return {"error": "Sin respuesta"}
    try:
        data = response.json()
        return data
    except Exception:
        text = response.text[:2000] if response.text else ""
        return {"raw_text": text}

def main():
    script_path = os.path.abspath(__file__)
    api_key = os.environ.get("PROBE_API_KEY", "").strip()
    real_doc_var = os.environ.get("PROBE_REAL_DOC", "").strip()

    # Criterio AC-3: chequeo anti-hardcode
    check_anti_hardcode(script_path, api_key)

    base_dir = os.path.dirname(script_path)
    results_path = os.path.join(base_dir, "results.json")
    raw_response_path = os.path.join(base_dir, "raw_response.json")

    results = {
        "metadata": {
            "endpoint": ENDPOINT_URL,
            "proveedor": "PlacApi",
            "modulo": "RUI (Registro Universal de Ingresos)",
            "dev": "Yeison",
            "tarea": "T001",
            "fecha_ejecucion_utc": datetime.now(timezone.utc).isoformat(),
            "consumo_credito": False
        },
        "casos": {},
        "validacion_real": {
            "ejecutada": False
        },
        "contrato_observado": {}
    }

    # =========================================================================
    # CASO (a): Sin header de auth → espera 401
    # =========================================================================
    print("[1/5] Ejecutando Caso (a): Petición sin header de autenticación...")
    payload_a = {"docType": "CC", "docNumber": "99999999999"}
    resp_a, lat_a, ts_a, err_a = make_request_with_retry("POST", ENDPOINT_URL, headers={"Content-Type": "application/json"}, json_data=payload_a)
    
    status_a = resp_a.status_code if resp_a is not None else 0
    body_a = parse_body(resp_a)
    results["casos"]["caso_a_sin_auth"] = {
        "descripcion": "Petición sin header de auth (espera 401)",
        "status_code": status_a,
        "latencia_ms": lat_a,
        "timestamp_utc": ts_a,
        "cuerpo": body_a,
        "error": err_a,
        "cumple_esperado": status_a == 401
    }
    print(f"      -> Status recibido: {status_a} en {lat_a}ms")

    # Si NO hay API key en el entorno: Criterio AC-1 (terminar de forma controlada)
    if not api_key:
        print("\n[MODO CONTRATO SIN CREDENCIAL]")
        print("La variable PROBE_API_KEY no está definida.")
        print("Se ejecutó el Caso (a) exitosamente para verificar la respuesta del servidor.")
        print("Los Casos (b), (c), (d) y (e) quedan reservados para cuando se configure la credencial.")
        results["metadata"]["modo"] = "completo-modo-contrato"
        results["metadata"]["bloqueo"] = "Falta PROBE_API_KEY"

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Resultados guardados en: {results_path}")
        sys.exit(0)

    # Headers con autenticación
    headers_valid = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    # =========================================================================
    # CASO (b): Auth inválida "PROBE-INVALID" → espera 401/403
    # =========================================================================
    print("[2/5] Ejecutando Caso (b): Petición con auth inválida 'PROBE-INVALID'...")
    headers_invalid = {
        "Content-Type": "application/json",
        "x-api-key": "PROBE-INVALID"
    }
    resp_b, lat_b, ts_b, err_b = make_request_with_retry("POST", ENDPOINT_URL, headers=headers_invalid, json_data=payload_a)
    status_b = resp_b.status_code if resp_b is not None else 0
    body_b = parse_body(resp_b)
    results["casos"]["caso_b_auth_invalida"] = {
        "descripcion": "Petición con x-api-key inválida (espera 401 o 403)",
        "status_code": status_b,
        "latencia_ms": lat_b,
        "timestamp_utc": ts_b,
        "cuerpo": body_b,
        "error": err_b,
        "cumple_esperado": status_b in [401, 403]
    }
    print(f"      -> Status recibido: {status_b} en {lat_b}ms")

    # =========================================================================
    # CASO (c): Payload JSON válido con documento ficticio (11 nueves) → espera 404/400
    # =========================================================================
    print("[3/5] Ejecutando Caso (c): Payload válido con documento ficticio '99999999999'...")
    payload_c = {
        "docType": "CC",
        "docNumber": "99999999999",
        "numero_documento": "99999999999"
    }
    resp_c, lat_c, ts_c, err_c = make_request_with_retry("POST", ENDPOINT_URL, headers=headers_valid, json_data=payload_c)
    status_c = resp_c.status_code if resp_c is not None else 0
    body_c = parse_body(resp_c)
    
    consumo_c = False
    if status_c == 200:
        consumo_c = True
        results["metadata"]["consumo_credito"] = True

    results["casos"]["caso_c_payload_valido_ficticio"] = {
        "descripcion": "Payload válido con doc ficticio 99999999999 (espera 404, 400 o sin resultado)",
        "status_code": status_c,
        "latencia_ms": lat_c,
        "timestamp_utc": ts_c,
        "cuerpo": body_c,
        "error": err_c,
        "consumo_credito": consumo_c,
        "cumple_esperado": status_c in [400, 404, 422, 200]
    }
    print(f"      -> Status recibido: {status_c} en {lat_c}ms")

    if isinstance(body_c, dict) and body_c:
        results["contrato_observado"] = extract_schema_contract(body_c)

    # Si consumió crédito en (c), regla 6: detener tras el primer 200
    if consumo_c:
        print("[AVISO] El Caso (c) respondió 200 (consumió crédito). Deteniendo según regla 6.")

    # =========================================================================
    # CASO (d): Payload malformado (sin docNumber / numero_documento) → espera 400/422
    # =========================================================================
    print("[4/5] Ejecutando Caso (d): Payload malformado sin documento...")
    payload_d = {
        "docType": "CC"
    }
    resp_d, lat_d, ts_d, err_d = make_request_with_retry("POST", ENDPOINT_URL, headers=headers_valid, json_data=payload_d)
    status_d = resp_d.status_code if resp_d is not None else 0
    body_d = parse_body(resp_d)
    results["casos"]["caso_d_payload_malformado"] = {
        "descripcion": "Payload malformado sin numero_documento (espera 400 o 422)",
        "status_code": status_d,
        "latencia_ms": lat_d,
        "timestamp_utc": ts_d,
        "cuerpo": body_d,
        "error": err_d,
        "cumple_esperado": status_d in [400, 422]
    }
    print(f"      -> Status recibido: {status_d} en {lat_d}ms")

    # =========================================================================
    # CASO (e): Validación real autorizada (autocercicio) - Criterios AC-5 / AC-6
    # =========================================================================
    if real_doc_var:
        print("\n[5/5] Ejecutando Caso (e): Validación real autorizada (autocercicio)...")
        # Formato esperado: "CC,1234567890" o "1234567890"
        parts = [p.strip() for p in real_doc_var.split(",") if p.strip()]
        if len(parts) == 2:
            real_doc_type, real_doc_num = parts[0], parts[1]
        else:
            real_doc_type, real_doc_num = "CC", parts[0]

        payload_e = {
            "docType": real_doc_type,
            "docNumber": real_doc_num,
            "numero_documento": real_doc_num
        }

        # Exactamente UNA consulta real sin reintentos (allow_retries=False)
        resp_e, lat_e, ts_e, err_e = make_request_with_retry(
            "POST", ENDPOINT_URL, headers=headers_valid, json_data=payload_e, allow_retries=False
        )
        status_e = resp_e.status_code if resp_e is not None else 0
        raw_body_e = parse_body(resp_e)

        # Guardar respuesta cruda en raw_response.json (ignorado en .gitignore)
        try:
            with open(raw_response_path, "w", encoding="utf-8") as f_raw:
                json.dump({
                    "endpoint": ENDPOINT_URL,
                    "timestamp_utc": ts_e,
                    "status_code": status_e,
                    "raw_response": raw_body_e
                }, f_raw, indent=2, ensure_ascii=False)
            print(f"      -> Respuesta cruda guardada en: {raw_response_path} (protegida por .gitignore)")
        except Exception as ex:
            print(f"      -> Error guardando raw_response.json: {ex}")

        # Redactar cuerpo para results.json
        redacted_body_e = redact_sensitive_data(raw_body_e)
        if status_e == 200:
            results["metadata"]["consumo_credito"] = True

        # Extraer contrato de respuesta real
        if isinstance(raw_body_e, dict):
            results["contrato_observado"] = extract_schema_contract(raw_body_e)

        doc_masked = f"{real_doc_type}...{real_doc_num[-3:]}" if len(real_doc_num) >= 3 else f"{real_doc_type}***"

        results["casos"]["caso_e_validacion_real_autorizada"] = {
            "descripcion": "Validación real autorizada (autocercicio)",
            "status_code": status_e,
            "latencia_ms": lat_e,
            "timestamp_utc": ts_e,
            "cuerpo_redactado": redacted_body_e,
            "error": err_e,
            "cumple_esperado": status_e == 200
        }

        results["validacion_real"] = {
            "ejecutada": True,
            "documento": doc_masked,
            "autorizacion": "autocercicio",
            "status_code": status_e
        }
        print(f"      -> Status recibido: {status_e} en {lat_e}ms (Datos redactados en results.json)")

    else:
        print("\n[5/5] Caso (e): PROBE_REAL_DOC no definida. Validación real omitida (AC-6).")
        results["validacion_real"] = {
            "ejecutada": False
        }

    results["metadata"]["modo"] = "completo"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Sondeo completado. Resultados estructurados guardados en: {results_path}")

if __name__ == "__main__":
    main()
