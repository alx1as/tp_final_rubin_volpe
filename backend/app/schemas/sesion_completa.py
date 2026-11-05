"""Registro de una sesión y varias observaciones en una sola operación."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.observacion import ObservacionCrear, ObservacionRespuesta
from app.schemas.sesion import SesionCrear, SesionRespuesta


class ObservacionEnSesion(ObservacionCrear):
    # Solo se envía al editar una observación ya persistida.
    id: int | None = Field(default=None, strict=True, ge=1)


class RegistroSesion(SesionCrear):
    observaciones: list[ObservacionEnSesion] = Field(default_factory=list, max_length=30)
    observaciones_eliminar: list[int] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def ids_consistentes(self):
        ids = [obs.id for obs in self.observaciones if obs.id is not None]
        if len(ids) != len(set(ids)):
            raise ValueError("Una observación no puede aparecer dos veces")
        if any(type(id_) is not int or id_ < 1 for id_ in self.observaciones_eliminar):
            raise ValueError("Los ID de observaciones a eliminar deben ser enteros positivos")
        if len(self.observaciones_eliminar) != len(set(self.observaciones_eliminar)):
            raise ValueError("No se puede eliminar la misma observación dos veces")
        if set(ids).intersection(self.observaciones_eliminar):
            raise ValueError("Una observación no puede actualizarse y eliminarse al mismo tiempo")
        return self


class RegistroSesionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sesion: SesionRespuesta
    observaciones: list[ObservacionRespuesta]
