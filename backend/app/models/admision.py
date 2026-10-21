"""Modelo de la tabla admision, ya creada mediante backend/init.sql."""

from datetime import date

from sqlmodel import Field, SQLModel


class Admision(SQLModel, table=True):
    __tablename__ = "admision"

    id: int | None = Field(default=None, primary_key=True)
    paciente_id: int = Field(foreign_key="paciente.id", unique=True)
    fecha: date
    motivo_consulta: str
    antecedentes_personales: str | None = None
    antecedentes_evolutivos: str | None = None
    antecedentes_salud: str | None = None
    grupo_familiar: str | None = None
    tratamientos_actuales: str | None = None
    observaciones: str | None = None
