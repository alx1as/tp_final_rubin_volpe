"""Consultar y guardar la admision de un paciente autorizado."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, SesionDB
from app.models import Admision
from app.schemas.admision import AdmisionGuardar, AdmisionRespuesta
from app.services.perfil import guardar


router = APIRouter(prefix="/pacientes/{paciente_id}/admision", tags=["Admisión"])


@router.get("", response_model=AdmisionRespuesta)
def obtener_admision(
    paciente: PacienteAutorizado,
    session: SesionDB,
):
    admision = session.exec(
        select(Admision).where(Admision.paciente_id == paciente.id)
    ).first()
    if admision is None:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    return admision


@router.put("", response_model=AdmisionRespuesta, responses={201: {"model": AdmisionRespuesta}})
def guardar_admision(
    datos: AdmisionGuardar,
    paciente: PacienteAutorizado,
    response: Response,
    session: SesionDB,
):
    admision = session.exec(
        select(Admision).where(Admision.paciente_id == paciente.id)
    ).first()

    if admision is None:
        admision = Admision(paciente_id=paciente.id, **datos.model_dump())
        response.status_code = status.HTTP_201_CREATED
    else:
        for campo, valor in datos.model_dump().items():
            setattr(admision, campo, valor)

    return guardar(session, admision)
