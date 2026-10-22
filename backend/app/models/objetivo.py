"""Objetivos del seguimiento de un paciente."""

from datetime import date
from sqlmodel import SQLModel, Field


class Objetivo(SQLModel, table=True):
    __tablename__ = "objetivo"

    id: int | None = Field(default=None, primary_key=True)
    paciente_id: int = Field(foreign_key="paciente.id")
    descripcion: str
    fecha_inicio: date
    estado: str = "activo"
    fecha_cierre: date | None = None
    observaciones_generales: str | None = None
