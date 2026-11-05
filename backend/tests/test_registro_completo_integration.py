"""Requiere TEST_DATABASE_URL terminada en _test (fixtures existentes)."""

import pytest

pytestmark = pytest.mark.integration

PACIENTE = {"nombre": "María", "apellido": "Ficticia", "fecha_nacimiento": "2014-06-01", "fecha_inicio_seguimiento": "2026-01-01"}


def test_endpoint_completo_persistencia_edicion_y_rollback(profile_client):
    client = profile_client
    paciente = client.post("/api/pacientes", json=PACIENTE).json()["id"]
    ajeno = client.post("/api/pacientes", json=PACIENTE).json()["id"]
    obj = client.post(f"/api/pacientes/{paciente}/objetivos", json={
        "descripcion": "Comprender instrucciones", "fecha_inicio": "2026-01-01",
    }).json()["id"]
    ruta = f"/api/pacientes/{paciente}/sesiones/completa"
    carga = {"fecha": "2026-11-05", "presente": True, "nota_general": "Prueba",
             "observaciones": [{"objetivo_id": obj, "contexto": "En clase"},
                                {"resultado": "Completó el trabajo"}]}
    respuesta = client.post(ruta, json=carga)
    assert respuesta.status_code == 201, respuesta.text
    datos = respuesta.json()
    assert len(datos["observaciones"]) == 2
    sesion_id = datos["sesion"]["id"]
    assert client.get(f"/api/pacientes/{paciente}/sesiones/{sesion_id}/observaciones").json()["total"] == 2
    assert client.post(f"/api/pacientes/{ajeno}/sesiones/completa", json={
        **carga, "observaciones": [{"objetivo_id": obj, "contexto": "Ficticio"}],
    }).status_code == 404
    assert client.post(f"/api/pacientes/{ajeno}/sesiones/completa", json={
        **carga, "observaciones": [{"contexto": "Ficticio"}],
    }).status_code == 201  # Sesión sin objetivo en el otro paciente, permitida.
    editado = client.patch(f"/api/pacientes/{paciente}/sesiones/{sesion_id}/completa", json={
        "fecha": "2026-11-06", "presente": False,
        "observaciones": [{"id": datos["observaciones"][0]["id"], "contexto": "Otro contexto"}],
        "observaciones_eliminar": [datos["observaciones"][1]["id"]],
    })
    assert editado.status_code == 200, editado.text
    assert len(editado.json()["observaciones"]) == 1
    assert editado.json()["sesion"]["presente"] is False
