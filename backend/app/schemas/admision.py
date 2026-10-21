"""Datos recibidos y devueltos por la API de admision."""

from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class AdmisionGuardar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    motivo_consulta: str
    antecedentes_personales: str | None = None
    antecedentes_evolutivos: str | None = None
    antecedentes_salud: str | None = None
    grupo_familiar: str | None = None
    tratamientos_actuales: str | None = None
    observaciones: str | None = None

    @field_validator("motivo_consulta")
    @classmethod
    def validar_motivo(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El motivo de consulta es obligatorio")
        return valor

    @field_validator(
        "antecedentes_personales",
        "antecedentes_evolutivos",
        "antecedentes_salud",
        "grupo_familiar",
        "tratamientos_actuales",
        "observaciones",
        mode="before",
    )
    @classmethod
    def normalizar_opcionales(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        if not isinstance(valor, str):
            raise ValueError("El campo debe ser texto")
        return valor.strip() or None


class AdmisionRespuesta(AdmisionGuardar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
