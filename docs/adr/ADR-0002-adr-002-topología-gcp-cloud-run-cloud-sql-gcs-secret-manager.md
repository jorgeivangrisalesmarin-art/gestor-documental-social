---
id: "ADR-0002"
title: "ADR-002: Topología GCP — Cloud Run + Cloud SQL + GCS + Secret Manager"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['gcp', 'cloud-run', 'infraestructura', 'topologia']approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26), plan T002."

---

## Context

El producto debe desplegarse en Google Cloud (decisión de producto de Jorge) con presupuesto mínimo para MVP de alcaldías en Colombia, sin operación de Kubernetes y con datos sensibles de salud (Ley 1581). Alternativas: GKE (demasiada operación para MVP), VM Compute Engine (gestión de SO manual), App Engine (menos control de contenedor).

## Decision

Topología GCP serverless: Cloud Run (servicios 'api' FastAPI y 'web' Next.js) en us-central1 (latencia y costo óptimos para Colombia; sin región GCP local), Cloud SQL PostgreSQL 16 con IP privada + conector nativo, Memorystore Redis (fase 2), Cloud Storage bucket privado para documentos (ADR-0006), Secret Manager para credenciales, Artifact Registry + Cloud Build para CI/CD (ADR-0005). No usar GKE ni VMs en el MVP.

## Consequences

Acoplamiento: la app solo depende de contratos gestionados (PORT dinámico, variables de entorno, SQLAlchemy URL, bucket GCS vía librería cliente) — sin dependencias de APIs internas de Cloud Run. Consistencia: PostgreSQL transaccional (Cloud SQL, sin consistencia eventual); Redis solo para caché/cola en fase 2 (ADR-007). Rollback: revisión de Cloud Run anterior + migraciones Alembic compatibles hacia atrás (expand-contract). Observabilidad: Cloud Logging estructurado, Cloud Monitoring con alertas de 5xx y latencia, health checks de Cloud Run sobre /health. Deuda técnica: Load Balancer + Cloud Armor y Cloud NAT con IP fija quedan para fase 2 (cuando haya dominio y proveedor requiera allowlist). Criterios EARS: WHEN Cloud Run escala a cero THEN la app debe arrancar en <30 s y ejecutar migraciones como paso de release separado, no en el arranque del contenedor.

## Alternatives

GKE Autopilot (descartado: costo y operación altos para MVP); Compute Engine + Docker (descartado: gestión de SO/escalado manual); southamerica-west1 (alternativa de región si se requiere residencia de datos en Suramérica).
