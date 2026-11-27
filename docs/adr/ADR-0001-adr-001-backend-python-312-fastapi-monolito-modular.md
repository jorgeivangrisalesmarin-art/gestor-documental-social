---
id: "ADR-0001"
title: "ADR-001: Backend Python 3.12 + FastAPI (monolito modular)"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['backend', 'python', 'fastapi', 'stack']
policy:
  imports: {'disallow': ['flask', 'django', 'litestar'], 'prefer': ['fastapi', 'pydantic', 'httpx', 'sqlalchemy', 'alembic']}
  python: {'disallow_imports': ['flask', 'django']}
  rationales: ['FastAPI da async nativo para I/O de proveedores y OpenAPI automático', 'Pydantic valida contratos de proveedores con tipos estrictos']approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26) en ejecución del plan T002; alineado con stack del decisor (Python/Next.js)."

---

## Context

El motor documental debe consumir APIs externas I/O-bound (PlacApi, Árbol) con alto paralelismo potencial y validación estricta de payloads. El stack propuesto en el brief es Python+FastAPI; Jorge (senior/decisor) ya desarrolla en Python y Next.js en otros proyectos, lo que reduce fricción de mantenimiento. Alternativas: NestJS/TypeScript (un solo lenguaje con el frontend), Django (baterías incluidas pero async menos natural para este caso), Go (rendimiento pero menor velocidad de desarrollo MVP).

## Decision

Backend en Python 3.12 + FastAPI (monolito modular), SQLAlchemy 2 (async) + Alembic, Pydantic v2 para validación, httpx async para proveedores. Prefer FastAPI; don't use Flask o Django como framework web del backend. UI web en Next.js separado (ver estructura del repo y ADR-002).

## Consequences

Acoplamiento: el dominio queda desacoplado de FastAPI mediante capa de servicios (routers → services → providers); el contrato DocumentProvider no expone httpx al dominio. Consistencia: transacciones locales en PostgreSQL (sin consistencia eventual en MVP); la cola de lotes es asíncrona pero con estado en BD (ver ADR-007). Rollback: sin downtime — revert de deploy en Cloud Run a revisión anterior. Observabilidad: /health y /health/providers; logs estructurados JSON con request_id; métricas de latencia por proveedor. Deuda técnica: migración futura de cola in-process a Redis/Celery (ADR-007). Criterio EARS: WHEN una consulta llega THEN el router responde sin bloquear el event loop (httpx async), objetivo p95 <500 ms sin contar al proveedor.

## Alternatives

NestJS/TS (descartado: duplicaría modelos de dominio entre lenguajes y el decisor ya domina Python); Django+DRF (descartado: async aún menos maduro para múltiples proveedores concurrentes); Go (descartado: menor velocidad MVP).
