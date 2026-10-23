"""Consultar, crear y editar objetivos de un paciente."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import ProfesionalActual, SesionDB
from app.models import Objetivo, Paciente
from app.schemas.objetivo import ObjetivoGuardar, ObjetivoRespuesta

router = APIRouter(prefix="/pacientes/{paciente_id}/objetivos", tags=["Objetivos"])


def verificar_paciente(paciente_id: int, session: SesionDB, profesional: ProfesionalActual) -> None:
    paciente = session.get(Paciente, paciente_id)
    if paciente is None or paciente.profesional_id != profesional.id:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")


@router.get("", response_model=list[ObjetivoRespuesta])
def listar_objetivos(paciente_id: int, session: SesionDB, profesional: ProfesionalActual):
    verificar_paciente(paciente_id, session, profesional)
    return session.exec(
        select(Objetivo)
        .where(Objetivo.paciente_id == paciente_id)
        .order_by(Objetivo.fecha_inicio.desc(), Objetivo.id.desc())
    ).all()


@router.post("", response_model=ObjetivoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_objetivo(
    paciente_id: int, datos: ObjetivoGuardar, session: SesionDB, profesional: ProfesionalActual
):
    verificar_paciente(paciente_id, session, profesional)
    registro = Objetivo(paciente_id=paciente_id, **datos.model_dump())
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


@router.put("/{objetivo_id}", response_model=ObjetivoRespuesta)
def editar_objetivo(
    paciente_id: int, objetivo_id: int, datos: ObjetivoGuardar,
    session: SesionDB, profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    registro = session.exec(
        select(Objetivo).where(Objetivo.id == objetivo_id, Objetivo.paciente_id == paciente_id)
    ).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(registro, campo, valor)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro
