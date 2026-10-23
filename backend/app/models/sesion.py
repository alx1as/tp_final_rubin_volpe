"""Sesión de seguimiento; diferente de una sesión de autenticación."""

from datetime import date

from sqlmodel import Field, SQLModel


class Sesion(SQLModel, table=True):
    __tablename__ = "sesion"

    id: int | None = Field(default=None, primary_key=True)
    paciente_id: int = Field(foreign_key="paciente.id")
    fecha: date
    presente: bool
    nota_general: str | None = None
