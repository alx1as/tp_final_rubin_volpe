"""Sugerencias revisables: nunca se guardan al invocar IA."""

from pydantic import Field, model_validator

from app.schemas.comun import Entrada, TextoOpcional
from app.schemas.organizacion import SolicitudOrganizacion
from app.schemas.observacion import ObservacionCrear


class SolicitudRegistroAsistido(SolicitudOrganizacion):
    pass


class ObservacionSugerida(ObservacionCrear):
    # El modelo solo puede proponer ID de objetivos ya existentes.
    pass


class RegistroSugerido(Entrada):
    nota_general: TextoOpcional = None
    observaciones: list[ObservacionSugerida] = Field(default_factory=list, max_length=6)

    @model_validator(mode="after")
    def no_vacio(self):
        if not self.nota_general and not self.observaciones:
            raise ValueError("No se encontró información utilizable en la transcripción")
        return self
