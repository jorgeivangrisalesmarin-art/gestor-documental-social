"""Seguridad: JWT (ADR-0004), Argon2id, HMAC de identificaciones y cifrado Fernet."""

import hashlib
import hmac as hmac_mod
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings

_hasher = PasswordHasher()

# ---------------------------------------------------------------- contraseñas


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


# ---------------------------------------------------------------- JWT


def create_token(user_id: int, organization_id: int, role: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "org_id": organization_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_exp_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Levanta jwt.InvalidTokenError/expiración si el token no es válido."""
    return jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])


# ------------------------------------------------- identificaciones (ADR-0004)


def _fernet() -> Fernet | None:
    key = get_settings().doc_encryption_key
    return Fernet(key.encode()) if key else None


def encrypt_document_id(numero: str) -> str:
    """Cifra la identificación para persistencia. Sin key configurada (dev), marca INSEGURO."""
    f = _fernet()
    if f is None:
        return f"INSEGURO-DEV:{numero}"
    return f.encrypt(numero.encode()).decode()


def decrypt_document_id(ciphertext: str) -> str:
    if ciphertext.startswith("INSEGURO-DEV:"):
        return ciphertext.removeprefix("INSEGURO-DEV:")
    f = _fernet()
    if f is None:
        raise RuntimeError("DOC_ENCRYPTION_KEY requerida para descifrar identificaciones")
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken as e:
        raise RuntimeError("Clave de cifrado no corresponde a los datos almacenados") from e


def document_hmac(tipo_documento: str, numero_documento: str) -> str:
    """Huella HMAC-SHA256 determinística para índice/deduplicación (nunca SHA-256 simple)."""
    key = get_settings().doc_hmac_key
    if not key:
        # Dev sin clave: HMAC con secreto efímero NO es válido entre reinicios;
        # usamos un valor derivado pero etiquetado para detectarlo en tests.
        key = "dev-ephemeral"
    value = f"{tipo_documento.strip().upper()}:{numero_documento.strip()}"
    return hmac_mod.new(key.encode(), value.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------- utilidades


def new_api_secret() -> str:
    return secrets.token_urlsafe(48)
