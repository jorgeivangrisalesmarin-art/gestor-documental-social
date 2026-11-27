"""Seed inicial (E4): organización + usuario admin desde variables de entorno."""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import SessionLocal
from app.models import Organization, Role, User
from app.security import hash_password

logger = logging.getLogger("gds.seed")


async def seed_initial_data() -> None:
    async with SessionLocal() as db:
        await _seed(db)


async def _seed(db: AsyncSession) -> None:
    settings = get_settings()
    org_count = await db.scalar(select(func.count()).select_from(Organization))
    if org_count == 0:
        org = Organization(name="Organización Piloto", nit="000000000-0")
        db.add(org)
        await db.flush()
    else:
        org = (await db.scalars(select(Organization).limit(1))).first()

    admin = await db.scalar(select(User).where(User.email == settings.seed_admin_email.lower()))
    if admin is None:
        db.add(
            User(
                organization_id=org.id,
                email=settings.seed_admin_email.lower(),
                password_hash=hash_password(settings.seed_admin_password),
                role=Role.admin,
            )
        )
        await db.commit()
        logger.info("Seed: organización piloto + admin creados")
