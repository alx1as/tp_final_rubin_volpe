"""Punto de entrada de la API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import Settings, load_settings
from app.db.session import build_engine


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings if settings is not None else load_settings()
    engine = build_engine(configuration)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="Seguimiento psicopedagógico", version="0.1.0", lifespan=lifespan
    )
    application.state.settings = configuration
    application.state.engine = engine
    application.include_router(health_router, prefix="/api")
    return application
