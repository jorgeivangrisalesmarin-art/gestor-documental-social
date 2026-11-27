---
id: "ADR-0007"
title: "ADR-007: Cola de lotes in-process en MVP (PostgreSQL), Redis/Celery en fase 2"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['masivos', 'cola', 'mvp', 'deuda-tecnica']
policy:
  imports: {'disallow': ['celery', 'redis (en el MVP)'], 'prefer': ['asyncio', 'sqlalchemy']}
  rationales: ['Menos servicios = menos costo y menos superficie de fallo para el piloto', 'Los estados ya viven en PostgreSQL (batches.processed_records, lookup_jobs.status)']
approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26), plan T002."

---

## Context

El brief propone Redis + Celery para el procesamiento masivo, pero el MVP debe ser funcional en una sesión con el mínimo de servicios (no sobredimensionar: regla 24.1 del brief), y los lotes del piloto son pequeños (<=100 registros). Introducir Redis+worker duplica la infraestructura del MVP.

## Decision

En el MVP, la cola de lotes es IN-PROCESS: FastAPI BackgroundTasks + control de concurrencia con asyncio.Semaphore + estados persistidos en PostgreSQL (batches/lookup_jobs). Don't añadir Redis ni Celery en el MVP; la interfaz interna (BatchProcessor) queda preparada para reemplazarse por un worker con Redis en fase 2 sin cambiar routers ni frontend.

## Consequences

Acoplamiento: routers dependen de la interfaz BatchProcessor; swap a Redis no toca API ni frontend. Consistencia: los estados se persisten por job ANTES y DESPUÉS de cada consulta (crash-safe por registro: un crash deja jobs en PROCESSING que un endpoint de recuperación puede re-marcar FAILED). Rollback: sin componente nuevo — revert de código. Observabilidad: progreso consultable GET /batches/{id} leyendo BD; log de cada job con batch_id. Deuda técnica: migración programada a Redis/Celery en fase 2 (lotes >1k, reintentos distribuidos, scheduling). EARS: WHEN un lote se procesa THEN cada registro pasa por estados PENDING->VALIDATING->QUEUED->PROCESSING->COMPLETED/PARTIAL_SUCCESS/FAILED persistidos en BD; WHEN el proceso muere a mitad THEN los jobs en PROCESSING quedan detectables y no se pierde el resultado ya obtenido.

## Alternatives

Redis+RQ/Celery desde el día 1 (descartado: viola la regla de no sobredimensionar; requerido en fase 2 para lotes grandes y reintentos distribuidos); Cloud Tasks (alternativa gestionada de fase 2).
