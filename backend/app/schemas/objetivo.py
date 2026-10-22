"""Esquemas de entrada y salida de objetivos."""

from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

EstadoObjetivo = Literal["activo", "cumplido", "cerrado"]


class ObjetivoGuardar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    descripcion: str
    fecha_inicio: date
    estado: EstadoObjetivo = "activo"
    fecha_cierre: date | None = None
    observaciones_generales: str | None = None

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("La descripción del objetivo es obligatoria")
        return valor

    @field_validator("fecha_cierre", mode="before")
    @classmethod
    def normalizar_fecha_cierre(cls, valor: str | date | None) -> str | date | None:
        return None if valor == "" else valor

    @field_validator("observaciones_generales", mode="before")
    @classmethod
    def normalizar_observaciones(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        if not isinstance(valor, str):
            raise ValueError("Las observaciones deben ser texto")
        return valor.strip() or None

    @model_validator(mode="after")
    def validar_cierre(self):
        if self.estado == "activo" and self.fecha_cierre is not None:
            raise ValueError("Un objetivo activo no debe tener fecha de cierre")
        if self.estado != "activo" and self.fecha_cierre is None:
            raise ValueError("Indicá la fecha de cierre del objetivo")
        if self.fecha_cierre is not None and self.fecha_cierre < self.fecha_inicio:
            raise ValueError("La fecha de cierre no puede ser anterior al inicio")
        return self


class ObjetivoRespuesta(ObjetivoGuardar):
    model_config = ConfigDict(from_attributes=True)
    id: int
    paciente_id: int
