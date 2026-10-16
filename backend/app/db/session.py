"""Engine sin conexión anticipada y una sesión por solicitud."""

from collections.abc import Generator

from fastapi import Request
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.core.config import Settings


def build_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=3,
        connect_args={"connect_timeout": 3, "options": "-c statement_timeout=3000"},
        hide_parameters=True,
    )


def get_session(request: Request) -> Generator[Session]:
    # Cierra la sesión y revierte transacciones pendientes incluso ante errores.
    with Session(request.app.state.engine) as session:
        yield session
