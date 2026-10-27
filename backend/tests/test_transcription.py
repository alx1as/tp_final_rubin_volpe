import os

import pytest
from starlette.datastructures import UploadFile
from sqlmodel import Session, select

from app.integrations.dependencies import obtener_transcriptor
from app.models import Informe, Observacion, Sesion


pytestmark = pytest.mark.integration
AUDIO = {"audio": ("nota.webm", b"Audio ficticio para probar el transporte", "audio/webm")}


class TranscriptorPrueba:
    def __init__(self, resultado=" Texto ficticio editable ", error=None):
        self.resultado = resultado
        self.error = error
        self.llamadas = []

    def transcribir(self, audio, *, nombre_archivo, tipo_contenido):
        self.llamadas.append((audio, nombre_archivo, tipo_contenido, audio.read()))
        if self.error is not None:
            raise self.error
        return self.resultado


def track_uploads(monkeypatch):
    uploads = []
    original = UploadFile.close

    async def close(upload):
        uploads.append(upload)
        await original(upload)

    monkeypatch.setattr(UploadFile, "close", close)
    return uploads


def test_transcription_returns_reviewable_text_without_persistence(profile_client, auth_app):
    adapter = TranscriptorPrueba()
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    response = profile_client.post("/api/transcripciones", files=AUDIO)
    assert response.status_code == 200 and response.json() == {"texto": "Texto ficticio editable"}
    stream, name, content_type, data = adapter.llamadas[0]
    assert name == "nota.webm" and content_type == "audio/webm"
    assert data == AUDIO["audio"][1] and stream.closed
    with Session(auth_app.state.engine) as session:
        for model in [Sesion, Observacion, Informe]:
            assert session.exec(select(model)).all() == []


@pytest.mark.parametrize("failure", [RuntimeError("Detalle privado ficticio"), TimeoutError("Tiempo privado ficticio")])
def test_transcription_provider_failures_are_sanitized_and_audio_is_closed(profile_client, auth_app, failure):
    adapter = TranscriptorPrueba(error=failure)
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    response = profile_client.post("/api/transcripciones", files=AUDIO)
    assert response.status_code == 503
    assert response.json() == {"detail": "Servicio externo no disponible"}
    assert "privado" not in response.text and "ficticio" not in response.text
    assert adapter.llamadas[0][0].closed


@pytest.mark.parametrize("result", ["", " \n\t", None, 123, {"texto": "No es un string"}])
def test_transcription_invalid_provider_output_is_unavailable(profile_client, auth_app, result):
    adapter = TranscriptorPrueba(resultado=result)
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    response = profile_client.post("/api/transcripciones", files=AUDIO)
    assert response.status_code == 503
    assert response.json() == {"detail": "Servicio externo no disponible"}
    assert adapter.llamadas[0][0].closed


def test_transcription_without_provider_closes_upload_and_returns_503(profile_client, monkeypatch):
    uploads = track_uploads(monkeypatch)
    response = profile_client.post("/api/transcripciones", files=AUDIO)
    assert response.status_code == 503
    assert response.json() == {"detail": "Servicio externo no configurado"}
    assert uploads and all(upload.file.closed for upload in uploads)


def test_unauthenticated_upload_is_closed_before_provider_call(auth_app, monkeypatch):
    from fastapi.testclient import TestClient

    adapter = TranscriptorPrueba()
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    uploads = track_uploads(monkeypatch)
    with TestClient(auth_app) as client:
        response = client.post("/api/transcripciones", files=AUDIO)
    assert response.status_code == 401
    assert adapter.llamadas == []
    assert uploads and all(upload.file.closed for upload in uploads)


def test_untrusted_origin_cannot_invoke_transcription(profile_client, auth_app):
    adapter = TranscriptorPrueba()
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    response = profile_client.post("/api/transcripciones", files=AUDIO, headers={"Origin": "https://externo.example"})
    assert response.status_code == 403 and adapter.llamadas == []


def test_transcription_rejects_empty_and_missing_audio_and_closes_resources(profile_client, auth_app, monkeypatch):
    adapter = TranscriptorPrueba()
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    uploads = track_uploads(monkeypatch)
    assert profile_client.post("/api/transcripciones", files={"audio": ("nota.webm", b"", "audio/webm")}).status_code == 422
    assert profile_client.post("/api/transcripciones", json={}).status_code == 422
    assert profile_client.post("/api/transcripciones", files={"archivo": AUDIO["audio"]}).status_code == 422
    assert adapter.llamadas == []
    assert uploads and all(upload.file.closed for upload in uploads)


@pytest.mark.parametrize("failure", [None, RuntimeError("Falla ficticia")])
def test_transcription_disk_spool_is_released_on_success_and_failure(profile_client, auth_app, failure):
    descriptors = []

    class TranscriptorDisco(TranscriptorPrueba):
        def transcribir(self, audio, **metadata):
            descriptors.append(audio.fileno())
            return super().transcribir(audio, **metadata)

    adapter = TranscriptorDisco(error=failure)
    auth_app.dependency_overrides[obtener_transcriptor] = lambda: adapter
    response = profile_client.post("/api/transcripciones", files={
        "audio": ("nota.webm", b"x" * (2 * 1024 * 1024), "audio/webm"),
    })
    assert response.status_code == (200 if failure is None else 503)
    assert adapter.llamadas[0][0].closed
    with pytest.raises(OSError):
        os.fstat(descriptors[0])
