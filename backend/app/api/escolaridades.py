"""Listar, crear y editar períodos escolares del paciente."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.pacientes import ProfesionalActual, SesionDB
from app.models import Escolaridad, Paciente
from app.schemas.escolaridad import EscolaridadGuardar, EscolaridadRespuesta


router = APIRouter(
    prefix="/pacientes/{paciente_id}/escolaridades", tags=["Escolaridad"]
)


def verificar_paciente(paciente_id: int, session: SesionDB, profesional: ProfesionalActual) -> None:
    paciente = session.get(Paciente, paciente_id)
    if paciente is None or paciente.profesional_id != profesional.id:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")


@router.get("", response_model=list[EscolaridadRespuesta])
def listar_escolaridades(
    paciente_id: int, session: SesionDB, profesional: ProfesionalActual
):
    verificar_paciente(paciente_id, session, profesional)
    return session.exec(
        select(Escolaridad)
        .where(Escolaridad.paciente_id == paciente_id)
        .order_by(Escolaridad.fecha_inicio.desc(), Escolaridad.id.desc())
    ).all()


@router.post("", response_model=EscolaridadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_escolaridad(
    paciente_id: int,
    datos: EscolaridadGuardar,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    registro = Escolaridad(paciente_id=paciente_id, **datos.model_dump())
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


@router.put("/{escolaridad_id}", response_model=EscolaridadRespuesta)
def editar_escolaridad(
    paciente_id: int,
    escolaridad_id: int,
    datos: EscolaridadGuardar,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    registro = session.exec(
        select(Escolaridad).where(
            Escolaridad.id == escolaridad_id,
            Escolaridad.paciente_id == paciente_id,
        )
    ).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Escolaridad no encontrada")
    for campo, valor in datos.model_dump().items():
        setattr(registro, campo, valor)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro
