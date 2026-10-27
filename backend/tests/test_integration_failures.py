from fastapi import HTTPException
import pytest

from app.integrations.dependencies import obtener_generador_informes, obtener_transcriptor


pytestmark = pytest.mark.integration
PATIENT = {"nombre": "Paciente", "apellido": "Prueba", "fecha_nacimiento": "2015-01-01", "fecha_inicio_seguimiento": "2026-01-01"}
REQUEST = {"titulo": "Informe ficticio", "periodo_desde": "2026-01-01", "periodo_hasta": "2026-01-31"}


class ProveedorPrueba:
    def __init__(self, failure):
        self.failure = failure

    def resultado(self):
        if isinstance(self.failure, Exception):
            raise self.failure
        return self.failure

    def transcribir(self, audio, **metadata):
        return self.resultado()

    def generar(self, contexto):
        return self.resultado()


@pytest.mark.parametrize("failure", [
    "unconfigured", TimeoutError("Detalle privado ficticio"), RuntimeError("Detalle privado ficticio"),
    HTTPException(status_code=400, detail="Detalle privado ficticio"),
    " ", None, {"contenido": "Objeto inválido"},
])
def test_external_failures_preserve_sources_and_manual_work(profile_client, auth_app, failure):
    client = profile_client
    patient = client.post("/api/pacientes", json=PATIENT).json()["id"]
    base = f"/api/pacientes/{patient}"
    source = client.post(base + "/sesiones", json={"fecha": "2026-01-10", "presente": True}).json()
    observations = f"{base}/sesiones/{source['id']}/observaciones"
    assert client.post(observations, json={"nota_libre": "Nota ficticia"}).status_code == 201
    manual = client.post(base + "/informes", json=REQUEST | {"contenido": "Informe manual ficticio"}).json()
    before = client.get(base + "/cronologia").json()
    configured = failure != "unconfigured"
    if configured:
        provider = ProveedorPrueba(failure)
        auth_app.dependency_overrides[obtener_transcriptor] = lambda: provider
        auth_app.dependency_overrides[obtener_generador_informes] = lambda: provider
    responses = [
        client.post("/api/transcripciones", files={"audio": ("nota.webm", b"Audio ficticio", "audio/webm")}),
        client.post(base + "/informes/generar", json=REQUEST),
    ]
    for response in responses:
        assert response.status_code == 503
        assert response.json() == {"detail": "Servicio externo no disponible" if configured else "Servicio externo no configurado"}
        assert "privado" not in response.text
    assert client.get(base + "/cronologia").json() == before
    assert client.get(base + "/informes").json()["total"] == 1
    assert client.get(f"{base}/informes/{manual['id']}").json() == manual
    # Después de ambas fallas, el mismo cliente sigue registrando y consultando.
    assert client.patch(f"{base}/sesiones/{source['id']}", json={"nota_general": "Nota manual ficticia"}).status_code == 200
    assert client.post(observations, json={"nota_libre": "Nueva nota manual ficticia"}).status_code == 201
    assert client.get(observations).json()["total"] == 2
    assert client.post(base + "/informes", json=REQUEST | {"contenido": "Segundo informe manual ficticio"}).status_code == 201
    assert client.patch(f"{base}/informes/{manual['id']}", json={"estado": "finalizado"}).status_code == 200
    assert client.get(base + "/informes").json()["total"] == 2
