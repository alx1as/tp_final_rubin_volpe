"""Profesionales externos asociados a pacientes de la profesional actual."""

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, SesionDB
from app.models import ProfesionalTratante
from app.schemas.comun import Pagina
from app.schemas.profesional_tratante import (
    ProfesionalTratanteEditar,
    ProfesionalTratanteGuardar,
    ProfesionalTratanteRespuesta,
)
from app.services.perfil import buscar_hijo, editar, guardar, paginar


router = APIRouter(
    prefix="/pacientes/{paciente_id}/profesionales-tratantes",
    tags=["Profesionales intervinientes"],
)


@router.get("", response_model=Pagina[ProfesionalTratanteRespuesta])
def listar_profesionales(
    paciente: PacienteAutorizado,
    session: SesionDB,
    pagina: ParametrosPagina,
):
    consulta = (
        select(ProfesionalTratante)
        .where(ProfesionalTratante.paciente_id == paciente.id)
        .order_by(ProfesionalTratante.fecha_inicio.desc(), ProfesionalTratante.id.desc())
    )
    return paginar(session, consulta, pagina)


@router.post("", response_model=ProfesionalTratanteRespuesta, status_code=status.HTTP_201_CREATED)
def crear_profesional(
    datos: ProfesionalTratanteGuardar,
    paciente: PacienteAutorizado,
    session: SesionDB,
):
    registro = ProfesionalTratante(paciente_id=paciente.id, **datos.model_dump())
    return guardar(session, registro)


@router.put("/{profesional_tratante_id}", response_model=ProfesionalTratanteRespuesta, deprecated=True)
def editar_profesional(
    profesional_tratante_id: int,
    datos: ProfesionalTratanteGuardar,
    paciente: PacienteAutorizado,
    session: SesionDB,
):
    registro = buscar_hijo(session, ProfesionalTratante, paciente.id, profesional_tratante_id)
    for campo, valor in datos.model_dump().items():
        setattr(registro, campo, valor)
    return guardar(session, registro)


@router.get("/{profesional_tratante_id}", response_model=ProfesionalTratanteRespuesta)
def consultar_profesional(
    profesional_tratante_id: int, paciente: PacienteAutorizado, session: SesionDB,
):
    return buscar_hijo(session, ProfesionalTratante, paciente.id, profesional_tratante_id)


@router.patch("/{profesional_tratante_id}", response_model=ProfesionalTratanteRespuesta)
def actualizar_profesional(
    profesional_tratante_id: int, datos: ProfesionalTratanteEditar,
    paciente: PacienteAutorizado, session: SesionDB,
):
    registro = buscar_hijo(session, ProfesionalTratante, paciente.id, profesional_tratante_id)
    return editar(session, registro, datos, ProfesionalTratanteGuardar)
