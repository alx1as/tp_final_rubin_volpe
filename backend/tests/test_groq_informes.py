"""Pruebas sin llamadas a servicios externos ni PostgreSQL."""

import json
from datetime import date
from types import SimpleNamespace

import pytest

from app.integrations import groq_informes
from app.integrations.contratos import ContextoInforme


def contexto_con_sesion(nota="Observación ficticia"):
    observacion = SimpleNamespace(
        objetivo_id=12, contexto="Aula", conducta_observable="Participa",
        intervencion=None, resultado=None, nota_libre=nota,
    )
    sesion = SimpleNamespace(
        fecha=date(2026, 10, 7), presente=True,
        nota_general="Seguimiento ficticio", observaciones=[observacion],
    )
    objetivo = SimpleNamespace(
        id=12, descripcion="Objetivo ficticio", estado="activo",
        observaciones_generales=None,
    )
    paciente = SimpleNamespace(nombre="Nombre privado", apellido="Apellido privado",
                               fecha_nacimiento=date(2010, 1, 1), id=900)
    return ContextoInforme(
        titulo="Informe ficticio", periodo_desde=date(2026, 10, 1),
        periodo_hasta=date(2026, 10, 31), paciente=paciente,
        sesiones=(sesion,), objetivos=(objetivo,),
    )


def test_groq_recibe_solo_datos_minimos_y_devuelve_texto(monkeypatch):
    recibido = {}

    class Respuesta:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, size):
            return b'{"choices":[{"message":{"content":" Borrador de prueba "}}]}'

    def fake_urlopen(peticion, timeout):
        recibido["url"] = peticion.full_url
        recibido["timeout"] = timeout
        recibido["headers"] = peticion.headers
        recibido["json"] = json.loads(peticion.data)
        return Respuesta()

    monkeypatch.setattr(groq_informes, "urlopen", fake_urlopen)
    texto = groq_informes.GeneradorGroq(api_key="clave_ficticia").generar(contexto_con_sesion())
    assert texto == "Borrador de prueba"
    assert recibido["url"] == groq_informes.URL_GROQ
    assert recibido["timeout"] == 30
    assert recibido["headers"]["Authorization"] == "Bearer clave_ficticia"
    assert recibido["headers"]["User-agent"] == "seguimiento-psicopedagogico/1.0"
    payload = recibido["json"]
    assert payload["model"] == "openai/gpt-oss-20b"
    registros = json.loads(payload["messages"][1]["content"].split("\n", 1)[1])
    assert registros["sesiones"][0]["observaciones"][0]["nota_libre"] == "Observación ficticia"
    assert registros["objetivos"][0]["referencia"] == 12
    assert "Nombre privado" not in payload["messages"][1]["content"]
    assert "Apellido privado" not in payload["messages"][1]["content"]
    assert "2010-01-01" not in payload["messages"][1]["content"]


def test_sin_sesiones_no_consulta_proveedor(monkeypatch):
    def no_debe_llamar(*args, **kwargs):
        pytest.fail("No debe enviar solicitudes vacías")

    monkeypatch.setattr(groq_informes, "urlopen", no_debe_llamar)
    contexto = contexto_con_sesion()
    contexto = ContextoInforme(
        titulo=contexto.titulo, periodo_desde=contexto.periodo_desde,
        periodo_hasta=contexto.periodo_hasta, paciente=contexto.paciente,
        sesiones=(), objetivos=(),
    )
    with pytest.raises(ValueError, match="sin sesiones"):
        groq_informes.GeneradorGroq("clave_ficticia").generar(contexto)


def test_falla_si_contexto_supera_limite_sin_recortarlo(monkeypatch):
    monkeypatch.setattr(groq_informes, "MAX_DATOS", 10)
    with pytest.raises(ValueError, match="límite"):
        groq_informes.GeneradorGroq("clave_ficticia").generar(contexto_con_sesion())
