"""Servicio de consulta individual (E5–E9, E12): jobs por tipo documental."""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import audit_event
from app.models import JobStatus, LookupJob, User
from app.providers import build_providers
from app.providers.base import DocumentType, LookupInput, ProviderError, ResultStatus
from app.security import document_hmac, encrypt_document_id

# Errores de proveedor que NO se reintentan (E6) mapean a estos error_code:
_FATAL_CODES = {
    "PROVIDER_UNAUTHORIZED",
    "PROVIDER_PAYMENT_REQUIRED",
    "PROVIDER_NOT_FOUND",
}


def _parse_types(types: list[str]) -> list[DocumentType]:
    valid = {t.value: t for t in DocumentType}
    unknown = [t for t in types if t not in valid]
    if unknown:
        raise ValueError(f"Tipos documentales desconocidos: {', '.join(unknown)}")
    return [valid[t] for t in types]


async def create_and_run_lookups(
    db: AsyncSession,
    user: User,
    tipo_documento: str,
    numero_documento: str,
    document_types: list[str],
    finalidad: str,
    autorizacion_confirmada: bool,
) -> list[LookupJob]:
    """Crea un job por tipo documental y lo procesa (flujo individual, inline)."""
    if not autorizacion_confirmada:
        raise PermissionError("Se requiere autorizacion_confirmada=true (finalidad registrada)")
    if not finalidad or len(finalidad) < 5:
        raise ValueError("La finalidad de la consulta es obligatoria")

    types = _parse_types(document_types)
    providers = build_providers()
    doc_hmac = document_hmac(tipo_documento, numero_documento)
    jobs: list[LookupJob] = []

    for dtype in types:
        job = LookupJob(
            organization_id=user.organization_id,
            created_by=user.id,
            document_type=dtype.value,
            document_ciphertext=encrypt_document_id(numero_documento),
            document_hmac=doc_hmac,
            provider=getattr(providers[dtype], "name", "desconocido"),
            status=JobStatus.PENDING,
        )
        db.add(job)
        jobs.append(job)
    await db.commit()

    for job in jobs:
        await process_job(db, job, tipo_documento=tipo_documento, numero_documento=numero_documento)

    audit_event(
        "lookup_individual",
        user_id=user.id,
        org_id=user.organization_id,
        finalidad=finalidad[:120],
        document_hmac=doc_hmac,
        document_types=[j.document_type for j in jobs],
        document_types_count=len(jobs),
    )
    return jobs


async def process_job(
    db: AsyncSession, job: LookupJob, *, tipo_documento: str, numero_documento: str
) -> LookupJob:
    providers = build_providers()
    dtype = DocumentType(job.document_type)
    provider = providers[dtype]
    job.status = JobStatus.PROCESSING
    job.started_at = datetime.now(UTC)
    await db.commit()

    try:
        result = await provider.lookup(
            LookupInput(
                document_type=dtype,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
            )
        )
    except ProviderError as e:
        job.status = JobStatus.FAILED
        job.error_code = e.code
        job.completed_at = datetime.now(UTC)
        audit_event(
            "lookup_failed", job_id=job.id, org_id=job.organization_id, error_code=e.code
        )
        await db.commit()
        return job

    job.result_json = json.dumps(
        {
            "status": result.status.value,
            "data": result.data,
            "source": result.source,
            "consulted_at": result.consulted_at.isoformat(),
            "live": bool(getattr(provider, "live", False)),
        },
        ensure_ascii=False,
    )
    job.source = result.source
    job.status = _status_for_result(result.status)
    job.completed_at = datetime.now(UTC)
    audit_event(
        "lookup_completed",
        job_id=job.id,
        org_id=job.organization_id,
        provider=job.provider,
        status=job.status.value,
        live=getattr(provider, "live", False),
    )
    await db.commit()
    return job


def _status_for_result(status: ResultStatus) -> JobStatus:
    if status == ResultStatus.NOT_FOUND:
        return JobStatus.NOT_FOUND
    if status == ResultStatus.MANUAL_ACTION_REQUIRED:
        return JobStatus.MANUAL_ACTION_REQUIRED
    return JobStatus.COMPLETED  # DATA_RETRIEVED y DOCUMENT_PENDING completan la consulta


async def get_job_for_org(db: AsyncSession, org_id: int, job_id: int) -> LookupJob | None:
    return await db.scalar(
        select(LookupJob).where(LookupJob.id == job_id, LookupJob.organization_id == org_id)
    )


async def list_jobs_for_org(db: AsyncSession, org_id: int, limit: int = 50) -> list[LookupJob]:
    result = await db.scalars(
        select(LookupJob)
        .where(LookupJob.organization_id == org_id)
        .order_by(LookupJob.created_at.desc())
        .limit(min(limit, 200))
    )
    return list(result)


def job_public_dict(job: LookupJob) -> dict:
    """Serializa el job SIN exponer ciphertext ni datos de otras organizaciones."""
    result = json.loads(job.result_json) if job.result_json else None
    return {
        "id": job.id,
        "batch_id": job.batch_id,
        "document_type": job.document_type,
        "provider": job.provider,
        "status": job.status.value if job.status else None,
        "source": job.source,
        "error_code": job.error_code,
        "result": result,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }
