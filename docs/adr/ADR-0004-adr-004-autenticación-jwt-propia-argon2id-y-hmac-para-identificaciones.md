---
id: "ADR-0004"
title: "ADR-004: Autenticación JWT propia, Argon2id y HMAC para identificaciones"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['seguridad', 'auth', 'ley1581', 'hmac']
policy:
  imports: {'disallow': ['python-jose (usar pyjwt)', 'passlib (usar argon2-cffi directo)'], 'prefer': ['pyjwt', 'argon2-cffi', 'cryptography']}
  rationales: ['pyjwt es mantenido y mínimo; python-jose está descontinuado', 'argon2-cffi implementa Argon2id sin capa extra']
approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26), plan T002."

---

## Context

La app maneja datos personales sensibles (salud, Ley 1581) de varias organizaciones (alcaldías). Se necesita control de acceso desde el MVP sin la complejidad de SSO/OAuth externo, y el brief exige no almacenar números de identificación en logs y usar HMAC con clave secreta (no SHA-256 simple) para hashes de identificación.

## Decision

Autenticación propia con JWT (pyjwt): POST /auth/login emite token HS256 con exp, org_id y role (admin|operador); endpoints protegidos por dependency que valida el token. Contraseñas con Argon2id (argon2-cffi). Separación por organización (organization_id) en todas las queries. Números de identificación: se guardan cifrados en reposo (Fernet con clave en Secret Manager) y su huella de búsqueda es HMAC-SHA256 con clave dedicada (DOC_HMAC_KEY). Don't use SHA-256 simple para hashes de identificación; don't usar OAuth externo en el MVP.

## Consequences

Acoplamiento: los routers dependen de la dependencia get_current_user; cambiar JWT por OIDC en fase SaaS solo toca auth/. Consistencia: inmediata (sin sesiones distribuidas); revocación de token = expiración corta (12 h) + cambio de secreto para invalidar todo. Rollback: sin dependencia externa — revert de código. Observabilidad: logs de auditoría por operación (usuario, finalidad, job_id) SIN identificadores en claro; métrica de logins fallidos para alerta. Deuda técnica: MFA y SSO para fase SaaS; rotación de claves Fernet/HMAC (keyring con versiones). EARS: WHEN un endpoint protegido recibe token inválido o expirado THEN responde 401 sin filtrar información; WHEN se persiste una identificación THEN se guarda cifrada con Fernet y su índice es HMAC-SHA256.

## Alternatives

OAuth2/OIDC con Google Workspace (descartado para MVP: las alcaldías no garantizan dominio; quedará para fase SaaS); sesiones de servidor en Redis (descartado: introduciría Redis antes de ADR-007).
