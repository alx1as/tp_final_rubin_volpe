"""Contacto profesional externo relacionado con un paciente."""

from datetime import date

from sqlmodel import Field, SQLModel


class ProfesionalTratante(SQLModel, table=True):
    __tablename__ = "profesional_tratante"

    id: int | None = Field(default=None, primary_key=True)
    paciente_id: int = Field(foreign_key="paciente.id")
    nombre: str
    especialidad: str
    contacto: str | None = None
    fecha_inicio: date
    fecha_fin: date | None = None
    observaciones: str | None = None
