from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Paciente, Profesional
from app.schemas.paciente import PacienteCrear, PacienteRespuesta


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

SesionDB = Annotated[Session, Depends(get_session)]


# TEMPORAL: profesional de prueba para desarrollo local.
# Reemplazar por autenticación real antes de publicar.
def obtener_profesional_actual(session: SesionDB) -> Profesional:
    profesional = session.get(Profesional, 1)

    if profesional is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el profesional de prueba",
        )

    return profesional


ProfesionalActual = Annotated[
    Profesional, Depends(obtener_profesional_actual)
]


# Listar pacientes del profesional.
@router.get("", response_model=list[PacienteRespuesta])
def listar_pacientes(
    session: SesionDB,
    profesional: ProfesionalActual,
):
    consulta = (
        select(Paciente)
        .where(Paciente.profesional_id == profesional.id)
        .order_by(Paciente.apellido, Paciente.nombre)
    )

    return session.exec(consulta).all()


# Guardar un paciente en PostgreSQL.
@router.post(
    "",
    response_model=PacienteRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_paciente(
    datos: PacienteCrear,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    paciente = Paciente(
        **datos.model_dump(),
        profesional_id=profesional.id,
    )

    session.add(paciente)
    session.commit()
    session.refresh(paciente)

    return paciente