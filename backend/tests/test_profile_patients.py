from fastapi.testclient import TestClient
import pytest


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre', 'apellido':'Prueba', 'fecha_nacimiento':'2015-01-01', 'fecha_inicio_seguimiento':'2026-01-01'}


def test_patients_create_paginate_read_and_patch(profile_client):
    client = profile_client
    assert client.get('/api/pacientes').json() == {'items': [], 'total': 0, 'offset': 0, 'limit': 20}
    ids = []
    for name in ['Zeta', 'Alfa', 'Alfa']:
        response = client.post('/api/pacientes', json=PATIENT | {'nombre': name})
        assert response.status_code == 201
        ids.append(response.json()['id'])
    page = client.get('/api/pacientes?offset=1&limit=1').json()
    assert page['total'] == 3 and page['offset'] == page['limit'] == 1
    assert page['items'][0]['id'] == ids[2]
    assert [item['id'] for item in client.get('/api/pacientes').json()['items']] == [ids[1], ids[2], ids[0]]
    assert client.get('/api/pacientes?offset=99').json() == {'items': [], 'total': 3, 'offset': 99, 'limit': 20}
    path = f'/api/pacientes/{ids[0]}'
    before = client.get(path).json()
    assert before['activo'] is True
    response = client.patch(path, json={'nombre':' Nuevo '})
    assert response.status_code == 200
    assert response.json() == before | {'nombre':'Nuevo'}
    assert client.patch(path, json={}).json() == response.json()
    assert client.get(path).json() == response.json()


@pytest.mark.parametrize('query', ['offset=-1', 'limit=0', 'limit=101', 'limit=abc', 'offset=1.5'])
def test_patients_invalid_pagination_is_422(profile_client, query):
    assert profile_client.get('/api/pacientes?' + query).status_code == 422


@pytest.mark.parametrize('invalid', [{'nombre':'  '}, {'apellido':None}, {'activo':None}, {'fecha_nacimiento':None}, {'fecha_nacimiento':'2027-01-01'}, {'id':1}, {'profesional_id':1}, {'paciente_id':1}])
def test_invalid_patient_patch_does_not_change_saved_record(profile_client, invalid):
    created = profile_client.post('/api/pacientes', json=PATIENT).json()
    path = f"/api/pacientes/{created['id']}"
    response = profile_client.patch(path, json=invalid)
    assert response.status_code == 422
    assert profile_client.get(path).json() == created
    assert all('input' not in item for item in response.json()['detail'])


def test_patient_dates_are_validated_as_a_complete_result(profile_client):
    created = profile_client.post('/api/pacientes', json=PATIENT).json()
    path = f"/api/pacientes/{created['id']}"
    changes = {'fecha_nacimiento':'2027-01-01', 'fecha_inicio_seguimiento':'2028-01-01'}
    assert profile_client.patch(path, json=changes).status_code == 200
    assert profile_client.get(path).json() == created | changes


def test_deactivating_patient_preserves_admission_and_objectives(profile_client):
    created = profile_client.post('/api/pacientes', json=PATIENT).json()
    path = f"/api/pacientes/{created['id']}"
    admission = profile_client.put(path + '/admision', json={'fecha':'2026-01-01', 'motivo_consulta':'Motivo ficticio'})
    admission.raise_for_status()
    objective = profile_client.post(path + '/objetivos', json={'descripcion':'Objetivo ficticio', 'fecha_inicio':'2026-01-01'})
    assert objective.status_code == 201
    response = profile_client.patch(path, json={'activo':False})
    assert response.status_code == 200 and response.json()['activo'] is False
    assert profile_client.get(path + '/admision').json() == admission.json()
    assert profile_client.get(path + '/objetivos').json()['items'] == [objective.json()]
    assert profile_client.get('/api/pacientes').json()['items'][0]['activo'] is False


def test_patients_individual_routes_hide_foreign_and_missing_records(auth_app, profile_client):
    patient = profile_client.post('/api/pacientes', json=PATIENT).json()
    with TestClient(auth_app) as other:
        data = {'nombre':'Otro', 'apellido':'Prueba', 'email':'otro@example.com', 'password':'Password de prueba 123'}
        assert other.post('/api/auth/registro', json=data).status_code == 201
        assert other.post('/api/auth/login', json={key:data[key] for key in ('email','password')}).status_code == 200
        assert other.get('/api/pacientes').json()['total'] == 0
        for patient_id in [patient['id'], 2147483647]:
            assert other.get(f'/api/pacientes/{patient_id}').status_code == 404
            assert other.patch(f'/api/pacientes/{patient_id}', json={'activo':False}).status_code == 404
    assert profile_client.get(f"/api/pacientes/{patient['id']}").json()['activo'] is True


@pytest.mark.parametrize('invalid', [{'nombre':' '}, {'apellido':None}, {'fecha_nacimiento':0}, {'fecha_nacimiento':'2026-01-01T00:00:00'}, {'fecha_inicio_seguimiento':'2010-01-01'}, {'id':1}, {'paciente_id':1}, {'profesional_id':1}])
def test_invalid_patient_creation_does_not_insert_rows(profile_client, invalid):
    assert profile_client.post('/api/pacientes', json=PATIENT | invalid).status_code == 422
    assert profile_client.get('/api/pacientes').json()['total'] == 0
