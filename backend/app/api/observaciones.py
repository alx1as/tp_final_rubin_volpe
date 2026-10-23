"""Observaciones de una sesión autorizada del paciente de la ruta."""

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import ParametrosPagina, SesionAutorizada, SesionDB
from app.models import Observacion
from app.schemas.comun import Pagina
from app.schemas.observacion import ObservacionCrear, ObservacionEditar, ObservacionRespuesta
from app.services.perfil import paginar
from app.services.seguimiento import buscar_observacion, crear_observacion, editar_observacion


router = APIRouter(
    prefix="/pacientes/{paciente_id}/sesiones/{sesion_id}/observaciones",
    tags=["Observaciones"],
)


@router.get("", response_model=Pagina[ObservacionRespuesta])
def listar_observaciones(sesion: SesionAutorizada, session: SesionDB, pagina: ParametrosPagina):
    consulta = select(Observacion).where(Observacion.sesion_id == sesion.id).order_by(Observacion.id)
    return paginar(session, consulta, pagina)


@router.post("", response_model=ObservacionRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_observacion(datos: ObservacionCrear, sesion: SesionAutorizada, session: SesionDB):
    return crear_observacion(session, sesion.id, sesion.paciente_id, datos)


@router.get("/{observacion_id}", response_model=ObservacionRespuesta)
def consultar_observacion(observacion_id: int, sesion: SesionAutorizada, session: SesionDB):
    return buscar_observacion(session, sesion.id, observacion_id)


@router.patch("/{observacion_id}", response_model=ObservacionRespuesta)
def actualizar_observacion(
    observacion_id: int, datos: ObservacionEditar, sesion: SesionAutorizada, session: SesionDB,
):
    registro = buscar_observacion(session, sesion.id, observacion_id)
    return editar_observacion(session, registro, sesion.paciente_id, datos)
