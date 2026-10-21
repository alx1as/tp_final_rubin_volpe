#representa la tabla existente de PostgreSQL. No crea otra tabla ni modifica la base.
from datetime import date
from sqlmodel import SQLModel, Field


class Paciente(SQLModel, table=True):
    __tablename__ = "paciente"

    id: int | None = Field(default=None, primary_key=True)
    profesional_id: int = Field(foreign_key="profesional.id")
    nombre: str
    apellido: str
    fecha_nacimiento: date
    fecha_inicio_seguimiento: date
    activo: bool = True