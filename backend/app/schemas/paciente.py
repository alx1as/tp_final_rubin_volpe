from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.schemas.comun import EdicionParcial, FechaDominio, TextoRequerido


class PacienteCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    apellido: str
    fecha_nacimiento: FechaDominio
    fecha_inicio_seguimiento: FechaDominio

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


class PacienteDatos(PacienteCrear):
    activo: bool = True


class PacienteEditar(EdicionParcial):
    campos_no_nulos = frozenset({"nombre", "apellido", "fecha_nacimiento", "fecha_inicio_seguimiento", "activo"})

    nombre: TextoRequerido | None = None
    apellido: TextoRequerido | None = None
    fecha_nacimiento: FechaDominio | None = None
    fecha_inicio_seguimiento: FechaDominio | None = None
    activo: bool | None = None


class PacienteRespuesta(PacienteDatos):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool
