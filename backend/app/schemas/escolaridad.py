"""Validaciones de entrada y respuesta para períodos escolares."""

from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class EscolaridadGuardar(BaseModel):
    model_config = ConfigDict(extra="forbid")

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

    @field_validator("institucion", "nivel", "grado_anio_sala", "modalidad")
    @classmethod
    def validar_requeridos(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo es obligatorio")
        return valor

    @field_validator(
        "jornada", "apoyos", "observaciones", "referente_nombre",
        "referente_rol", "referente_contacto", mode="before"
    )
    @classmethod
    def normalizar_texto_opcional(cls, valor: str | None) -> str | None:
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


class EscolaridadRespuesta(EscolaridadGuardar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
