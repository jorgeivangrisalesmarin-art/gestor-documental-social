# Gestor Documental Social

Motor documental para consultar y descargar reportes/certificados de **ADRES**, **SISBÉN IV** y **RUI** con proveedores intercambiables (PlacApi hoy; Árbol y conectores propios en fases siguientes). Diseñado para la atención en ventanilla de alcaldías (piloto: Alcaldía de Andes, Antioquia).

## Arquitectura (ADR-0001/0002/0003)

| Componente | Stack | Ubicación |
|---|---|---|
| API del motor | Python 3.12 + FastAPI (monolito modular) | `api/` |
| Web administrativa | Next.js 15 (App Router, TypeScript) | `web/` |
| BD | PostgreSQL (Cloud SQL en GCP; sqlite solo dev rápido) | `docker-compose.yml` |
| Documentos | FS local en dev → GCS privado con URL firmada (ADR-0006) | `api/app/storage.py` |
| Lotes | In-process con semáforo (ADR-007); Redis/Celery en fase 2 | `api/app/services/batch_service.py` |
| CI/CD | Cloud Build → staging auto; prod solo manual N1 (ADR-0005) | `cloudbuild.yaml` |

**Seguridad desde el diseño** (ADR-0004): identificaciones cifradas Fernet + huella HMAC-SHA256 para índice/deduplicación; auditoría estructurada **sin identificadores en claro**; JWT HS256 + Argon2id; CORS restringido al origen web.

## Inicio rápido

```bash
# 1. Backend (sqlite dev; para Postgres: docker compose up postgres)
python3 -m venv .venv
source .venv/bin/activate
pip install -e "./api[dev]"
uvicorn app.main:app --reload --port 8000   # desde api/ con: cd api && uvicorn app.main:app --reload
```

Uvicorn desde api/: `cd api && ../.venv/bin/uvicorn app.main:app --reload --port 8000`
y frontend: `cd web && npm install && npm run dev`.

Admin inicial (seed): `admin@local.test` / `admin1234` (variables `SEED_ADMIN_*`; cambiar en prod).

## Tareas de equipo (metodología 4 capas)

- Prompt maestro del equipo: `PROMPT-EQUIPO-DESARROLLO.md`
- Plan GCP: `docs/plan-desarrollo-despliegue-gcp.md`
- T001 juniors: `docs/tareas/T001-…juniors.md` (sondeo APIs proveedores)
- Specs EARS: `.kiro/specs/motor-documental/requirements.md`
- ADRs: `docs/adr/` (0001-0007, formato MADR)
- Test report y verify.log: `docs/TEST_REPORT.md`, `.claude/state/verify.log`
- Runbook de despliegue GCP: `deploy/gcp-deploy-runbook.md` (T010/T011, solo N1)

## Reglas inviolables del proyecto (resumen)

1. Consultas con datos reales solo con autorización del titular (autocercicio válido para validación técnica) y finalidad registrada.
2. Ningún secreto en código/Git — solo variables de entorno o Secret Manager.
3. JSON ≠ documento oficial: sin PDF real, el estado es DOCUMENT_PENDING.
4. Nunca presentar datos fixture como reales (el UI lo etiqueta siempre).
5. Los juniors no hacen merge ni despliegan: PR → revisión de Jorge → main.
