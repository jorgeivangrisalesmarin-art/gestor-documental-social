---
id: "ADR-0006"
title: "ADR-006: Almacenamiento documental — FS local en dev, GCS privado con URLs firmadas en prod"
status: accepted
date: 2026-11-26
deciders: ['Jorge']
tags: ['documentos', 'gcs', 'storage', 'seguridad']
policy:
  boundaries: {'rules': [{'forbid': 'frontend -> bucket GCS directo sin URL firmada emitida por el backend'}]}approval_date: 2026-11-26
approval_notes: "Aprobado por Jorge (2026-11-26), plan T002."

---

## Context

Los documentos obtenidos legítimamente (reportes/certificados) son datos sensibles. El brief exige no exponer documentos por enlaces públicos, registrar sha256 y conservar trazabilidad de fuente y fecha. En desarrollo local no hay GCS; en producción sí.

## Decision

Abstracción DocumentStorage con dos implementaciones: LocalFilesystemStorage (desarrollo: DOCUMENT_STORAGE_PATH, nombres seguros generados UUID + extensión validada) y GcsStorage (producción: bucket privado, sin acceso público, KMS gestionado por Google). La descarga SIEMPRE pasa por el backend: GET /documents/{id}/download valida sesión y organiza el streaming; en GCS se genera URL firmada V4 de corta duración (<=5 min) solo tras autorización. Don't exponer buckets públicos; don't construir URLs de descarga en el frontend.

## Consequences

Acoplamiento: el motor documental depende de la interfaz DocumentStorage, no de GCS. Consistencia: registro en BD (documents.sha256, storage_path) es la fuente de verdad; el archivo huérfano sin registro se considera inválido. Rollback: los objetos son inmutables por nombre-UUID; borrar un documento = estado en BD + tarea de limpieza. Observabilidad: cada descarga audita usuario y job; métrica de descargas y errores 404 de objetos. Deuda técnica: política de conservación/eliminación (retención) y CMEK para fase SaaS; antivirus/validación MIME profunda (magic bytes) al subir documentos externos. EARS: WHEN se almacena un documento THEN se calcula sha256 y se registra fuente+fecha+estado; WHEN un usuario sin sesión pide descarga THEN responde 401 sin revelar existencia del objeto.

## Alternatives

S3 compatible (MinIO) local para paridad con prod (descartado para MVP: añade un servicio más en docker-compose; la abstracción permite añadirlo en fase 2); servir archivos desde el proceso API siempre (aceptable en MVP; URL firmada reduce carga en fase 2).
