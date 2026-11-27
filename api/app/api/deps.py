"""Dependencias FastAPI: usuario autenticado y sesión de BD (E2, E3)."""

import jwt as pyjwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User
from app.security import decode_token


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = auth.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado") from None

    user = await db.get(User, int(payload["sub"]))
    if user is None or user.organization_id != payload.get("org_id"):
        # 401 sin revelar existencia (E2/E3)
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return user


def require_role(*roles: str):
    async def _checker(user: User = Depends(get_current_user)) -> User:
        if roles and user.role.value not in roles:
            raise HTTPException(status_code=403, detail="Rol insuficiente")
        return user

    return _checker
