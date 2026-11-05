"""Propuesta no persistida de organización de una nota transcripta."""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CAMPOS_NOTA = ("contexto", "conducta_observable", "intervencion", "resultado", "nota_libre")


class SolicitudOrganizacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: str = Field(min_length=5, max_length=12000)

    @field_validator("texto")
    @classmethod
    def texto_util(cls, texto: str) -> str:
        texto = texto.strip()
        if len(texto) < 5:
            raise ValueError("La nota debe contener al menos cinco caracteres")
        return texto


class SugerenciaObservacion(BaseModel):
    """Los campos ausentes en el relato son null; nada se guarda aquí."""

    model_config = ConfigDict(extra="forbid")
    contexto: str | None = Field(max_length=3500)
    conducta_observable: str | None = Field(max_length=3500)
    intervencion: str | None = Field(max_length=3500)
    resultado: str | None = Field(max_length=3500)
    nota_libre: str | None = Field(max_length=3500)

    @field_validator(*CAMPOS_NOTA)
    @classmethod
    def limpiar(cls, texto: str | None) -> str | None:
        if texto is None:
            return None
        return texto.strip() or None

    @model_validator(mode="after")
    def verificar_algun_contenido(self):
        if not any(getattr(self, campo) for campo in CAMPOS_NOTA):
            raise ValueError("No se encontró información utilizable")
        return self
