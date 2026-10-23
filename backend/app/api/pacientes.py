from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, ProfesionalActual, SesionDB
from app.models import Paciente
from app.schemas.comun import Pagina
from app.schemas.paciente import PacienteCrear, PacienteDatos, PacienteEditar, PacienteRespuesta
from app.services.perfil import editar, guardar, paginar


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

# Listar pacientes del profesional.
@router.get("", response_model=Pagina[PacienteRespuesta])
def listar_pacientes(
    session: SesionDB,
    profesional: ProfesionalActual,
    pagina: ParametrosPagina,
):
    consulta = (
        select(Paciente)
        .where(Paciente.profesional_id == profesional.id)
        .order_by(Paciente.apellido, Paciente.nombre, Paciente.id)
    )

    return paginar(session, consulta, pagina)


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

    return guardar(session, paciente)


@router.get("/{paciente_id}", response_model=PacienteRespuesta)
def consultar_paciente(paciente: PacienteAutorizado):
    return paciente


@router.patch("/{paciente_id}", response_model=PacienteRespuesta)
def editar_paciente(datos: PacienteEditar, paciente: PacienteAutorizado, session: SesionDB):
    return editar(session, paciente, datos, PacienteDatos)
