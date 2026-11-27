"""Abstracción DocumentStorage (ADR-0006): FS local en MVP; GCS en producción."""

import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path

# Whitelist estricta de tipos permitidos (E10): extensión -> mime
ALLOWED = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".csv": "text/csv",
}


@dataclass
class StoredFile:
    storage_path: str
    sha256: str
    mime_type: str
    size: int


class DocumentStorage:
    """Interfaz: guardar y leer archivos de forma segura (sin nombres de usuario)."""

    def save(self, data: bytes, ext: str) -> StoredFile: ...
    def open(self, storage_path: str) -> bytes: ...
    def exists(self, storage_path: str) -> bool: ...


class LocalFilesystemStorage(DocumentStorage):
    """Desarrollo/MVP: archivos en DOCUMENT_STORAGE_PATH con nombre UUID."""

    def __init__(self, base_path: str) -> None:
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, ext: str) -> StoredFile:
        ext = ext.lower()
        if ext not in ALLOWED:
            raise ValueError(f"Extensión no permitida: {ext}")
        name = f"{uuid.uuid4()}{ext}"
        path = self.base / name
        path.write_bytes(data)
        return StoredFile(
            storage_path=str(path),
            sha256=hashlib.sha256(data).hexdigest(),
            mime_type=ALLOWED[ext],
            size=len(data),
        )

    def open(self, storage_path: str) -> bytes:
        path = Path(storage_path)
        # Anti path-traversal: el archivo debe residir dentro de base
        path.resolve().relative_to(self.base.resolve())
        return path.read_bytes()

    def exists(self, storage_path: str) -> bool:
        return Path(storage_path).exists()


class GcsStorage(DocumentStorage):
    """Producción (ADR-0006): bucket privado GCS + URLs firmadas V4. Stub fase despliegue."""

    def __init__(self, bucket: str) -> None:
        raise NotImplementedError("GcsStorage se activa en T010 (despliegue GCP)")


def build_storage() -> DocumentStorage:
    from app.config import get_settings

    return LocalFilesystemStorage(get_settings().document_storage_path)
