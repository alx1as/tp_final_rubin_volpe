"""Sesiones de seguimiento de un paciente autorizado."""

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, SesionAutorizada, SesionDB
from app.models import Sesion
from app.schemas.comun import Pagina
from app.schemas.sesion import SesionCrear, SesionEditar, SesionRespuesta
from app.services.perfil import editar, guardar, paginar


router = APIRouter(prefix="/pacientes/{paciente_id}/sesiones", tags=["Sesiones"])


@router.get("", response_model=Pagina[SesionRespuesta])
def listar_sesiones(paciente: PacienteAutorizado, session: SesionDB, pagina: ParametrosPagina):
    consulta = select(Sesion).where(Sesion.paciente_id == paciente.id).order_by(Sesion.fecha.desc(), Sesion.id.desc())
    return paginar(session, consulta, pagina)


@router.post("", response_model=SesionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_sesion(datos: SesionCrear, paciente: PacienteAutorizado, session: SesionDB):
    return guardar(session, Sesion(paciente_id=paciente.id, **datos.model_dump()))


@router.get("/{sesion_id}", response_model=SesionRespuesta)
def consultar_sesion(sesion: SesionAutorizada):
    return sesion


@router.patch("/{sesion_id}", response_model=SesionRespuesta)
def editar_sesion(datos: SesionEditar, sesion: SesionAutorizada, session: SesionDB):
    return editar(session, sesion, datos, SesionCrear)
