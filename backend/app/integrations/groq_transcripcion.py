"""Adaptador de audio temporal con Groq Whisper. No persiste grabaciones."""

from dataclasses import dataclass
from pathlib import PurePath
from typing import BinaryIO

# El plan gratuito de Groq acepta archivos de hasta 25 MB.
MAX_AUDIO_BYTES = 25 * 1024 * 1024
EXTENSIONES = {"webm", "wav", "mp3", "m4a", "mp4", "ogg", "flac", "mpeg", "mpga"}


@dataclass(frozen=True, repr=False)
class TranscriptorGroq:
    api_key: str
    model: str = "whisper-large-v3-turbo"

    def transcribir(
        self, audio: BinaryIO, *, nombre_archivo: str | None, tipo_contenido: str | None,
    ) -> str:
        # El archivo pertenece a FastAPI. No se cierra ni se conserva aquí.
        extension = PurePath((nombre_archivo or "").replace("\\", "/")).suffix.lower().lstrip(".")
        if extension not in EXTENSIONES:
            raise ValueError("Formato de audio no admitido")
        datos = audio.read(MAX_AUDIO_BYTES + 1)
        if not datos or len(datos) > MAX_AUDIO_BYTES:
            raise ValueError("Audio vacío o demasiado grande")

        # Import local para no afectar los endpoints manuales si falta la librería.
        from groq import Groq

        with Groq(api_key=self.api_key, timeout=40.0, max_retries=0) as cliente:
            respuesta = cliente.audio.transcriptions.create(
                file=(f"nota.{extension}", datos),
                model=self.model,
                language="es",
                response_format="json",
                temperature=0,
            )
        return respuesta.text
