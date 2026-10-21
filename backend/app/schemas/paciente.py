from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class PacienteCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    apellido: str
    fecha_nacimiento: date
    fecha_inicio_seguimiento: date

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo no puede estar vacío")
        return valor

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_inicio_seguimiento < self.fecha_nacimiento:
            raise ValueError("El seguimiento no puede comenzar antes del nacimiento")
        return self


class PacienteRespuesta(PacienteCrear):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool