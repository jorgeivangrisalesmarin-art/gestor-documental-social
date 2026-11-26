# Plan de desarrollo y despliegue en Google Cloud — Gestor Documental Social

**Tipo:** plan de sesión (intención/diseño). Jerarquía: ADRs > este plan > runbooks.
**Fecha:** 2026-11-26 · **Estado:** vigente
**Equipo:** Jorge (senior) · Jhon, Markos, Yeison, Pepito (juniors, con Antigravity)
**Metodología:** 4 capas del stack — ADR (adr-kit/MADR) → Ticket → Spec EARS (Kiro) → PR revisado + verificación real.

---

## 1. Objetivo

Construir el MVP del motor documental (consulta individual y masiva de ADRES,
SISBÉN IV y RUI vía proveedores intercambiables) y desplegarlo en Google Cloud
en dos entornos (staging y producción), con el flujo de trabajo del equipo:
cada junior ejecuta paquetes de trabajo con su agente Antigravity, Jorge
revisa los PR y aprueba merge a `main` y todo despliegue.

**Producto de esta sesión (T001):** sondeo verificado de las APIs de los
proveedores por cada junior → `docs/tareas/T001-sondeo-apis-proveedores-juniors.md`.

## 2. Decisiones arquitectónicas — Capa 1 (ADRs por crear en la próxima sesión)

Con `adr_preflight` antes de cada creación; aprobación con `adr_approve`
nunca dejarlos en propuesta. Cada ADR responde: acoplamiento, consistencia
eventual, rollback, observabilidad, deuda técnica.

| ADR | Decisión | Opciones en tensión | responsable |
| --- | --- | --- | --- |
| ADR-001 | Backend **Python 3.12 + FastAPI** (contenedor único, monolito modular) vs NestJS/TypeScript vs Django | FastAPI es el stack propuesto en el brief; async nativo para proveedores I/O-bound; validación Pydantic | Jorge |
| ADR-002 | **Topología GCP**: Cloud Run + Cloud SQL (PostgreSQL) + Memorystore (Redis) + Cloud Storage + Secret Manager + Artifact Registry + Cloud Build | Cloud Run serverless vs GKE; Cloud SQL vs AlloyDB; GCS vs S3-compatible en otro proveedor | Jorge |
| ADR-003 | **Contrato `DocumentProvider`** (lookup + healthCheck) con adaptadores por proveedor y normalización propia | Interfaz única vs SDKs de cada proveedor filtrando hasta el dominio | Jorge |
| ADR-004 | **Autenticación de la app**: sesión con roles (admin/operador) por organización, hash Argon2id; HMAC-SHA256 con clave en Secret Manager para hashes de documento | OAuth externo vs sesión propia para el MVP | Jorge |
| ADR-005 | **CI/CD**: Cloud Build + Cloud Deploy; staging automático tras PR mergeado; producción SOLO manual vía checkpoint N1 | Trunk-based vs GitFlow | Jorge |
| ADR-006 | Manejo de **documentos**: bucket GCS privado, nombres seguros, sha256, sin enlaces públicos, descarga firmada de corta duración generada por el backend | GCS firmado vs proxy de descarga por el backend | Jorge |

## 3. Arquitectura objetivo en Google Cloud

```
                         ┌─────────────────────────────────────────────┐
 Usuario (funcionario)   │                  Proyecto GCP                │
        │  HTTPS         │                                              │
        ▼                │  Cloud Load Balancer + Cloud Armor (fase 2)  │
   [ App Web ] ──────────┼──► Cloud Run «web» (Next.js/React estático)  │
        │  REST JSON     │        │                                     │
        ▼                │        ▼                                     │
   Cloud Run «api» ◄─────┼── FastAPI: motor documental + colas + audit  │
        │                │   ├─ Secret Manager (PLACAPI_API_KEY,        │
        │                │   │   ARBOL_API_KEY, HMAC_KEY, DB/Redis)     │
        │                │   ├─ Cloud SQL PostgreSQL (IP privada)       │
        │                │   ├─ Memorystore Redis (colas/lotes)         │
        │                │   └─ Cloud Storage bucket privado (docs)     │
        ▼                │                                              │
   Proveedores ──────────┼── PlacApi (x-api-key) / Árbol (Bearer)       │
   ADRES·SISBÉN·RUI      │   egress por Cloud NAT (IP fija, fase 2)     │
                         │  Cloud Build + Artifact Registry (CI/CD)     │
                         │  Cloud Logging/Monitoring + alertas          │
                         └─────────────────────────────────────────────┘
```

Decisiones de despliegue:

