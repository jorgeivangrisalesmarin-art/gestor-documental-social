"""Descarga segura de documentos (E10, E11): siempre vía backend, nunca URL pública."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.audit import audit_event
from app.db import get_db
from app.models import Document, User
from app.storage import build_storage

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    doc = await db.scalar(
        select(Document).where(
            Document.id == document_id, Document.organization_id == user.organization_id
        )
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    storage = build_storage()
    if not storage.exists(doc.storage_path):
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    data = storage.open(doc.storage_path)

    audit_event(
        "document_downloaded",
        user_id=user.id,
        org_id=user.organization_id,
        document_id=doc.id,
        sha256=doc.sha256,
    )
    filename = f"{doc.document_type.lower()}_{doc.id}.pdf"
    return Response(
        content=data,
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
