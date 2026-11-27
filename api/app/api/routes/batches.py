"""Rutas de consulta masiva (E13–E16): carga CSV/Excel, validación, procesamiento."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Batch, LookupJob, User
from app.services.batch_service import (
    batch_public_dict,
    create_batch,
    parse_file,
    process_batch,
    validate_rows,
)

router = APIRouter(prefix="/api/v1/batches", tags=["batches"])


async def _batch_for_org(db: AsyncSession, org_id: int, batch_id: int) -> Batch:
    batch = await db.get(Batch, batch_id)
    if batch is None or batch.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return batch


@router.post("", status_code=201)
async def upload_batch(
    file: UploadFile, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=422, detail="Solo se aceptan archivos .csv o .xlsx")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=422, detail="Archivo demasiado grande (máx 5 MB)")

    try:
        rows = parse_file(data, file.filename)
        valid, errors = validate_rows(rows)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    batch = await create_batch(db, user, file.filename, valid, errors)
    out = batch_public_dict(
        batch,
        list(
            await db.scalars(select(LookupJob).where(LookupJob.batch_id == batch.id))
        ),
    )
    out["validation_errors"] = errors
    return out


@router.post("/{batch_id}/process")
async def start_batch(
    batch_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    batch = await _batch_for_org(db, user.organization_id, batch_id)
    try:
        batch = await process_batch(db, user, batch)
    except PermissionError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    jobs = list(await db.scalars(select(LookupJob).where(LookupJob.batch_id == batch.id)))
    return batch_public_dict(batch, jobs)


@router.get("/{batch_id}")
async def batch_status(
    batch_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    batch = await _batch_for_org(db, user.organization_id, batch_id)
    jobs = list(await db.scalars(select(LookupJob).where(LookupJob.batch_id == batch.id)))
    return batch_public_dict(batch, jobs)


@router.get("")
async def list_batches(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    result = await db.scalars(
        select(Batch)
        .where(Batch.organization_id == user.organization_id)
        .order_by(Batch.created_at.desc())
        .limit(100)
    )
    return [batch_public_dict(b, []) for b in result]
