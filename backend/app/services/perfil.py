"""Consultas autorizadas, paginación y escrituras del perfil."""

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from app.models import Paciente
from app.schemas.comun import Pagina, Paginacion, validar_edicion


def buscar_paciente(session: Session, profesional_id: int, paciente_id: int) -> Paciente:
    paciente = session.exec(select(Paciente).where(
        Paciente.id == paciente_id, Paciente.profesional_id == profesional_id,
    )).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


def buscar_hijo(session: Session, modelo, paciente_id: int, registro_id: int):
    registro = session.exec(select(modelo).where(
        modelo.id == registro_id, modelo.paciente_id == paciente_id,
    )).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return registro


def paginar(session: Session, consulta, parametros: Paginacion) -> Pagina:
    total = session.exec(select(func.count()).select_from(consulta.order_by(None).subquery())).one()
    items = session.exec(consulta.offset(parametros.offset).limit(parametros.limit)).all()
    return Pagina(items=items, total=total, offset=parametros.offset, limit=parametros.limit)


def guardar(session: Session, registro):
    try:
        session.add(registro)
        session.commit()
        session.refresh(registro)
    except SQLAlchemyError:
        session.rollback()
        raise
    return registro


def editar(session: Session, registro, cambios: BaseModel, esquema: type[BaseModel]):
    actual = {campo: getattr(registro, campo) for campo in esquema.model_fields}
    valores = validar_edicion(actual, cambios, esquema)
    if not valores:
        return registro
    for campo, valor in valores.items():
        setattr(registro, campo, valor)
    return guardar(session, registro)
