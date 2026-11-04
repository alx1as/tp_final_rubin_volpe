"""Dependencias independientes para transcripción y generación de informes."""

from typing import Annotated

from fastapi import Depends, Request

from app.integrations.contratos import GeneradorInformes, Transcriptor
from app.integrations.groq_informes import GeneradorGroq


def obtener_transcriptor() -> Transcriptor | None:
    # La integración de audio se mantiene separada (a cargo de Mavi).
    return None


def obtener_generador_informes(request: Request) -> GeneradorInformes | None:
    configuracion = getattr(request.app.state, "settings", None)
    clave = getattr(configuracion, "groq_api_key", None)
    if clave is None or not clave.get_secret_value().strip():
        return None
    return GeneradorGroq(
        api_key=clave.get_secret_value(), model=configuracion.groq_model,
    )


TranscriptorActual = Annotated[Transcriptor | None, Depends(obtener_transcriptor)]
GeneradorActual = Annotated[GeneradorInformes | None, Depends(obtener_generador_informes)]
