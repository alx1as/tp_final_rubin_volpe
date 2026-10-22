"""Modelo de escolaridad; la tabla ya existe en backend/init.sql."""

from datetime import date

from sqlmodel import Field, SQLModel


class Escolaridad(SQLModel, table=True):
    __tablename__ = "escolaridad"

    id: int | None = Field(default=None, primary_key=True)
    paciente_id: int = Field(foreign_key="paciente.id")
    institucion: str
    nivel: str
    grado_anio_sala: str
    modalidad: str
    jornada: str | None = None
    fecha_inicio: date
    fecha_fin: date | None = None
    apoyos: str | None = None
    observaciones: str | None = None
    referente_nombre: str | None = None
    referente_rol: str | None = None
    referente_contacto: str | None = None
