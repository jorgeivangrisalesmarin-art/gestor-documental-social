---
id: "ADR-0005"
title: "ADR-005: CI/CD Cloud Build — staging automático, producción solo manual (N1)"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['cicd', 'gcp', 'cloudbuild', 'deploy']
policy:
  boundaries: {'rules': [{'forbid': 'push directo de humanos a main (siempre via PR)'}, {'forbid': 'deploy prod automático en cualquier pipeline'}]}
approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26), plan T002."

---

## Context

El equipo tiene 1 senior y 4 juniors; se necesita calidad constante en main y despliegues a producción controlados por el senior (protocolo N1: deploy NUNCA automático). Alternativas: GitHub Actions (requiere runners y secretos adicionales), GitLab CI (otro proveedor), deploy manual sin CI (frágil con juniors).

## Decision

CI/CD con Cloud Build + Artifact Registry + Cloud Deploy (o gcloud run deploy en el pipeline del MVP): merge a main dispara build (lint ruff + pytest + build imágenes) y deploy automático SOLO a staging; producción requiere aprobación explícita de Jorge (checkpoint N1) y tag de release (v*). Don't deploy to production automatically; don't push directamente a main (PR obligatorio con revisión del senior).

## Consequences

Acoplamiento: el pipeline solo depende del repo y de APIs gestionadas de GCP; las imágenes se nombran por commit SHA (trazabilidad). Consistencia: staging puede divergir temporalmente de prod hasta el siguiente N1 (ventana tolerada: horas). Rollback: deploy de la imagen SHA anterior conocida-buena en minutos. Observabilidad: historial de builds en Cloud Build; badge de estado en README; alerta en fallo de build de main. Deuda técnica: entornos efímeros por PR (preview) cuando el presupuesto lo permita; escaneo de secretos automatizado en CI (gitleaks) antes del primer release real. EARS: WHEN un merge llega a main THEN Cloud Build ejecuta lint+tests y despliega staging sin intervención; WHEN el build falla THEN main se considera rota y se bloquea el deploy a prod hasta corrección.

## Alternatives

GitHub Actions (alternativa válida si Cloud Build resulta limitado; mantener los mismos gates); trunk sin CI (descartado: con juniors, main debe quedar siempre verde).
