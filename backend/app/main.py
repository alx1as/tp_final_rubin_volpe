"""Punto de entrada de la API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import Settings, load_settings
from app.db.session import build_engine

from fastapi.middleware.cors import CORSMiddleware

from app.api.pacientes import router as pacientes_router
from app.api.admisiones import router as admisiones_router

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
    application.include_router(pacientes_router, prefix="/api")
    application.include_router(admisiones_router, prefix="/api")

        # Permitir solicitudes del frontend durante el desarrollo local.
        # más adelante configuramos los orígenes permitidos para producción.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application
