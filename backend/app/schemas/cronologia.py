"""Sesiones de la cronología con todas sus observaciones."""

from app.schemas.observacion import ObservacionRespuesta
from app.schemas.sesion import SesionRespuesta


class EntradaCronologia(SesionRespuesta):
    observaciones: list[ObservacionRespuesta]
