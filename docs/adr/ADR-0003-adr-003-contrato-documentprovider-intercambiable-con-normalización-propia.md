---
id: "ADR-0003"
title: "ADR-003: Contrato DocumentProvider intercambiable con normalización propia"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['arquitectura', 'proveedores', 'contrato', 'adaptadores']
policy:
  imports: {'disallow': ['requests (usar httpx async en el backend)'], 'prefer': ['httpx']}
  boundaries: {'rules': [{'forbid': 'services -> placapi/httpx directo (solo capa providers habla HTTP)'}, {'forbid': 'providers -> SQLAlchemy (providers no tocan la BD)'}]}
approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26), plan T002."

---

## Context

El sistema debe consultar tres tipos documentales (ADRES, SISBÉN IV, RUI) a través de proveedores externos (PlacApi hoy, Árbol como alternativa, conectores propios a futuro). El brief prohíbe acoplar el backend a PlacApi y exige separación estricta de los tres tipos documentales y de datos vs documentos oficiales.

## Decision

Contrato común DocumentProvider con dos operaciones: lookup(input) -> LookupResult y healthCheck() -> ProviderHealth. Tipos documentales como enum separado (ADRES_AFFILIATION_REPORT | SISBEN_IV_CERTIFICATE | RUI_CERTIFICATE). Cada adaptador (placapi-eps, placapi-sisben, placapi-rui, arbol-adres) transforma SU respuesta cruda a un LookupResult normalizado del dominio; el dominio NUNCA ve los modelos de PlacApi/Árbol (don't import modelos de proveedores fuera de providers/). Errores tipados: ProviderUnauthorized(401), ProviderPaymentRequired(402), ProviderNotFound(404), ProviderRateLimited(429), ProviderServerError(5xx) con reintentos solo para 429/5xx.

## Consequences

Acoplamiento: servicios dependen solo del protocolo DocumentProvider y de LookupResult; agregar Árbol o conectores propios no cambia routers ni motor. Consistencia: LookupResult siempre incluye fuente, fecha_consulta y estado (DATA_RETRIEVED | NOT_FOUND | DOCUMENT_PENDING | MANUAL_ACTION_REQUIRED) — sin consistencia eventual entre proveedores. Rollback: registrar/desregistrar proveedor en el registry sin deploy adicional (config-driven). Observabilidad: healthCheck expuesto en /health/providers; latencia y error_code por proveedor en logs estructurados. Deuda técnica: fallback automático entre proveedores (fase 2) requerirá una capa de routing por tipo documental sobre este mismo contrato. EARS: WHEN un proveedor responde 429/5xx THEN el adaptador reintenta con backoff máximo 2 veces y registra error_code; WHEN responde 401/402 THEN marca el proveedor degradado sin reintentar.

## Alternatives

Usar SDKs de cada proveedor filtrando en servicios (descartado: acopla dominio a contratos de terceros y duplica normalización); capa única genérica por documento (descartado: los tres tipos tienen contratos distintos y el brief exige separación).
