from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event


pytestmark = pytest.mark.integration
PATIENT = {
    "nombre": "Paciente", "apellido": "Prueba", "fecha_nacimiento": "2015-01-01",
    "fecha_inicio_seguimiento": "2026-01-01",
}


@pytest.fixture
def chronology(profile_client):
    patient = profile_client.post("/api/pacientes", json=PATIENT).json()["id"]
    return profile_client, f"/api/pacientes/{patient}"


def add_session(client, base, day, present=True):
    response = client.post(base + "/sesiones", json={"fecha": day, "presente": present})
    assert response.status_code == 201
    return response.json()


def test_chronology_pages_sessions_with_complete_ordered_observations(chronology, auth_app):
    client, base = chronology
    path = base + "/cronologia"
    assert client.get(path).json() == {"items": [], "total": 0, "offset": 0, "limit": 20}
    sessions = [add_session(client, base, day, index != 2) for index, day in enumerate(
        ["2026-01-01", "2026-02-01", "2026-02-01"]
    )]
    observation_path = f"{base}/sesiones/{sessions[1]['id']}/observaciones"
    observations = [client.post(observation_path, json={"nota_libre": "Nota ficticia"}).json()
                    for _ in range(3)]
    sibling = client.post("/api/pacientes", json=PATIENT).json()["id"]
    add_session(client, f"/api/pacientes/{sibling}", "2027-01-01")

    statements = []
    def capture(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)
    event.listen(auth_app.state.engine, "before_cursor_execute", capture)
    try:
        response = client.get(path)
    finally:
        event.remove(auth_app.state.engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 3
    assert result["items"] == [record | {"observaciones": observations if record == sessions[1] else []}
                               for record in reversed(sessions)]
    # Una única consulta para todas las observaciones de la página.
    assert sum("FROM observacion" in statement for statement in statements) == 1
    page = client.get(path, params={"offset": 1, "limit": 1}).json()
    assert page == {"items": [sessions[1] | {"observaciones": observations}],
                    "total": 3, "offset": 1, "limit": 1}
    assert client.get(path, params={"offset": 99}).json() == {
        "items": [], "total": 3, "offset": 99, "limit": 20,
    }


@pytest.mark.parametrize("params,expected", [
    ({"desde": "2026-02-01"}, ["2026-03-01", "2026-02-01"]),
    ({"hasta": "2026-02-01"}, ["2026-02-01", "2026-01-01"]),
    ({"desde": "2026-02-01", "hasta": "2026-02-01"}, ["2026-02-01"]),
    ({"desde": "2026-01-01", "hasta": "2026-03-01"}, ["2026-03-01", "2026-02-01", "2026-01-01"]),
    ({"desde": "2027-01-01"}, []),
])
def test_chronology_filters_are_inclusive_and_count_before_pagination(chronology, params, expected):
    client, base = chronology
    for day in ["2026-01-01", "2026-02-01", "2026-03-01"]:
        add_session(client, base, day)
    response = client.get(base + "/cronologia", params=params)
    assert response.status_code == 200
    assert [item["fecha"] for item in response.json()["items"]] == expected
    page = client.get(base + "/cronologia", params=params | {"offset": 1, "limit": 1}).json()
    assert page["total"] == len(expected)
    assert [item["fecha"] for item in page["items"]] == expected[1:2]


@pytest.mark.parametrize("query", [
    "desde=2026-02-01&hasta=2026-01-01", "desde=", "hasta=2026-02-30",
    "desde=2026-01-01T00:00:00", "desde=123", "hasta=01-02-2026",
    "offset=-1", "limit=0", "limit=101",
])
def test_chronology_rejects_invalid_dates_interval_and_page(chronology, query):
    client, base = chronology
    assert client.get(base + "/cronologia?" + query).status_code == 422


def test_chronology_reflects_source_changes_and_preserves_inactive_history(chronology):
    client, base = chronology
    first = add_session(client, base, "2026-01-01")
    second = add_session(client, base, "2026-02-01", False)
    source = f"{base}/sesiones/{first['id']}"
    observation = client.post(source + "/observaciones", json={"nota_libre": "Inicial"}).json()
    assert client.patch(source, json={"fecha": "2026-03-01"}).status_code == 200
    assert client.patch(source + f"/observaciones/{observation['id']}", json={"nota_libre": "Editada"}).status_code == 200
    assert client.patch(base, json={"activo": False}).status_code == 200
    result = client.get(base + "/cronologia").json()
    assert [item["id"] for item in result["items"]] == [first["id"], second["id"]]
    assert result["items"][0]["observaciones"][0]["nota_libre"] == "Editada"
    assert client.get(base + "/cronologia?hasta=2026-02-01").json()["total"] == 1


def test_chronology_hides_foreign_and_missing_patients(chronology, auth_app):
    client, base = chronology
    add_session(client, base, "2026-01-01")
    assert client.get("/api/pacientes/2147483647/cronologia").status_code == 404
    with TestClient(auth_app) as other:
        account = {"nombre": "Otro", "apellido": "Prueba", "email": "otro@example.com", "password": "Password de prueba 123"}
        assert other.post("/api/auth/registro", json=account).status_code == 201
        assert other.post("/api/auth/login", json={key: account[key] for key in ("email", "password")}).status_code == 200
        assert other.get(base + "/cronologia").status_code == 404
