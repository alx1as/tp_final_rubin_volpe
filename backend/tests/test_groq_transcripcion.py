"""Pruebas locales del adaptador sin subir audio a Internet."""

import io
import sys
from types import SimpleNamespace

import pytest

from app.integrations.groq_transcripcion import TranscriptorGroq, MAX_AUDIO_BYTES


def test_transcripcion_envia_audio_y_recibe_texto(monkeypatch):
    recibido = {}

    class Transcripciones:
        def create(self, **kwargs):
            recibido.update(kwargs)
            return SimpleNamespace(text=" Texto ficticio transcripto ")

    class Cliente:
        def __init__(self, **kwargs):
            recibido["configuracion"] = kwargs
            self.audio = SimpleNamespace(transcriptions=Transcripciones())

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setitem(sys.modules, "groq", SimpleNamespace(Groq=Cliente))
    audio = io.BytesIO(b"audio de prueba")
    texto = TranscriptorGroq("clave_ficticia").transcribir(
        audio, nombre_archivo="nota.webm", tipo_contenido="audio/webm",
    )
    assert texto == " Texto ficticio transcripto "
    assert recibido["file"] == ("nota.webm", b"audio de prueba")
    assert recibido["language"] == "es"
    assert recibido["model"] == "whisper-large-v3-turbo"
    assert recibido["configuracion"]["api_key"] == "clave_ficticia"
    assert not audio.closed


def test_rechaza_extension_invalida_y_audio_excesivo():
    transcriptor = TranscriptorGroq("clave_ficticia")
    with pytest.raises(ValueError):
        transcriptor.transcribir(io.BytesIO(b"abc"), nombre_archivo="nota.exe", tipo_contenido=None)
    with pytest.raises(ValueError):
        transcriptor.transcribir(io.BytesIO(b"x" * (MAX_AUDIO_BYTES + 1)),
                                 nombre_archivo="nota.webm", tipo_contenido="audio/webm")
