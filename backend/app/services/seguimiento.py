"""Reglas que relacionan sesión, observación y objetivo del mismo paciente."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Objetivo, Observacion
from app.schemas.comun import validar_edicion
from app.schemas.observacion import ObservacionCrear, ObservacionEditar
from app.services.perfil import buscar_hijo, guardar


def buscar_observacion(session: Session, sesion_id: int, observacion_id: int) -> Observacion:
    registro = session.exec(select(Observacion).where(
        Observacion.id == observacion_id, Observacion.sesion_id == sesion_id,
    )).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Observación no encontrada")
    return registro


def validar_objetivo(session: Session, paciente_id: int, objetivo_id: int | None) -> None:
    if objetivo_id is not None:
        buscar_hijo(session, Objetivo, paciente_id, objetivo_id)


def crear_observacion(session: Session, sesion_id: int, paciente_id: int, datos: ObservacionCrear):
    validar_objetivo(session, paciente_id, datos.objetivo_id)
    return guardar(session, Observacion(sesion_id=sesion_id, **datos.model_dump()))


def editar_observacion(session: Session, registro: Observacion, paciente_id: int, datos: ObservacionEditar):
    actual = {campo: getattr(registro, campo) for campo in ObservacionCrear.model_fields}
    valores = validar_edicion(actual, datos, ObservacionCrear)
    validar_objetivo(session, paciente_id, valores.get("objetivo_id", actual["objetivo_id"]))
    if not valores:
        return registro
    for campo, valor in valores.items():
        setattr(registro, campo, valor)
    return guardar(session, registro)
