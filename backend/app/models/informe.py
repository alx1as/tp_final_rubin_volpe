"""Informe persistido, independiente de los registros fuente del seguimiento."""

from datetime import date

from sqlmodel import Field, SQLModel


class Informe(SQLModel, table=True):
    __tablename__ = "informe"

    id: int | None = Field(default=None, primary_key=True)
    paciente_id: int = Field(foreign_key="paciente.id", ondelete="RESTRICT")
    titulo: str
    fecha: date = Field(default_factory=date.today)
    estado: str = "borrador"
    periodo_desde: date
    periodo_hasta: date
    contenido: str
    asistido_ia: bool = False
