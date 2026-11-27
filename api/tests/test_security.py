"""Pruebas de seguridad: JWT, Argon2id, HMAC determinista y Fernet (ADR-0004, E12)."""

import pytest

from app.security import (
    create_token,
    decode_token,
    decrypt_document_id,
    document_hmac,
    encrypt_document_id,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("mi-clave-segura-123")
    assert h != "mi-clave-segura-123"
    assert verify_password("mi-clave-segura-123", h)
    assert not verify_password("otra-clave", h)


def test_jwt_roundtrip():
    token = create_token(user_id=7, organization_id=2, role="admin")
    payload = decode_token(token)
    assert payload["sub"] == "7"
    assert payload["org_id"] == 2
    assert payload["role"] == "admin"


def test_jwt_invalido_rechazado():
    import jwt as pyjwt

    with pytest.raises(pyjwt.PyJWTError):
        decode_token("token-forjado")


def test_hmac_determinista_y_distinto():
    a = document_hmac("CC", "123456789")
    b = document_hmac("CC", " 123456789 ")  # espacios se normalizan
    c = document_hmac("TI", "123456789")
    assert a == b
    assert a != c
    assert len(a) == 64


def test_fernet_roundtrip():
    cifrado = encrypt_document_id("1020304050")
    assert "1020304050" not in cifrado
    assert decrypt_document_id(cifrado) == "1020304050"


def test_tipo_numero_junto_roundtrip():
    """Formato del lote: ciphertext guarda TIPO:numero (batch_service)."""
    cifrado = encrypt_document_id("TI:98765432")
    assert decrypt_document_id(cifrado) == "TI:98765432"
