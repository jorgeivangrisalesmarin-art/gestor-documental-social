# Spec EARS — Motor Documental (MVP)

Fuente única de verdad de los criterios de aceptación. Copiar al ticket, nunca reescribir.

## 1. Autenticación y organizaciones

- **E1** CUANDO un usuario envía credenciales válidas a `POST /auth/login` EL SISTEMA DEBERÁ retornar un JWT (exp 12 h) con org_id y role, y registrar el login en auditoría sin el password.
- **E2** CUANDO un endpoint protegido recibe un token inválido, expirado o ausente EL SISTEMA DEBERÁ responder 401 sin revelar información del recurso.
- **E3** CUANDO un usuario de organización A consulta recursos de organización B EL SISTEMA DEBERÁ responder 404 (sin filtrar existencia).
- **E4** CUANDO el sistema arranque por primera vez EL SISTEMA DEBERÁ crear la organización inicial y un usuario admin desde variables de entorno (`SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`).

## 2. Consulta individual (proveedores)

- **E5** CUANDO se solicita una consulta de un tipo documental (ADRES | SISBEN_IV | RUI) EL SISTEMA DEBERÁ crear un `lookup_job` con estado `PENDING`, resolverlo con el adaptador activo del registro de proveedores y persistir el `LookupResult` normalizado sin exponer la key del proveedor.
- **E6** CUANDO el proveedor responde 401 o 402 EL SISTEMA DEBERÁ marcar el job `FAILED` con `error_code` correspondiente y NO reintentar.
- **E7** CUANDO el proveedor responde 429 o 5xx EL SISTEMA DEBERÁ reintentar con backoff (máx. 2) y, si persiste, marcar `FAILED` con `error_code`.
- **E8** CUANDO no hay credencial configurada para el proveedor EL SISTEMA DEBERÁ usar el adaptador fixture (etiquetado como ficticio) y el resultado DEBERÁ marcarse `source="fixture"` para nunca presentarse como consulta real.
- **E9** CUANDO la respuesta es exitosa pero el proveedor no entrega PDF oficial EL SISTEMA DEBERÁ registrar estado `DOCUMENT_PENDING` (los datos JSON nunca se presentan como documento oficial).

## 3. Motor documental y almacenamiento

- **E10** CUANDO se almacena un documento EL SISTEMA DEBERÁ generar nombre seguro (UUID + extensión validada), calcular sha256, registrar fuente, fecha de consulta y estado, y guardar en el storage configurado (FS local en dev).
- **E11** CUANDO un usuario con sesión válida solicita `GET /api/v1/documents/{id}/download` de su organización EL SISTEMA DEBERÁ transmitir el archivo; sin sesión o de otra organización → 401/404.
- **E12** CUANDO se consulta la identificación de una persona EL SISTEMA DEBERÁ persistirla cifrada (Fernet) y su índice como HMAC-SHA256 con clave dedicada; NUNCA en texto plano ni en logs.

## 4. Consulta masiva (lotes)

- **E13** CUANDO se carga un CSV/Excel EL SISTEMA DEBERÁ validar columnas mínimas (tipo_documento, numero_documento, adres, sisben_iv, rui, autorizacion_confirmada, referencia_autorizacion) y responder el resumen de validación sin procesar registros inválidos.
- **E14** CUANDO un lote inicia procesamiento EL SISTEMA DEBERÁ procesar cada registro con estados persistidos (PENDING→VALIDATING→QUEUED→PROCESSING→COMPLETED/PARTIAL_SUCCESS/FAILED), concurrencia limitada (semáforo) y control de duplicados.
- **E15** CUANDO un registro sin `autorizacion_confirmada=true` aparece en el lote EL SISTEMA DEBERÁ excluirlo del procesamiento y registrar el motivo.
- **E16** CUANDO se consulta el estado de un lote EL SISTEMA DEBERÁ retornar contadores y estado individual por documento.

## 5. Seguridad y auditoría

- **E17** CUANDO cualquier operación mutante ocurre EL SISTEMA DEBERÁ registrar en auditoría usuario, organización, operación y job_id — sin identificadores en claro.
- **E18** CUANDO la app arranca EL SISTEMA DEBERÁ exponer `/health` y `/health/providers` (estado de auth por proveedor, sin secretos).

## Alcance NO incluido en este spec (MVP)

WhatsApp, asistente IA, multi-tenancy completo, facturación, fallback automático entre proveedores, automatización web de portales, Redis/Celery (ADR-007), PDFs generados propios.
