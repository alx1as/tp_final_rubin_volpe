"""Validaciones de datos para profesionales externos al sistema."""

from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.schemas.comun import EdicionParcial, FechaDominio, FechaOpcional, TextoOpcional, TextoRequerido


class ProfesionalTratanteGuardar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    especialidad: str
    contacto: str | None = None
    fecha_inicio: FechaDominio
    fecha_fin: FechaOpcional = None
    observaciones: str | None = None

    @field_validator("nombre", "especialidad")
    @classmethod
    def validar_requeridos(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo es obligatorio")
        return valor

    @field_validator("contacto", "observaciones", mode="before")
    @classmethod
    def normalizar_opcionales(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        if not isinstance(valor, str):
            raise ValueError("El campo debe ser texto")
        return valor.strip() or None

    @field_validator("fecha_fin", mode="before")
    @classmethod
    def normalizar_fecha_fin(cls, valor: str | date | None) -> str | date | None:
        return None if valor == "" else valor

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de finalización no puede ser anterior al inicio")
        return self


class ProfesionalTratanteEditar(EdicionParcial):
    campos_no_nulos = frozenset({"nombre", "especialidad", "fecha_inicio"})

    nombre: TextoRequerido | None = None
    especialidad: TextoRequerido | None = None
    contacto: TextoOpcional = None
    fecha_inicio: FechaDominio | None = None
    fecha_fin: FechaOpcional = None
    observaciones: TextoOpcional = None


class ProfesionalTratanteRespuesta(ProfesionalTratanteGuardar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
