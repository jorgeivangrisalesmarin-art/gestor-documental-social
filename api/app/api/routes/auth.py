"""Rutas de autenticación (E1, E4)."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.audit import audit_event
from app.db import get_db
from app.models import User
from app.security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    email: str
    role: str
    organization_id: int


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == body.email.lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        # Mensaje genérico: no revelar si el email existe
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    audit_event("login", user_id=user.id, org_id=user.organization_id)
    return TokenResponse(access_token=create_token(user.id, user.organization_id, user.role.value))


@router.get("/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=user.id, email=user.email, role=user.role.value, organization_id=user.organization_id
    )
