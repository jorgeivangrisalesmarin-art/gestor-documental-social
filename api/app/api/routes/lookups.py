"""Rutas de consulta individual (E5, E9) e historial."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.services.lookup_service import (
    create_and_run_lookups,
    get_job_for_org,
    job_public_dict,
    list_jobs_for_org,
)

router = APIRouter(prefix="/api/v1/lookups", tags=["lookups"])


class LookupCreate(BaseModel):
    tipo_documento: str = Field(pattern="^(CC|TI|CE|PA|NIT)$")
    numero_documento: str = Field(min_length=5, max_length=15, pattern=r"^\d+$")
    document_types: list[str] = Field(min_length=1, max_length=3)
    finalidad: str = Field(min_length=5, max_length=200)
    autorizacion_confirmada: bool


@router.post("", status_code=201)
async def create_lookup(
    body: LookupCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    try:
        jobs = await create_and_run_lookups(
            db,
            user,
            tipo_documento=body.tipo_documento,
            numero_documento=body.numero_documento,
            document_types=body.document_types,
            finalidad=body.finalidad,
            autorizacion_confirmada=body.autorizacion_confirmada,
        )
    except PermissionError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return [job_public_dict(j) for j in jobs]


@router.get("")
async def list_lookups(
    limit: int = 50, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    jobs = await list_jobs_for_org(db, user.organization_id, limit=limit)
    return [job_public_dict(j) for j in jobs]


@router.get("/{job_id}")
async def get_lookup(
    job_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    job = await get_job_for_org(db, user.organization_id, job_id)
    if job is None:
        # 404 sin filtrar existencia entre organizaciones (E3)
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return job_public_dict(job)
