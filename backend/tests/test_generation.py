from datetime import date

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event
from sqlmodel import Session

from app.integrations.dependencies import obtener_generador_informes
from app.models import Observacion, Sesion


pytestmark = pytest.mark.integration
PATIENT = {"nombre": "Paciente", "apellido": "Prueba", "fecha_nacimiento": "2015-01-01", "fecha_inicio_seguimiento": "2026-01-01"}
REQUEST = {"titulo": " Informe ficticio ", "periodo_desde": "2026-02-01", "periodo_hasta": "2026-02-28"}


class GeneradorPrueba:
    def __init__(self, resultado=" Borrador ficticio editable ", error=None):
        self.resultado = resultado
        self.error = error
        self.contextos = []

    def generar(self, contexto):
        self.contextos.append(contexto)
        if self.error is not None:
            raise self.error
        return self.resultado


@pytest.fixture
def generation(profile_client, auth_app):
    patient = profile_client.post("/api/pacientes", json=PATIENT).json()
    adapter = GeneradorPrueba()
    auth_app.dependency_overrides[obtener_generador_informes] = lambda: adapter
    return profile_client, f"/api/pacientes/{patient['id']}", patient, adapter


def add_session(client, base, day, present=True):
    response = client.post(base + "/sesiones", json={"fecha": day, "presente": present})
    assert response.status_code == 201
    return response.json()


def test_generation_uses_only_patient_period_sources_and_waits_for_review_to_save(generation):
    client, base, patient, adapter = generation
    goal = client.post(base + "/objetivos", json={"descripcion": "Objetivo ficticio", "fecha_inicio": "2026-01-01"}).json()
    client.post(base + "/objetivos", json={"descripcion": "Sin evidencia en el período", "fecha_inicio": "2026-01-01"})
    sessions = [add_session(client, base, day, index != 2) for index, day in enumerate(
        ["2026-01-31", "2026-02-01", "2026-02-28", "2026-02-28", "2026-03-01"]
    )]
    observations = []
    for record in [sessions[1], sessions[3], sessions[1], sessions[0]]:
        observations.append(client.post(f"{base}/sesiones/{record['id']}/observaciones", json={
            "nota_libre": "Nota ficticia", "objetivo_id": goal["id"],
        }).json())
    sibling = client.post("/api/pacientes", json=PATIENT).json()["id"]
    add_session(client, f"/api/pacientes/{sibling}", "2026-02-15")
    before = client.get(base + "/cronologia").json()
    response = client.post(base + "/informes/generar", json=REQUEST)
    assert response.status_code == 200
    draft = response.json()
    assert set(draft) == {"titulo", "fecha", "periodo_desde", "periodo_hasta", "contenido", "estado", "asistido_ia"}
    assert draft["titulo"] == "Informe ficticio" and draft["contenido"] == "Borrador ficticio editable"
    assert draft["estado"] == "borrador" and draft["asistido_ia"] is True
    context = adapter.contextos[0]
    assert context.paciente.model_dump(mode="json") == patient
    assert not hasattr(context.paciente, "profesional_id")
    assert context.titulo == "Informe ficticio"
    assert context.periodo_desde == date(2026, 2, 1) and context.periodo_hasta == date(2026, 2, 28)
    assert [entry.id for entry in context.sesiones] == [sessions[3]["id"], sessions[2]["id"], sessions[1]["id"]]
    assert context.sesiones[1].presente is False and context.sesiones[1].observaciones == []
    assert [item.id for item in context.sesiones[2].observaciones] == [observations[0]["id"], observations[2]["id"]]
    assert [item.id for item in context.objetivos] == [goal["id"]]
    assert client.get(base + "/cronologia").json() == before
    assert client.get(base + "/informes").json()["total"] == 0
    # Confirmación/revisión explícita: usar el POST habitual después de editar.
    draft["contenido"] = "Texto ficticio revisado"
    saved = client.post(base + "/informes", json=draft)
    assert saved.status_code == 201
    assert saved.json()["asistido_ia"] is True and saved.json()["estado"] == "borrador"
    assert saved.json()["contenido"] == draft["contenido"]
    assert client.get(base + "/informes").json()["total"] == 1


