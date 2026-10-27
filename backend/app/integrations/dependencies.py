"""Puntos de sustitución: sin proveedor en ejecución hasta la integración real."""

from typing import Annotated

from fastapi import Depends

from app.integrations.contratos import GeneradorInformes, Transcriptor


def obtener_transcriptor() -> Transcriptor | None:
    return None


def obtener_generador_informes() -> GeneradorInformes | None:
    return None


TranscriptorActual = Annotated[Transcriptor | None, Depends(obtener_transcriptor)]
GeneradorActual = Annotated[GeneradorInformes | None, Depends(obtener_generador_informes)]
