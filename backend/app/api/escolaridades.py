"""Listar, crear y editar períodos escolares del paciente."""

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, SesionDB
from app.models import Escolaridad
from app.schemas.comun import Pagina
from app.schemas.escolaridad import EscolaridadEditar, EscolaridadGuardar, EscolaridadRespuesta
from app.services.perfil import buscar_hijo, editar, guardar, paginar


router = APIRouter(
    prefix="/pacientes/{paciente_id}/escolaridades", tags=["Escolaridad"]
)


@router.get("", response_model=Pagina[EscolaridadRespuesta])
def listar_escolaridades(
    paciente: PacienteAutorizado, session: SesionDB, pagina: ParametrosPagina,
):
    consulta = (
        select(Escolaridad)
        .where(Escolaridad.paciente_id == paciente.id)
        .order_by(Escolaridad.fecha_inicio.desc(), Escolaridad.id.desc())
    )
    return paginar(session, consulta, pagina)


@router.post("", response_model=EscolaridadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_escolaridad(
    datos: EscolaridadGuardar,
    paciente: PacienteAutorizado,
    session: SesionDB,
):
    registro = Escolaridad(paciente_id=paciente.id, **datos.model_dump())
    return guardar(session, registro)


@router.put("/{escolaridad_id}", response_model=EscolaridadRespuesta, deprecated=True)
def editar_escolaridad(
    escolaridad_id: int,
    datos: EscolaridadGuardar,
    paciente: PacienteAutorizado,
    session: SesionDB,
):
    registro = buscar_hijo(session, Escolaridad, paciente.id, escolaridad_id)
    for campo, valor in datos.model_dump().items():
        setattr(registro, campo, valor)
    return guardar(session, registro)


@router.get("/{escolaridad_id}", response_model=EscolaridadRespuesta)
def consultar_escolaridad(escolaridad_id: int, paciente: PacienteAutorizado, session: SesionDB):
    return buscar_hijo(session, Escolaridad, paciente.id, escolaridad_id)


@router.patch("/{escolaridad_id}", response_model=EscolaridadRespuesta)
def actualizar_escolaridad(
    escolaridad_id: int, datos: EscolaridadEditar,
    paciente: PacienteAutorizado, session: SesionDB,
):
    registro = buscar_hijo(session, Escolaridad, paciente.id, escolaridad_id)
    return editar(session, registro, datos, EscolaridadGuardar)
