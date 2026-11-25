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
        fecha_inicio=date(2026, 9, 1), fecha_cierre=None,
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


def test_estado_del_objetivo_no_anticipa_cierre_posterior():
    contexto = contexto_con_sesion()
    objetivo = contexto.objetivos[0]
    objetivo.estado = "cumplido"
    objetivo.fecha_cierre = date(2026, 11, 1)
    datos = groq_informes.datos_minimos(contexto)["objetivos"][0]
    assert datos["estado_actual"] == "cumplido"
    assert datos["estado_segun_fechas_al_fin_del_periodo"] == "activo"
    objetivo.fecha_cierre = date(2026, 10, 30)
    assert groq_informes.datos_minimos(contexto)["objetivos"][0]["estado_segun_fechas_al_fin_del_periodo"] == "cumplido"
    objetivo.fecha_inicio = date(2026, 11, 1)
    assert groq_informes.datos_minimos(contexto)["objetivos"][0]["estado_segun_fechas_al_fin_del_periodo"] == "no determinado"


def test_no_acepta_borrador_truncado(monkeypatch):
    class Respuesta:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, size):
            return b'{"choices":[{"finish_reason":"length","message":{"content":"Incompleto"}}]}'

    monkeypatch.setattr(groq_informes, "urlopen", lambda *args, **kwargs: Respuesta())
    with pytest.raises(ValueError, match="truncado"):
        groq_informes.GeneradorGroq("clave_ficticia").generar(contexto_con_sesion())
