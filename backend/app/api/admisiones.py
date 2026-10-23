"""Consultar y guardar la admision de un paciente autorizado."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.dependencies import ProfesionalActual, SesionDB
from app.models import Admision, Paciente
from app.schemas.admision import AdmisionGuardar, AdmisionRespuesta


router = APIRouter(prefix="/pacientes/{paciente_id}/admision", tags=["Admisión"])


def verificar_paciente(paciente_id: int, session: SesionDB, profesional: ProfesionalActual) -> None:
    paciente = session.get(Paciente, paciente_id)
    if paciente is None or paciente.profesional_id != profesional.id:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")


@router.get("", response_model=AdmisionRespuesta | None)
def obtener_admision(
    paciente_id: int,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)
    return session.exec(
        select(Admision).where(Admision.paciente_id == paciente_id)
    ).first()


@router.put("", response_model=AdmisionRespuesta)
def guardar_admision(
    paciente_id: int,
    datos: AdmisionGuardar,
    session: SesionDB,
    profesional: ProfesionalActual,
):
    verificar_paciente(paciente_id, session, profesional)

    admision = session.exec(
        select(Admision).where(Admision.paciente_id == paciente_id)
    ).first()

    if admision is None:
        admision = Admision(paciente_id=paciente_id, **datos.model_dump())
    else:
        for campo, valor in datos.model_dump().items():
            setattr(admision, campo, valor)

    session.add(admision)
    session.commit()
    session.refresh(admision)
    return admision
