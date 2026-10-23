"""Dependencias compartidas de acceso a datos y autenticación."""

from typing import Annotated
from dataclasses import dataclass

from fastapi import Cookie, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models import Profesional, SesionAutenticacion
from app.services.auth import validar_sesion


SesionDB = Annotated[Session, Depends(get_session)]


@dataclass(frozen=True, repr=False)
class ContextoAutenticacion:
    sesion: SesionAutenticacion
    profesional: Profesional


def obtener_acceso(
    session: SesionDB,
    sesion: Annotated[str | None, Cookie()] = None,
) -> ContextoAutenticacion:
    actual, profesional = validar_sesion(sesion, session)
    return ContextoAutenticacion(actual, profesional)


AccesoActual = Annotated[ContextoAutenticacion, Depends(obtener_acceso)]


def obtener_profesional_actual(acceso: AccesoActual) -> Profesional:
    return acceso.profesional


ProfesionalActual = Annotated[Profesional, Depends(obtener_profesional_actual)]
