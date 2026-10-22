"""Profesionales externos asociados a pacientes de la profesional actual."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.pacientes import ProfesionalActual, SesionDB
from app.models import Paciente, ProfesionalTratante
from app.schemas.profesional_tratante import (
    ProfesionalTratanteGuardar,
    ProfesionalTratanteRespuesta,
)


router = APIRouter(
    prefix="/pacientes/{paciente_id}/profesionales-tratantes",
    tags=["Profesionales intervinientes"],
)


def verificar_paciente(paciente_id: int, session: SesionDB, profesional: ProfesionalActual) -> None:
    paciente = session.get(Paciente, paciente_id)
    if paciente is None or paciente.profesional_id != profesional.id:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")


@router.get("", response_model=list[ProfesionalTratanteRespuesta])
def listar_profesionales(
    paciente_id: int,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    return session.exec(
        select(ProfesionalTratante)
        .where(ProfesionalTratante.paciente_id == paciente_id)
        .order_by(ProfesionalTratante.fecha_inicio.desc(), ProfesionalTratante.id.desc())
    ).all()


@router.post("", response_model=ProfesionalTratanteRespuesta, status_code=status.HTTP_201_CREATED)
def crear_profesional(
    paciente_id: int,
    datos: ProfesionalTratanteGuardar,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    registro = ProfesionalTratante(paciente_id=paciente_id, **datos.model_dump())
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


@router.put("/{profesional_tratante_id}", response_model=ProfesionalTratanteRespuesta)
def editar_profesional(
    paciente_id: int,
    profesional_tratante_id: int,
    datos: ProfesionalTratanteGuardar,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    registro = session.exec(
        select(ProfesionalTratante).where(
            ProfesionalTratante.id == profesional_tratante_id,
            ProfesionalTratante.paciente_id == paciente_id,
        )
    ).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Profesional interviniente no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(registro, campo, valor)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro
