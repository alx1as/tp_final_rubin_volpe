from datetime import date

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Informe
from app.services.perfil import guardar


pytestmark = pytest.mark.integration
PATIENT = {
    "nombre": "Paciente", "apellido": "Prueba", "fecha_nacimiento": "2015-01-01",
    "fecha_inicio_seguimiento": "2026-01-01",
}
REPORT = {
    "titulo": " Informe ficticio ", "fecha": "2026-03-01", "periodo_desde": "2026-01-01",
    "periodo_hasta": "2026-02-28", "contenido": " Texto ficticio\nSegunda línea ",
}


@pytest.fixture
def reports(profile_client):
    patient = profile_client.post("/api/pacientes", json=PATIENT).json()["id"]
    return profile_client, f"/api/pacientes/{patient}", patient


def test_reports_persist_manual_defaults_and_page_with_stable_order(reports):
    client, base, patient = reports
    path = base + "/informes"
    assert client.get(path).json() == {"items": [], "total": 0, "offset": 0, "limit": 20}
    records = []
    for day in ["2026-02-01", "2026-03-01", "2026-03-01"]:
        response = client.post(path, json=REPORT | {"fecha": day})
        assert response.status_code == 201
        record = response.json()
        assert record["paciente_id"] == patient
        assert record["titulo"] == "Informe ficticio"
        assert record["contenido"] == "Texto ficticio\nSegunda línea"
        assert record["estado"] == "borrador" and record["asistido_ia"] is False
        assert client.get(f"{path}/{record['id']}").json() == record
        records.append(record)
    assert client.get(path).json()["items"] == records[::-1]
    assert client.get(path + "?offset=1&limit=1").json() == {
        "items": [records[1]], "total": 3, "offset": 1, "limit": 1,
    }
    assert client.get(path + "?offset=99").json() == {
        "items": [], "total": 3, "offset": 99, "limit": 20,
    }
    # Desactivar conserva el informe y su consulta individual.
    assert client.patch(base, json={"activo": False}).status_code == 200
    assert client.get(f"{path}/{records[0]['id']}").json() == records[0]
    assert client.get(path).json()["total"] == 3


def test_reports_default_date_and_accept_reviewed_assistance_flag(reports):
    client, base, _ = reports
    body = {key: value for key, value in REPORT.items() if key != "fecha"}
    before = date.today().isoformat()
    manual = client.post(base + "/informes", json=body)
    assert manual.status_code == 201
    assert manual.json()["fecha"] in {before, date.today().isoformat()}
    assert manual.json()["asistido_ia"] is False
    reviewed = client.post(base + "/informes", json=body | {"asistido_ia": True})
    assert reviewed.status_code == 201 and reviewed.json()["asistido_ia"] is True
    assert reviewed.json()["estado"] == "borrador"


@pytest.mark.parametrize("invalid", [
    {"titulo": " "}, {"contenido": "\n\t"}, {"titulo": None}, {"contenido": None},
    {"periodo_hasta": "2025-01-01"}, {"periodo_desde": "2026-02-30"},
    {"fecha": "2026-01-01T00:00:00"}, {"fecha": 123}, {"fecha": None},
    {"asistido_ia": "false"}, {"asistido_ia": None}, {"estado": "finalizado"},
    {"estado": "otro"}, {"id": 123}, {"paciente_id": 123}, {"profesional_id": 123},
])
def test_invalid_report_creation_does_not_persist(reports, invalid):
    client, base, _ = reports
    path = base + "/informes"
    response = client.post(path, json=REPORT | invalid)
    assert response.status_code == 422
    assert client.get(path).json()["total"] == 0


@pytest.mark.parametrize("query", ["offset=-1", "limit=0", "limit=101"])
def test_reports_reject_invalid_pagination(reports, query):
    client, base, _ = reports
    assert client.get(base + "/informes?" + query).status_code == 422


def test_report_isolation_between_patients_and_professionals(reports, auth_app):
    client, base, _ = reports
    response = client.post(base + "/informes", json=REPORT)
    assert response.status_code == 201
    record = response.json()
    path = f"{base}/informes/{record['id']}"
    sibling = client.post("/api/pacientes", json=PATIENT).json()["id"]
    assert client.get(f"/api/pacientes/{sibling}/informes").json()["total"] == 0
    assert client.get(f"/api/pacientes/{sibling}/informes/{record['id']}").status_code == 404
    assert client.get(base + "/informes/2147483647").status_code == 404
    assert client.get("/api/pacientes/2147483647/informes").status_code == 404
    assert client.post("/api/pacientes/2147483647/informes", json=REPORT).status_code == 404
    with TestClient(auth_app) as other:
        account = {"nombre": "Otro", "apellido": "Prueba", "email": "otro@example.com", "password": "Password de prueba 123"}
        assert other.post("/api/auth/registro", json=account).status_code == 201
        assert other.post("/api/auth/login", json={key: account[key] for key in ("email", "password")}).status_code == 200
        other_patient = other.post("/api/pacientes", json=PATIENT).json()["id"]
        for url in [base + "/informes", path, f"/api/pacientes/{other_patient}/informes/{record['id']}"]:
            assert other.get(url).status_code == 404
        assert other.post(base + "/informes", json=REPORT).status_code == 404
        assert other.get(f"/api/pacientes/{other_patient}/informes").json()["total"] == 0
    assert client.get(path).json() == record


@pytest.mark.parametrize("invalid", [
    {"titulo": " "}, {"contenido": ""}, {"estado": "otro"},
    {"periodo_hasta": date(2025, 1, 1)}, {"paciente_id": 2147483647},
])
def test_report_sql_constraints_rollback_and_reusable_session(reports, auth_app, invalid):
    client, base, patient = reports
    data = {
        "paciente_id": patient, "titulo": "Informe ficticio", "contenido": "Texto ficticio",
        "fecha": date(2026, 3, 1), "periodo_desde": date(2026, 1, 1),
        "periodo_hasta": date(2026, 2, 28),
    }
    with Session(auth_app.state.engine) as session:
        with pytest.raises(IntegrityError):
            guardar(session, Informe(**(data | invalid)))
        assert session.is_active
        valid = guardar(session, Informe(**data))
        assert valid.id is not None
    assert client.get(base + "/informes").json()["total"] == 1


def test_report_edits_and_finalization_are_explicit_and_preserve_sources(reports):
    client, base, _ = reports
    session = client.post(base + "/sesiones", json={"fecha": "2026-01-01", "presente": True}).json()
    source_path = f"{base}/sesiones/{session['id']}"
    observation = client.post(source_path + "/observaciones", json={"nota_libre": "Nota ficticia"}).json()
    chronology_before = client.get(base + "/cronologia").json()
    record = client.post(base + "/informes", json=REPORT).json()
    path = f"{base}/informes/{record['id']}"
    assert client.patch(path, json={}).json() == record
    changed = client.patch(path, json={"contenido": " Contenido revisado ", "periodo_hasta": "2026-01-01"})
    assert changed.status_code == 200
    expected = record | {"contenido": "Contenido revisado", "periodo_hasta": "2026-01-01"}
    assert changed.json() == expected  # Editar no finaliza automáticamente.
    final = client.patch(path, json={"estado": "finalizado", "titulo": " Revisado "})
    assert final.status_code == 200
    expected |= {"estado": "finalizado", "titulo": "Revisado"}
    assert final.json() == expected
    assert client.patch(path, json={"contenido": "Corrección posterior"}).json() == expected | {"contenido": "Corrección posterior"}
    assert client.get(base + "/cronologia").json() == chronology_before
    assert client.get(source_path).json() == session
    assert client.get(source_path + f"/observaciones/{observation['id']}").json() == observation
    assert client.get(base + "/informes").json()["total"] == 1
    assert client.delete(path).status_code == 405
    assert client.put(path, json=REPORT).status_code == 405
    # No existe bloqueo/firma irreversible: reabrir exige una acción explícita.
    reopened = client.patch(path, json={"estado": "borrador"})
    assert reopened.status_code == 200 and reopened.json()["estado"] == "borrador"


@pytest.mark.parametrize("invalid", [
    {"titulo": " "}, {"contenido": "\t"}, {"titulo": None}, {"contenido": None},
    {"fecha": None}, {"periodo_desde": None}, {"periodo_hasta": None},
    {"estado": None}, {"asistido_ia": None}, {"asistido_ia": 0}, {"asistido_ia": "true"},
    {"estado": "otro"}, {"periodo_desde": "2026-03-01"}, {"periodo_hasta": "2025-01-01"},
    {"fecha": "2026-01-01T00:00:00"}, {"contenido": 123},
    {"id": 123}, {"paciente_id": 123}, {"profesional_id": 123},
])
def test_invalid_report_patch_does_not_change_any_field(reports, invalid):
    client, base, _ = reports
    record = client.post(base + "/informes", json=REPORT).json()
    path = f"{base}/informes/{record['id']}"
    response = client.patch(path, json={"titulo": "No se debe guardar"} | invalid)
    assert response.status_code == 422
    assert client.get(path).json() == record
    assert client.get(base + "/informes").json()["total"] == 1


def test_report_patch_validates_combined_period_and_resorts_by_date(reports):
    client, base, _ = reports
    first = client.post(base + "/informes", json=REPORT).json()
    second = client.post(base + "/informes", json=REPORT).json()
    path = f"{base}/informes/{first['id']}"
    # El nuevo comienzo sería inválido con el final actual; enviar ambos juntos
    # debe validarse contra el resultado completo, sin estados intermedios.
    changed = client.patch(path, json={
        "periodo_desde": "2027-01-01", "periodo_hasta": "2027-01-01",
        "fecha": "2027-02-01", "asistido_ia": True,
    })
    assert changed.status_code == 200
    assert changed.json() == first | {
        "periodo_desde": "2027-01-01", "periodo_hasta": "2027-01-01",
        "fecha": "2027-02-01", "asistido_ia": True,
    }
    assert [item["id"] for item in client.get(base + "/informes").json()["items"]] == [first["id"], second["id"]]


def test_report_patch_cannot_modify_foreign_or_crossed_parent(reports, auth_app):
    client, base, _ = reports
    record = client.post(base + "/informes", json=REPORT).json()
    path = f"{base}/informes/{record['id']}"
    sibling = client.post("/api/pacientes", json=PATIENT).json()["id"]
    assert client.patch(f"/api/pacientes/{sibling}/informes/{record['id']}", json={"estado": "finalizado"}).status_code == 404
    assert client.patch(base + "/informes/2147483647", json={}).status_code == 404
    with TestClient(auth_app) as other:
        account = {"nombre": "Otro", "apellido": "Prueba", "email": "otro@example.com", "password": "Password de prueba 123"}
        assert other.post("/api/auth/registro", json=account).status_code == 201
        assert other.post("/api/auth/login", json={key: account[key] for key in ("email", "password")}).status_code == 200
        other_patient = other.post("/api/pacientes", json=PATIENT).json()["id"]
        for url in [path, f"/api/pacientes/{other_patient}/informes/{record['id']}"]:
            assert other.patch(url, json={"contenido": "Ajeno", "estado": "finalizado"}).status_code == 404
    assert client.get(path).json() == record
