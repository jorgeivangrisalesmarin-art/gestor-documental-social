"""Motor de base de datos y sesión asíncrona (SQLAlchemy 2)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    settings = get_settings()
    # Con Pool para sqlite async; pre_ping para Postgres en Cloud Run (conexiones frías)
    return create_async_engine(settings.database_url, pool_pre_ping=True)


engine = _make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
