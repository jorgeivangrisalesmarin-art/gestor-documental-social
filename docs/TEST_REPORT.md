# TEST_REPORT — MVP motor documental (2026-11-27)

## 1. Pruebas automatizadas (pytest)

**26/26 PASS** · `make test` · cobertura de criterios:

| Suite | Criterios | Resultado |
|---|---|---|
| test_security.py | JWT válido/forjado, Argon2id, HMAC determinista, Fernet roundtrip (E12) | 6/6 PASS |
| test_providers.py | fixtures E8, NOT_FOUND, tipos separados, reintento 429 vs no-reintento 401 (E6/E7), paths eps/sisben/rui | 8/8 PASS |
| test_api.py | health E18, login E1, 401 sin token E2, lookup 422 sin autorización, lookup fixture E5/E8, NOT_FOUND, tipo inválido, batch completo E13–E16, exclusión E15, columnas malas, reproceso 409 | 12/12 PASS |

Lint: `ruff check` limpio.

## 2. Verificación E2E real (Playwright MCP) — evidencia adjunta

Entorno: API uvicorn :8001 (sqlite dev, fixtures), Web `next start` :3000 (build producción).

| # | Flujo | Resultado | Evidencia |
|---|---|---|---|
| 1 | Login admin → dashboard | PASS | snapshot 01-17-08 |
| 2 | Consulta individual CC/123456789 + ADRES + SISBÉN IV → 2 jobs COMPLETED, fuente fixture, avisos FICTICIO, documento redactado ***789 | PASS | snapshot 01-17-36 |
| 3 | Carga lote CSV 4 filas → validación, 4 jobs + 1 EXCLUDED (SIN_AUTORIZACION, E15) visible en UI | PASS | snapshot 01-18-24 |
| 4 | Procesamiento lote → COMPLETED, estados por documento (Completada/No encontrado/Excluida); 2º clic → 409 anti-doble-proceso | PASS | snapshot 01-18-37 + e2e-masiva-completed.png |
| 5 | Historial: 7 jobs con tipo/estado/fuente correctos | PASS | snapshot 01-19-02 |
| 6 | Proveedores: 3 tipos OK en modo fixture | PASS | snapshot 01-19-18 |

## 3. Limitaciones conocidas (no bloquean MVP)

1. Sin PLACAPI_API_KEY todo corre en modo fixture etiquetado (E8) — ninguna consulta real fue probada aún.
2. Conteo de lotes: la exclusión (EXCLUDED) se refleja en "Errores" — separar en fase 2 en su propia columna.
3. JWT en localStorage — migrar a cookie httpOnly antes de producción (ADR-0004 deuda).
4. Documentos PDF: endpoints y storage listos (E10/E11); sin PDFs reales hasta tener proveedor autorizado — DOCUMENT_PENDING funciona.
5. Favicon 404 cosmético; chunk stale del primer build (resuelto reiniciando next start).

## 4. Pendiente de credenciales

- PLACAPI_API_KEY → conmutar a proveedores reales (`/health/providers` pasa a "credencial configurada").
- T001 juniors entrega contratos reales para pulir normalizadores PlacApi.
