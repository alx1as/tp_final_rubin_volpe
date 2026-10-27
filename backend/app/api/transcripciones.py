"""Audio multipart autenticado, sin guardado automático de texto ni audio."""

from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.api.dependencies import ProfesionalActual
from app.integrations.dependencies import TranscriptorActual
from app.schemas.integraciones import TranscripcionRespuesta
from app.services.transcripcion import transcribir_audio


router = APIRouter(prefix="/transcripciones", tags=["Transcripciones"])


@router.post("", response_model=TranscripcionRespuesta)
def transcribir(
    profesional: ProfesionalActual, transcriptor: TranscriptorActual,
    audio: Annotated[UploadFile, File()],
):
    return transcribir_audio(audio, transcriptor)
