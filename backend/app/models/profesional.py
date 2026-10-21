from sqlmodel import SQLModel, Field


class Profesional(SQLModel, table=True):
    __tablename__ = "profesional"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    email: str
    password_hash: str
    activo: bool = True