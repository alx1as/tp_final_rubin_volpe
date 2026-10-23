"""Contenido mínimo de observaciones y edición parcial sin reasignar sesión."""

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator

from app.schemas.comun import EdicionParcial, Entrada, FechaDominio, TextoOpcional


IdObjetivo = Annotated[int, Field(strict=True, ge=1)]
CAMPOS_CONTENIDO = ("contexto", "conducta_observable", "intervencion", "resultado", "nota_libre")


class ObservacionCrear(Entrada):
    objetivo_id: IdObjetivo | None = None
    contexto: TextoOpcional = None
    conducta_observable: TextoOpcional = None
    intervencion: TextoOpcional = None
    resultado: TextoOpcional = None
    nota_libre: TextoOpcional = None

    @model_validator(mode="after")
    def validar_contenido(self):
        if not any(getattr(self, campo) for campo in CAMPOS_CONTENIDO):
            raise ValueError("Al menos un campo de la observación debe contener texto")
        return self


class ObservacionEditar(EdicionParcial):
    objetivo_id: IdObjetivo | None = None
    contexto: TextoOpcional = None
    conducta_observable: TextoOpcional = None
    intervencion: TextoOpcional = None
    resultado: TextoOpcional = None
    nota_libre: TextoOpcional = None


class ObservacionRespuesta(ObservacionCrear):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sesion_id: int


class EvidenciaObjetivo(ObservacionRespuesta):
    fecha_sesion: FechaDominio
