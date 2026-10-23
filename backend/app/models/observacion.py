"""Observaciones de una sesión, vinculadas opcionalmente a un objetivo."""

from sqlmodel import Field, SQLModel


class Observacion(SQLModel, table=True):
    __tablename__ = "observacion"

    id: int | None = Field(default=None, primary_key=True)
    sesion_id: int = Field(foreign_key="sesion.id", ondelete="RESTRICT")
    objetivo_id: int | None = Field(default=None, foreign_key="objetivo.id", ondelete="RESTRICT")
    contexto: str | None = None
    conducta_observable: str | None = None
    intervencion: str | None = None
    resultado: str | None = None
    nota_libre: str | None = None
