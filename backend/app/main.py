"""Punto de entrada de la API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    DisconnectionError, IntegrityError, OperationalError, SQLAlchemyError, TimeoutError,
)

from app.api.admisiones import router as admisiones_router
from app.api.auth import router as auth_router
from app.api.escolaridades import router as escolaridades_router
from app.api.health import router as health_router
from app.api.objetivos import router as objetivos_router
from app.api.observaciones import router as observaciones_router
from app.api.pacientes import router as pacientes_router
from app.api.profesionales_tratantes import router as profesionales_tratantes_router
from app.api.sesiones import router as sesiones_router
from app.core.config import Settings, load_settings
from app.core.origins import ValidateOriginMiddleware
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
    application.include_router(auth_router, prefix="/api")
    application.include_router(pacientes_router, prefix="/api")
    application.include_router(admisiones_router, prefix="/api")
    application.include_router(escolaridades_router, prefix="/api")
    application.include_router(profesionales_tratantes_router, prefix="/api")
    application.include_router(objetivos_router, prefix="/api")
    application.include_router(sesiones_router, prefix="/api")
    application.include_router(observaciones_router, prefix="/api")

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        # FastAPI incluye entradas en errores de validación por defecto. Nunca
        # devolver contraseñas, cookies u otros valores recibidos en el cuerpo.
        return JSONResponse(status_code=422, content={"detail": [
            {key: item[key] for key in ("type", "loc", "msg")}
            for item in error.errors()
        ]})

    @application.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, error: SQLAlchemyError):
        if isinstance(error, (OperationalError, DisconnectionError, TimeoutError)):
            return JSONResponse(status_code=503, content={"detail": "Base de datos no disponible"})
        if isinstance(error, IntegrityError):
            return JSONResponse(status_code=409, content={"detail": "Conflicto de integridad"})
        return JSONResponse(status_code=500, content={"detail": "Error interno"})

    application.add_middleware(
        ValidateOriginMiddleware, allowed_origins=configuration.allowed_origins,
    )
    # CORS envuelve la guardia para agregar sus encabezados también en errores.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=configuration.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    return application