- **MVP = 2 servicios Cloud Run** (`web`, `api`) en `us-central1` o `southamerica-west1` (región más cercana a Colombia; verificar precio/latencia — decisión en ADR-002). Escala a cero para costo mínimo.
- **Cloud SQL** con IP privada + conector nativo desde Cloud Run; sin IP pública.
- **Secret Manager** para `PLACAPI_API_KEY`, `ARBOL_API_KEY`, `DOC_HMAC_KEY`, credenciales DB/Redis — jamás en `.env` versionado (`.env.example` solo con nombres).
- **Service accounts por servicio** con mínimo privilegio (Cloud Run → Secret Accessor + SQL Client + Storage Object Admin sobre su bucket).
- **CI/CD (ADR-005):** merge a `main` → Cloud Build (test + lint + build + push Artifact Registry) → deploy automático a **staging**. **Producción: solo aprobación explícita de Jorge** (protocolo N1) con tag de release.
- Las mutaciones GCP (crear proyecto/recursos, autorizar redes, secretos, migraciones sobre datos reales) son **checkpoint N1**: lista `Cn` con qué cambia/riesgo/rollback/comando exacto y una línea de respuesta por lote.

## 4. Modelo de datos y contratos

- Entidades del brief §11 (`organizations`, `users`, `authorizations`,
  `lookup_jobs`, `documents`, `batches`) — migraciones Alembic desde el día 1.
- Números de identificación: nunca en logs ni en texto plano en reportes;
  `document_hash` = HMAC-SHA256(clave en Secret Manager).
- Contrato de proveedor (fuente única: `.kiro/specs/motor-documental/`):

```
interface DocumentProvider:
  lookup(input: LookupInput) -> LookupResult   # datos normalizados + referencia de fuente
  healthCheck() -> ProviderHealth              # auth OK, latencia, creditos/cuota
DocumentType = ADRES_AFFILIATION_REPORT | SISBEN_IV_CERTIFICATE | RUI_CERTIFICATE
```

## 5. Requisitos clave en EARS (Capa 3 — se detallan por spec en `.kiro/specs/`)

**Proveedores**
- CUANDO el backend recibe una consulta de tipo X EL SISTEMA DEBERÁ resolverla con el adaptador activo de X sin exponer la clave del proveedor.
- CUANDO un proveedor responde 401/402/429/5xx EL SISTEMA DEBERÁ registrar `error_code`, aplicar reintento solo para 429/5xx con backoff, y marcar `MANUAL_ACTION_REQUIRED` si persiste.
- CUANDO `healthCheck` de un proveedor falla N veces seguidas EL SISTEMA DEBERÁ marcarlo degradado en el panel Proveedores y bloquear nuevos jobs hacia él.

**Motor documental**
- CUANDO una consulta retorna datos JSON EL SISTEMA DEBERÁ registrar el documento como `DOCUMENT_PENDING` salvo que exista un mecanismo autorizado de obtención del PDF oficial (nunca presentar JSON como documento).
- CUANDO se almacena un documento EL SISTEMA DEBERÁ calcular sha256, guardar en bucket privado con nombre seguro y registrar fuente y fecha de consulta.

**Masivos**
- CUANDO un lote se procesa EL SISTEMA DEBERÁ validar autorización y finalidad por registro, controlar concurrencia y duplicados, y exponer estado individual por documento.
- CUANDO un registro no cumple condiciones de autorización EL SISTEMA DEBERÁ excluirlo del procesamiento y registrarlo con motivo.

**Seguridad**
- CUANDO cualquier endpoint recibe una request EL SISTEMA DEBERÁ exigir sesión válida y registrar en auditoría usuario, finalidad y operación.
- CUANDO se descarga un documento EL SISTEMA DEBERÁ hacerlo solo mediante enlace firmado de corta duración generado por el backend.

## 6. Plan de tareas y asignación

Estados: `todo · doing · review · blocked · done`. Estimaciones en horas de reloj del desarrollador.

