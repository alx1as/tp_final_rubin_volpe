"""Organización opcional de transcripciones. Requiere acceso al paciente."""

from fastapi import APIRouter, Request
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, SesionDB
from app.integrations.contratos import IntegracionNoConfigurada, IntegracionNoDisponible
from app.integrations.groq_organizacion import OrganizadorGroq
from app.integrations.groq_registro import OrganizadorRegistroGroq
from app.models import Objetivo
from app.schemas.organizacion import SolicitudOrganizacion, SugerenciaObservacion
from app.schemas.registro_asistido import SolicitudRegistroAsistido, RegistroSugerido

router = APIRouter(prefix="/pacientes/{paciente_id}/observaciones", tags=["Observaciones"])


@router.post("/organizar", response_model=SugerenciaObservacion)
def organizar_nota(datos: SolicitudOrganizacion, paciente: PacienteAutorizado, request: Request):
    # La dependencia paciente exige una sesión autenticada y acceso al paciente.
    configuracion = request.app.state.settings
    clave = configuracion.groq_api_key
    if clave is None or not clave.get_secret_value().strip():
        raise IntegracionNoConfigurada
    try:
        return OrganizadorGroq(
            api_key=clave.get_secret_value(), model=configuracion.groq_model,
        ).organizar(datos.texto)
    except Exception:
        # No incluir notas ni respuestas de un proveedor externo en el error HTTP.
        raise IntegracionNoDisponible from None


@router.post("/organizar-registro", response_model=RegistroSugerido)
def organizar_registro(
    datos: SolicitudRegistroAsistido, paciente: PacienteAutorizado,
    session: SesionDB, request: Request,
):
    """Sugerencias para un registro único; ninguna escritura en PostgreSQL."""
    clave = request.app.state.settings.groq_api_key
    if clave is None or not clave.get_secret_value().strip():
        raise IntegracionNoConfigurada
    # No enviar información identificatoria del paciente.
    objetivos = session.exec(select(Objetivo).where(Objetivo.paciente_id == paciente.id)).all()
    disponibles = [{"id": objetivo.id, "descripcion": objetivo.descripcion} for objetivo in objetivos]
    try:
        return OrganizadorRegistroGroq(
            api_key=clave.get_secret_value(), model=request.app.state.settings.groq_model,
        ).organizar(datos.texto, disponibles)
    except Exception:
        raise IntegracionNoDisponible from None
