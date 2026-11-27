"""Entrypoint de la API del Gestor Documental Social (FastAPI, ADR-0001).

Cloud Run exige escuchar en $PORT; uvicorn lo resuelve en el Dockerfile.
Migraciones: dev usa create_all; producción usa Alembic (T010, ADR-002).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, batches, documents, health, lookups
from app.config import get_settings
from app.db import Base, engine
from app.seed import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev/MVP: crear esquema y organización inicial; en prod lo hace Alembic (T010)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Gestor Documental Social — API",
        version="0.1.0",
        description="Motor documental ADRES / SISBÉN IV / RUI con proveedores intercambiables",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.web_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(lookups.router)
    app.include_router(batches.router)
    app.include_router(documents.router)
    return app


app = create_app()
