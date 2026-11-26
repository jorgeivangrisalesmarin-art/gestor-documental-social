# Índice de documentación — Gestor Documental Social

Jerarquía de autoridad: **ADRs (`docs/adr/`) > planes (`plan-*.md`) > tareas y runbooks (`tareas/`) > README del proyecto**.
La documentación generada automáticamente por LLM (wikis) es desechable: nunca fuente de verdad.

## Raíz

- `../PROMPT-EQUIPO-DESARROLLO.md` — prompt maestro: equipo experto de desarrollo + metodología 4 capas + flujo por desarrollador (Jorge/Claude Code, juniors/Antigravity). Pegar al inicio de cada sesión de agente.
- `../1.0 PROJECT BRIEF + MASTER DEVELOPMENT PROMPT.md` — brief original del producto (visión, requisitos, reglas de ingeniería).
- `../Documento de dirección técnica y plan de desarrollo.md` — estrategia de fases y decisión de producto.

## docs/

- [plan-desarrollo-despliegue-gcp.md](plan-desarrollo-despliegue-gcp.md) — plan vigente: ADRs por crear, arquitectura GCP (Cloud Run/SQL/Redis/GCS/Secret Manager), EARS, 14 tareas asignadas (T001–T014), entornos, costos, riesgos, DoD.
- [T001-sondeo-apis-proveedores-juniors.md](tareas/T001-sondeo-apis-proveedores-juniors.md) — primera tarea de los juniors: script de sondeo por endpoint (Jhon: placapi/eps · Markos: placapi/sisben · Yeison: placapi/rui · Pepito: arbol/adres + matriz comparativa).

## Pendiente de crear (según plan)

- `docs/adr/ADR-001…006` — decisiones MADR (backend, topología GCP, contrato proveedores, auth, CI/CD, documentos) — tarea T002.
- `docs/T001-matriz-proveedores.md` — entregable de Pepito (T001).
- `.kiro/specs/` — specs EARS por feature (Capa 3) — desde T003/T004.
