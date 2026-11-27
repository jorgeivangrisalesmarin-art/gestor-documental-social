# Design — Motor Documental (MVP)

Decisiones vinculantes: ADR-0001..0007 (`docs/adr/`). Este documento las aplica al MVP.

## Arquitectura (monolito modular)

```
web (Next.js) ──HTTP──► api (FastAPI)
                          ├── api/routes      (auth, lookups, batches, documents, health)
                          ├── services        (lookup, batch, document)  ← dominio
                          ├── providers       (base + placapi/* + fixtures)
                          ├── storage         (DocumentStorage: LocalFilesystem)
                          ├── models          (SQLAlchemy: org, users, authorizations,
                          │                    lookup_jobs, documents, batches)
                          └── security        (JWT, Argon2id, HMAC, Fernet)
                        PostgreSQL (DATABASE_URL; sqlite+aiosqlite solo para dev rápido)
```

Reglas de dependencia (ADR-0003): `routes → services → providers/storage`; providers nunca importan la BD; services nunca importan httpx.

## Modelo de datos (brief §11 + ajustes MVP)

- `organizations(id, name, nit, created_at)`
- `users(id, organization_id FK, email unique, password_hash (argon2id), role: admin|operador, created_at)`
- `authorizations(id, organization_id, subject_document_hmac, purpose, authorization_reference, authorized_at, status, expires_at)`
- `batches(id, organization_id, created_by, filename, total_records, processed_records, success_count, error_count, status, created_at)`
- `lookup_jobs(id, organization_id, created_by, batch_id FK nullable, document_type, document_ciphertext, document_hmac, provider, status, result_json, source, error_code, started_at, completed_at)`
  - desviación documentada: `document_ciphertext` (Fernet) + `document_hmac` (HMAC-SHA256) reemplazan el `document_hash` simple del brief (ADR-0004).
- `documents(id, organization_id, lookup_job_id FK, document_type, source, origin, storage_path, mime_type, sha256, generated_at, retrieved_at, verification_status)`

## Contrato de proveedor

```python
class DocumentType(StrEnum): ADRES_AFFILIATION_REPORT; SISBEN_IV_CERTIFICATE; RUI_CERTIFICATE

@dataclass LookupInput: document_type; tipo_documento: str; numero_documento: str
@dataclass LookupResult: document_type; status: DATA_RETRIEVED|NOT_FOUND|DOCUMENT_PENDING|MANUAL_ACTION_REQUIRED
                         data: dict; source: str; consulted_at: datetime

class DocumentProvider(Protocol):
    name: str
    async def lookup(self, input: LookupInput) -> LookupResult
    async def health_check(self) -> ProviderHealth

Errores tipados: ProviderUnauthorized, ProviderPaymentRequired, ProviderNotFound,
ProviderRateLimited, ProviderServerError (reintento solo 429/5xx, máx 2, backoff exponencial).
```

Registro de proveedores por tipo documental, configurable: si `PLACAPI_API_KEY` no existe → adaptador fixture (source="fixture", E8).

## Estados de job

`PENDING → PROCESSING → COMPLETED | FAILED | NOT_FOUND | MANUAL_ACTION_REQUIRED` (+`DOCUMENT_PENDING` como estado de documento asociado).

## API REST (v1)

- `POST /auth/login` → {access_token}; `GET /auth/me`
- `POST /api/v1/lookups` {tipo_documento, numero_documento, document_types[], finalidad, autorizacion_confirmada} → job(s) creados y procesados
- `GET /api/v1/lookups/{id}` → estado + resultados normalizados
- `GET /api/v1/lookups` → historial paginado de la organización
- `POST /api/v1/batches` (multipart CSV/Excel) → validación E13 + creación; `POST /api/v1/batches/{id}/process` → inicia procesamiento; `GET /api/v1/batches/{id}` → E16; `GET /api/v1/batches/{id}/export` → CSV de resultados
- `GET /api/v1/documents/{id}/download` → E11
- `GET /health`, `GET /health/providers` → E18

## Seguridad

JWT HS256 (exp 12h, secreto `JWT_SECRET`); Argon2id; Fernet `DOC_ENCRYPTION_KEY`; HMAC `DOC_HMAC_KEY`; auditoría estructurada sin PII (E17); CORS solo para el origen del frontend (`WEB_ORIGIN`).

## Verificación

pytest (unit: providers/security; integración: API con TestClient + sqlite aislado) + Playwright MCP para los flujos UI (login, consulta fixture, lote pequeño) con captura; registro en `.claude/state/verify.log`.
