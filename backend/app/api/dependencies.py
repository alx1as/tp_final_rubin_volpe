"""Dependencias compartidas de acceso a datos y autenticación."""

from typing import Annotated
from dataclasses import dataclass

from fastapi import Cookie, Depends, Query
from sqlmodel import Session

from app.db.session import get_session
from app.models import Paciente, Profesional, Sesion, SesionAutenticacion
from app.schemas.comun import Paginacion
from app.services.auth import validar_sesion
from app.services.perfil import buscar_hijo, buscar_paciente


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


def obtener_paciente_autorizado(
    paciente_id: int, session: SesionDB, profesional: ProfesionalActual,
) -> Paciente:
    return buscar_paciente(session, profesional.id, paciente_id)


PacienteAutorizado = Annotated[Paciente, Depends(obtener_paciente_autorizado)]


def obtener_sesion_autorizada(
    sesion_id: int, paciente: PacienteAutorizado, session: SesionDB,
) -> Sesion:
    return buscar_hijo(session, Sesion, paciente.id, sesion_id)


SesionAutorizada = Annotated[Sesion, Depends(obtener_sesion_autorizada)]


def obtener_paginacion(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Paginacion:
    return Paginacion(offset=offset, limit=limit)


ParametrosPagina = Annotated[Paginacion, Depends(obtener_paginacion)]
