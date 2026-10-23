from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import ProfesionalActual, SesionDB
from app.models import Paciente
from app.schemas.paciente import PacienteCrear, PacienteRespuesta


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

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
