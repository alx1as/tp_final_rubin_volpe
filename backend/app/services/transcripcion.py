"""Transcripción temporal: el audio se cierra en todos los caminos."""

from fastapi import HTTPException, UploadFile

from app.integrations.contratos import IntegracionNoConfigurada, Transcriptor
from app.schemas.integraciones import TranscripcionRespuesta
from app.services.integraciones import ejecutar_integracion


def transcribir_audio(audio: UploadFile, transcriptor: Transcriptor | None) -> TranscripcionRespuesta:
    try:
        if transcriptor is None:
            raise IntegracionNoConfigurada
        if not audio.file.read(1):
            raise HTTPException(status_code=422, detail="El archivo de audio está vacío")
        audio.file.seek(0)
        texto = ejecutar_integracion(lambda: transcriptor.transcribir(
            audio.file, nombre_archivo=audio.filename, tipo_contenido=audio.content_type,
        ))
        return TranscripcionRespuesta(texto=texto)
    finally:
        # UploadFile usa SpooledTemporaryFile: close también elimina su archivo
        # temporal si el parser tuvo que volcar el audio a disco.
        audio.file.close()
