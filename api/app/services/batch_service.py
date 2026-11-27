"""Servicio de consulta masiva (E13–E16): CSV/Excel → lote → procesamiento in-process.

ADR-0007: sin Redis/Celery en el MVP; estados persistidos en PostgreSQL y
concurrencia limitada por semáforo. La interfaz permite swap a worker en fase 2.
"""

import asyncio
import csv
import io
import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import audit_event
from app.db import SessionLocal
from app.models import Batch, BatchStatus, JobStatus, LookupJob, User
from app.security import decrypt_document_id, document_hmac, encrypt_document_id
from app.services.lookup_service import process_job

REQUIRED_COLUMNS = [
    "tipo_documento",
    "numero_documento",
    "adres",
    "sisben_iv",
    "rui",
    "autorizacion_confirmada",
    "referencia_autorizacion",
]

_TRUE = {"true", "1", "si", "sí", "x", "yes"}
MAX_BATCH = 100  # MVP: lotes pequeños del piloto

DOCTYPES_BY_FLAG = [
    ("adres", "ADRES_AFFILIATION_REPORT"),
    ("sisben_iv", "SISBEN_IV_CERTIFICATE"),
    ("rui", "RUI_CERTIFICATE"),
]


def parse_file(data: bytes, filename: str) -> list[dict[str, str]]:
    """Parsea CSV (con BOM) o XLSX a lista de dicts con claves normalizadas."""
    name = filename.lower()
    if name.endswith((".xlsx", ".xls")):
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [str(h).strip().lower() for h in rows[0]]
        return [
            dict(zip(headers, (str(c).strip() if c is not None else "" for c in r), strict=False))
            for r in rows[1:]
        ]

    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    return [
        {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in reader
    ]


def validate_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Valida columnas y valores (E13). Retorna (validos, errores)."""
    errors: list[dict] = []
    valid: list[dict] = []

    if rows:
        headers = set(rows[0].keys())
        missing = [c for c in REQUIRED_COLUMNS if c not in headers]
        if missing:
            raise ValueError(f"Faltan columnas obligatorias: {', '.join(missing)}")

    for i, row in enumerate(rows, start=2):  # fila 1 = encabezados
        row_errors: list[str] = []
        tipo = row.get("tipo_documento", "").upper()
        numero = row.get("numero_documento", "")
        if not tipo or not numero:
            row_errors.append("tipo_documento y numero_documento son obligatorios")
        if numero and not numero.isdigit():
            row_errors.append("numero_documento debe ser numérico")

        requested = [dtype for flag, dtype in DOCTYPES_BY_FLAG if _to_bool(row.get(flag))]
        if not requested:
            row_errors.append("Debe solicitar al menos un documento (adres/sisben_iv/rui)")

        autorizada = _to_bool(row.get("autorizacion_confirmada"))
        ref = row.get("referencia_autorizacion", "")
        if autorizada and not ref:
            row_errors.append("autorizacion_confirmada requiere referencia_autorizacion")

        if row_errors:
            errors.append(
                {
                    "fila": i,
                    "errores": row_errors,
                    "numero_documento": f"***{numero[-3:]}" if numero else "",
                }
            )
        else:
            valid.append({**row, "_fila": i, "_autorizada": autorizada, "_tipos": requested})
    return valid, errors


def _to_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in _TRUE


async def create_batch(
    db: AsyncSession, user: User, filename: str, rows: list[dict], errors: list[dict]
) -> Batch:
    if len(rows) > MAX_BATCH:
        raise ValueError(f"El MVP procesa lotes de hasta {MAX_BATCH} registros")
    batch = Batch(
        organization_id=user.organization_id,
        created_by=user.id,
        filename=filename[:255],
        total_records=len(rows) + len(errors),
        status=BatchStatus.VALIDATING,
    )
    db.add(batch)
    await db.flush()

    for row in rows:
        doc_hmac = document_hmac(row.get("tipo_documento", ""), row.get("numero_documento", ""))
        # El ciphertext guarda "TIPO:numero" para recuperar el tipo al procesar
        ciphertext = encrypt_document_id(
            f"{row.get('tipo_documento', '').upper()}:{row.get('numero_documento', '')}"
        )
        if not row["_autorizada"]:
            # E15: sin autorización se registra el motivo y NO se procesa
            db.add(
                LookupJob(
                    organization_id=user.organization_id,
                    created_by=user.id,
                    batch_id=batch.id,
                    document_type=",".join(row["_tipos"]),
                    document_ciphertext=ciphertext,
                    document_hmac=doc_hmac,
                    provider="excluido",
                    status=JobStatus.EXCLUDED,
                    error_code="SIN_AUTORIZACION",
                )
            )
            continue
        for dtype in row["_tipos"]:
            db.add(
                LookupJob(
                    organization_id=user.organization_id,
                    created_by=user.id,
                    batch_id=batch.id,
                    document_type=dtype,
                    document_ciphertext=ciphertext,
                    document_hmac=doc_hmac,
                    provider="pendiente",
                    status=JobStatus.PENDING,
                )
            )
    await db.commit()
    audit_event(
        "batch_created",
        user_id=user.id,
        org_id=user.organization_id,
        batch_id=batch.id,
        total=batch.total_records,
        excluded=sum(1 for r in rows if not r["_autorizada"]),
        validation_errors=len(errors),
    )
    return batch


async def process_batch(db: AsyncSession, user: User, batch: Batch) -> Batch:
    """Procesa los jobs pendientes del lote con concurrencia limitada (E14)."""
    if batch.status in (BatchStatus.PROCESSING, BatchStatus.COMPLETED, BatchStatus.PARTIAL_SUCCESS):
        raise PermissionError(f"El lote ya está en estado {batch.status.value}")

    result = await db.scalars(
        select(LookupJob).where(
            LookupJob.batch_id == batch.id,
            LookupJob.organization_id == user.organization_id,
            LookupJob.status == JobStatus.PENDING,
        )
    )
    jobs = list(result)
    batch.status = BatchStatus.PROCESSING
    await db.commit()

    sem = asyncio.Semaphore(3)  # MVP: concurrencia conservadora contra el proveedor

    async def _run(job_id: int) -> None:
        # Cada job usa SU PROPIA sesión: la sesión de la request no tolera
        # commits concurrentes; el resultado queda persistido por process_job.
        async with sem, SessionLocal() as job_db:
            job = await job_db.get(LookupJob, job_id)
            if job is None or job.status != JobStatus.PENDING:
                return
            # El ciphertext guarda "TIPO:numero" — se descifra SOLO en memoria, jamás en logs
            tipo, numero = decrypt_document_id(job.document_ciphertext).split(":", 1)
            await process_job(job_db, job, tipo_documento=tipo, numero_documento=numero)

    await asyncio.gather(*(_run(j.id) for j in jobs))

    # Recalcular contadores desde BD (fuente de verdad). populate_existing
    # refresca los jobs del identity map (los estados los committearon las
    # sesiones de los jobs) sin expirar objetos usados en contexto síncrono.
    await db.refresh(batch)
    all_jobs = await db.scalars(
        select(LookupJob)
        .where(LookupJob.batch_id == batch.id)
        .execution_options(populate_existing=True)
    )
    jobs_all = list(all_jobs)
    done = [j for j in jobs_all if j.status not in (JobStatus.PENDING, JobStatus.PROCESSING)]
    ok = sum(1 for j in done if j.status in (JobStatus.COMPLETED, JobStatus.NOT_FOUND))
    batch.processed_records = len(done)
    batch.success_count = ok
    batch.error_count = len(done) - ok
    if any(j.status == JobStatus.PROCESSING for j in jobs_all):
        batch.status = BatchStatus.PROCESSING
    elif not any(j.status == JobStatus.FAILED for j in done):
        batch.status = BatchStatus.COMPLETED
    else:
        batch.status = BatchStatus.PARTIAL_SUCCESS
    await db.commit()
    audit_event(
        "batch_processed", user_id=user.id, org_id=batch.organization_id,
        batch_id=batch.id, status=batch.status.value,
    )
    return batch


def batch_public_dict(batch: Batch, jobs: list[LookupJob]) -> dict:
    return {
        "id": batch.id,
        "filename": batch.filename,
        "status": batch.status.value,
        "total_records": batch.total_records,
        "processed_records": batch.processed_records,
        "success_count": batch.success_count,
        "error_count": batch.error_count,
        "created_at": batch.created_at.isoformat() if batch.created_at else None,
        "jobs": [
            {
                "id": j.id,
                "document_type": j.document_type,
                "status": j.status.value,
                "error_code": j.error_code,
                "source": j.source,
            }
            for j in jobs
        ],
    }


def jobs_json(jobs: list[LookupJob]) -> str:
    return json.dumps([j.id for j in jobs])


def utcnow() -> datetime:
    return datetime.now(UTC)
