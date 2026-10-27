from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.integrations.dependencies import (
    GeneradorActual, TranscriptorActual, obtener_generador_informes, obtener_transcriptor,
)
from app.schemas.integraciones import BorradorGenerado, SolicitudBorrador


REQUEST = {"titulo": " Informe ficticio ", "periodo_desde": "2026-01-01", "periodo_hasta": "2026-01-31"}


def test_adapters_are_absent_by_default_and_can_be_injected_independently():
    app = FastAPI()

    @app.get("/dependencias")
    def probe(transcriptor: TranscriptorActual, generador: GeneradorActual):
        return {"transcriptor": transcriptor is not None, "generador": generador is not None}

    with TestClient(app) as client:
        assert client.get("/dependencias").json() == {"transcriptor": False, "generador": False}
        app.dependency_overrides[obtener_transcriptor] = lambda: object()
        assert client.get("/dependencias").json() == {"transcriptor": True, "generador": False}
        app.dependency_overrides[obtener_generador_informes] = lambda: object()
        assert client.get("/dependencias").json() == {"transcriptor": True, "generador": True}


@pytest.mark.parametrize("invalid", [
    {"titulo": " "}, {"periodo_hasta": "2025-12-31"}, {"periodo_desde": None},
    {"periodo_hasta": "2026-01-01T00:00:00"}, {"paciente_id": 1}, {"contenido": "No es una entrada"},
])
def test_generation_request_rejects_invalid_interval_and_injected_fields(invalid):
    with pytest.raises(ValidationError):
        SolicitudBorrador.model_validate(REQUEST | invalid)


def test_generated_draft_is_editable_save_payload_without_persisted_identity():
    request = SolicitudBorrador.model_validate(REQUEST)
    assert request.titulo == "Informe ficticio"
    draft = BorradorGenerado(**request.model_dump(), contenido=" Texto ficticio ")
    payload = draft.model_dump(mode="json")
    assert payload["contenido"] == "Texto ficticio"
    assert payload["fecha"] == date.today().isoformat()
    assert payload["estado"] == "borrador" and payload["asistido_ia"] is True
    assert not {"id", "paciente_id"} & payload.keys()
    for invalid in [{"estado": "finalizado"}, {"asistido_ia": False}, {"id": 1}]:
        with pytest.raises(ValidationError):
            BorradorGenerado.model_validate(payload | invalid)