def test_generation_gathers_all_sources_beyond_list_page_size(generation, auth_app):
    client, base, patient, adapter = generation
    with Session(auth_app.state.engine) as session:
        session.add_all([Sesion(paciente_id=patient["id"], fecha=date(2026, 2, 10), presente=True) for _ in range(105)])
        session.commit()
    response = client.post(base + "/informes/generar", json=REQUEST)
    assert response.status_code == 200
    assert len(adapter.contextos[0].sesiones) == 105
    ids = [entry.id for entry in adapter.contextos[0].sesiones]
    assert ids == sorted(ids, reverse=True)
    assert client.get(base + "/informes").json()["total"] == 0


def test_generation_empty_period_has_no_invented_source_records(generation):
    client, base, _, adapter = generation
    response = client.post(base + "/informes/generar", json=REQUEST)
    assert response.status_code == 200
    assert adapter.contextos[0].sesiones == () and adapter.contextos[0].objetivos == ()
    assert client.get(base + "/informes").json()["total"] == 0


def test_generator_receives_detached_public_snapshots(generation, auth_app):
    client, base, _, adapter = generation
    source = add_session(client, base, "2026-02-10")
    before = client.get(base + "/cronologia").json()

    class GeneradorMutante(GeneradorPrueba):
        def generar(self, contexto):
            contexto.paciente.nombre = "Cambio que no debe persistir"
            contexto.sesiones[0].nota_general = "Cambio que no debe persistir"
            return super().generar(contexto)

    auth_app.dependency_overrides[obtener_generador_informes] = lambda: GeneradorMutante()
    assert client.post(base + "/informes/generar", json=REQUEST).status_code == 200
    assert client.get(base).json()["nombre"] == PATIENT["nombre"]
    assert client.get(base + "/cronologia").json() == before
    assert client.get(f"{base}/sesiones/{source['id']}").json() == source


@pytest.mark.parametrize("invalid", [
    {"titulo": " "}, {"periodo_hasta": "2026-01-31"}, {"periodo_desde": "2026-02-30"},
    {"periodo_hasta": None}, {"paciente_id": 1}, {"asistido_ia": False}, {"contenido": "No se recibe texto"},
])
def test_invalid_generation_does_not_call_provider_or_save(generation, invalid):
    client, base, _, adapter = generation
    assert client.post(base + "/informes/generar", json=REQUEST | invalid).status_code == 422
    assert adapter.contextos == []
    assert client.get(base + "/informes").json()["total"] == 0


def test_generation_hides_foreign_patient_and_checks_before_calling_provider(generation, auth_app):
    client, base, _, adapter = generation
    assert client.post("/api/pacientes/2147483647/informes/generar", json=REQUEST).status_code == 404
    with TestClient(auth_app) as other:
        account = {"nombre": "Otro", "apellido": "Prueba", "email": "otro@example.com", "password": "Password de prueba 123"}
        assert other.post("/api/auth/registro", json=account).status_code == 201
        assert other.post("/api/auth/login", json={key: account[key] for key in ("email", "password")}).status_code == 200
        assert other.post(base + "/informes/generar", json=REQUEST).status_code == 404
    assert adapter.contextos == []


def test_generation_keeps_session_observation_snapshot_during_concurrent_insert(generation, auth_app):
    client, base, patient, adapter = generation
    original = add_session(client, base, "2026-02-10")
    inserted = []

    def insert_after_source_query(connection, cursor, statement, parameters, context, executemany):
        if inserted or not statement.lstrip().startswith("SELECT sesion."):
            return
        inserted.append(True)
        with Session(auth_app.state.engine) as other_session:
            concurrent = Sesion(paciente_id=patient["id"], fecha=date(2026, 2, 11), presente=True)
            other_session.add(concurrent)
            other_session.flush()
            other_session.add(Observacion(sesion_id=concurrent.id, nota_libre="Nota concurrente ficticia"))
            other_session.commit()

    event.listen(auth_app.state.engine, "after_cursor_execute", insert_after_source_query)
    try:
        response = client.post(base + "/informes/generar", json=REQUEST)
    finally:
        event.remove(auth_app.state.engine, "after_cursor_execute", insert_after_source_query)
    assert inserted and response.status_code == 200
    assert [entry.id for entry in adapter.contextos[0].sesiones] == [original["id"]]
    assert adapter.contextos[0].sesiones[0].observaciones == []
    assert client.get(base + "/cronologia").json()["total"] == 2
