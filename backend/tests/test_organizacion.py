"""Pruebas sin llamadas reales a Groq ni datos de pacientes."""

import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.integrations.groq_organizacion import OrganizadorGroq
from app.schemas.organizacion import SolicitudOrganizacion, SugerenciaObservacion


class RespuestaSimulada:
    def __init__(self, contenido):
        self.contenido = contenido

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, max_bytes):
        return self.contenido


def test_organizador_usa_esquema_estricto_y_no_guarda():
    capturado = {}
    datos = {"contexto": "En el aula", "conducta_observable": "Necesitó ayuda para leer",
             "intervencion": "Se dividió la consigna", "resultado": None, "nota_libre": None}

    def respuesta(request, timeout):
        capturado["solicitud"] = json.loads(request.data)
        capturado["timeout"] = timeout
        return RespuestaSimulada(json.dumps({
            "choices": [{"message": {"content": json.dumps(datos)}}]
        }).encode())

    with patch("app.integrations.groq_organizacion.urlopen", respuesta):
        salida = OrganizadorGroq("clave_de_prueba").organizar("Hoy trabajamos en el aula y costó leer")
    assert salida.contexto == "En el aula"
    assert salida.resultado is None
    assert capturado["solicitud"]["response_format"]["json_schema"]["strict"] is True
    assert capturado["solicitud"]["messages"][1]["content"].endswith(
        "Hoy trabajamos en el aula y costó leer")
    assert capturado["timeout"] == 35


def test_no_acepta_suposiciones_en_campos_extra():
    with pytest.raises(ValidationError):
        SugerenciaObservacion.model_validate({
            "contexto": "a", "conducta_observable": None, "intervencion": None,
            "resultado": None, "nota_libre": None, "diagnostico": "inventado",
        })


def test_no_acepta_salida_vacia():
    with pytest.raises(ValidationError):
        SugerenciaObservacion.model_validate({
            "contexto": None, "conducta_observable": None, "intervencion": None,
            "resultado": None, "nota_libre": None,
        })


def test_solicitud_rechaza_texto_vacio_o_excesivo():
    for texto in ["   ", "abc", "x" * 12001]:
        with pytest.raises(ValidationError):
            SolicitudOrganizacion(texto=texto)