| ID | Tarea | P | Asignado | Est. | Depende | Criterios de aceptación (resumen EARS) | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T001 | Sondeo APIs proveedores (script por junior) | P0 | Jhon: `POST /api/eps` · Markos: `POST /api/sisben` · Yeison: `POST /api/rui` · Pepito: Árbol ADRES + matriz comparativa | 2–3 c/u | — | Ver `docs/tareas/T001-…juniors.md` (criterios completos) | doing |
| T002 | ADRs 001–006 (sesión de arquitectura) | P0 | Jorge | 4 | T001 | 6 ADRs MADR aprobados con consecuencias rigurosas | todo |
| T003 | Scaffold monorepo: `api/` (FastAPI), `web/`, `.kiro/specs/`, CI base, `.env.example`, README | P0 | Jorge + Yeison | 6 | T002 | Repo corre `make dev`; lint+tests en verde; PRs con template | todo |
| T004 | Contrato `DocumentProvider` + normalización + errores tipados + fixtures ficticios | P0 | Jorge | 6 | T003 | Spec EARS aprobada; pruebas unitarias de contrato | todo |
| T005 | Adaptadores PlacApi (eps/sisben/rui) sobre T001 + reintentos + rate limit | P0 | Jhon + Markos | 8 | T001,T004 | CUANDO hay key, consulta real de prueba pasa; SIN key, fixtures etiquetados | todo |
| T006 | Motor documental: estados, sha256, bucket local→GCS, auditoría | P0 | Jorge + Yeison | 8 | T004 | Criterios EARS "Motor documental" PASS con evidencia | todo |
| T007 | API REST: consulta individual, estado de job, descarga firmada | P0 | Pepito | 8 | T006 | OpenAPI publicada; pruebas de integración en verde | todo |
| T008 | Frontend web: consulta individual + historial + descargas | P0 | Jhon | 10 | T007 | Flujos verificados con Playwright y captura | todo |
| T009 | Masivos: carga Excel/CSV, validación, cola Redis, ZIP | P1 | Markos | 12 | T007 | Criterios EARS "Masivos" PASS; lote de prueba ≤ 10 registros | todo |
| T010 | Infra GCP: proyecto, APIs, Cloud SQL, Redis, bucket, SA, secretos | P0 | Jorge (checkpoint N1) | 6 | T002 | `terraform/` o `gcloud` scripted; rollback documentado | todo |
| T011 | CI/CD Cloud Build → staging; deploy prod manual N1 | P0 | Jorge | 6 | T010,T003 | Merge a main despliega staging; prod requiere aprobación | todo |
| T012 | Seguridad y cumplimiento: HMAC, auditoría, minimización, rate limit, Ley 1581 checklist | P0 | Jorge + Pepito | 8 | T006 | Checklist §15 del brief PASS; revisión de seguridad limpia | todo |
| T013 | Pruebas E2E + TEST_REPORT + README instalación | P0 | Yeison | 6 | T008,T009 | Los 10 puntos BLOQUE 6 del brief verificados con evidencia | todo |
| T014 | Piloto con funcionario SISBÉN Andes (demo autorizada) | P1 | Jorge | 4 | T013,T012 | Demo real con autorización registrada; feedback registrado | todo |

**Orden crítico:** T001 → T002 → T003/T004 → T005/T006 → T007 → T008/T009 → T010/T011 en paralelo desde T002 → T012/T013 → T014.

## 7. Entornos

| Entorno | Dónde | Datos | Deploy |
| --- | --- | --- | --- |
| local | máquina de cada dev | fixtures ficticios | `make dev` |
| staging | proyecto GCP `gds-staging` | datos de prueba ficticios | automático tras merge a `main` |
| producción | proyecto GCP `gds-prod` (o proyecto único con dos servicios etiquetados si el presupuesto lo exige — decidir en ADR-002) | datos reales autorizados | **solo manual con checkpoint N1 de Jorge** |

## 8. Costos estimados MVP (mensual, a validar en T010)

- Cloud Run escala a 0: ~$0–10 · Cloud SQL smallest HA-off: ~$10–30 · Memorystore smallest: ~$30–45 · GCS + egress: ~$1–5 · LB/Armor solo si hay dominio (fase 2). Créditos PlacApi: variable por volumen de consultas (presupuestar con los resultados del sondeo T001). **Total MVP ≈ USD 45–90/mes + créditos de proveedor.**

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
| --- | --- |
| Sin credenciales PlacApi/Árbol | T005 con fixtures etiquetados; solicitar credenciales sandbox a proveedores (acción externa → checkpoint N1) |
| Tratamiento de datos personales sin fundamento jurídico | Nada de consultas con datos reales sin autorización escrita + finalidad; checklist Ley 1581/2012 en T012; validación institucional antes del piloto (T014) |
| Confusión JSON ≠ documento oficial | Estados `DOCUMENT_PENDING` y etiquetado visual obligatorio (regla 4 del prompt maestro) |
| Dependencia de un solo proveedor | Contrato intercambiable (ADR-003); Árbol como fallback en fase 2 |
| Juniors suben secretos o hacen merge sin revisión | Reglas inviolables del prompt + protección de rama `main` (PR obligatorio, solo Jorge aprueba) + scan de secretos en CI |

## 10. Definition of Done (global)

1. Criterios EARS del paquete PASS verificados con evidencia (no asumidos).
2. PR revisado en contexto limpio, sin archivos fuera de alcance, sin tests alterados para pasar.
3. `.claude/state/verify.log` actualizado (fecha, tarea, PASS/FAIL, evidencia).
4. Ticket y spec actualizados; índice `docs/README.md` al día en el mismo cambio.
5. Merge aprobado por Jorge; CI verde; deploy solo según reglas de §7.
