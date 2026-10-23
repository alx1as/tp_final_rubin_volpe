from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, select

from app.models import Profesional


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre', 'apellido':'Prueba', 'fecha_nacimiento':'2015-01-01', 'fecha_inicio_seguimiento':'2026-01-01'}
PERIODS = {
    'profesionales-tratantes': {
        'required': 'nombre',
        'body': {'nombre':'Contacto ficticio', 'especialidad':'Especialidad', 'contacto':'contacto@example.com', 'fecha_inicio':'2026-01-01', 'fecha_fin':'2026-12-01', 'observaciones':'Nota ficticia'},
        'required_fields': ['nombre','especialidad','fecha_inicio'],
    },
    'escolaridades': {
        'required': 'institucion',
        'body': {'institucion':'Institucion ficticia', 'nivel':'Primario', 'grado_anio_sala':'1', 'modalidad':'Comun', 'jornada':'Simple', 'fecha_inicio':'2026-01-01', 'fecha_fin':'2026-12-01', 'apoyos':'Apoyo ficticio', 'observaciones':'Nota ficticia', 'referente_nombre':'Referente', 'referente_rol':'Docente', 'referente_contacto':'Contacto ficticio'},
        'required_fields': ['institucion','nivel','grado_anio_sala','modalidad','fecha_inicio'],
    },
}


@pytest.fixture(params=PERIODS)
def period(request, profile_client):
    resource = request.param
    patient = profile_client.post('/api/pacientes', json=PATIENT)
    assert patient.status_code == 201
    path = f"/api/pacientes/{patient.json()['id']}/{resource}"
    return profile_client, resource, path, PERIODS[resource]


def test_period_create_paginate_consult_patch_and_full_put(period, auth_app):
    client, resource, path, case = period
    body = case['body']
    assert client.get(path).json() == {'items': [], 'total':0, 'offset':0, 'limit':20}
    responses = [client.post(path, json=body), client.post(path, json=body | {'fecha_fin':None}), client.post(path, json=body | {'fecha_inicio':'2027-01-01', 'fecha_fin':None})]
    assert all(response.status_code == 201 for response in responses)
    ids = [response.json()['id'] for response in responses]
    items = client.get(path + '?limit=100').json()['items']
    assert [item['id'] for item in items] == ids[::-1]
    assert sum(item['fecha_fin'] is None for item in items) == 2
    page = client.get(path + '?offset=1&limit=1').json()
    assert page['total'] == 3 and page['items'][0]['id'] == ids[1]
    assert client.get(path + '?offset=99').json()['items'] == []
    detail = f'{path}/{ids[0]}'
    before = client.get(detail).json()
    for field, value in body.items():
        assert before[field] == value
    changed = client.patch(detail, json={case['required']:' Nuevo ', 'fecha_fin':'  ', 'observaciones':'   '})
    assert changed.status_code == 200
    assert changed.json() == before | {case['required']:'Nuevo', 'fecha_fin':None, 'observaciones':None}
    assert client.patch(detail, json={}).json() == changed.json()
    assert client.get(detail).json() == changed.json()
    complete = {key:body[key] for key in case['required_fields']}
    replaced = client.put(detail, json=complete)
    assert replaced.status_code == 200 and replaced.json()['id'] == ids[0]
    assert replaced.json()['observaciones'] is None and replaced.json()['fecha_fin'] is None
    assert client.put(detail, json={'observaciones':'Parcial'}).status_code == 422
    with Session(auth_app.state.engine) as session:
        assert len(session.exec(select(Profesional)).all()) == 1


@pytest.mark.parametrize('invalid_case', ['null_required','blank_required','null_start','end_before_start','start_after_end','bad_date','bad_optional','id','paciente_id','profesional_id'])
def test_invalid_period_patch_and_creation_preserve_data(period, invalid_case):
    client, resource, path, case = period
    body = case['body']
    invalid = {
        'null_required': {case['required']:None},
        'blank_required': {case['required']:'   '},
        'null_start': {'fecha_inicio':None},
        'end_before_start': {'fecha_fin':'2025-01-01'},
        'start_after_end': {'fecha_inicio':'2027-01-01'},
        'bad_date': {'fecha_fin':0},
        'bad_optional': {'observaciones':123},
        'id': {'id':999}, 'paciente_id':{'paciente_id':999}, 'profesional_id':{'profesional_id':999},
    }[invalid_case]
    created = client.post(path, json=body).json()
    detail = f"{path}/{created['id']}"
    response = client.patch(detail, json=invalid)
    assert response.status_code == 422
    assert client.get(detail).json() == created
    assert client.post(path, json=body | invalid).status_code == 422
    assert client.get(path).json()['total'] == 1


@pytest.mark.parametrize('query', ['limit=0','limit=101','offset=-1'])
def test_period_pagination_rejects_invalid_values(period, query):
    client, resource, path, case = period
    assert client.get(path + '?' + query).status_code == 422


def test_period_identity_is_scoped_to_patient_and_professional(period, auth_app):
    client, resource, path, case = period
    created = client.post(path, json=case['body']).json()
    child_id = created['id']
    sibling = client.post('/api/pacientes', json=PATIENT).json()['id']
    sibling_path = f'/api/pacientes/{sibling}/{resource}/{child_id}'
    assert client.get(sibling_path).status_code == 404
    assert client.patch(sibling_path, json={'observaciones':'Cambio'}).status_code == 404
    assert client.put(sibling_path, json=case['body']).status_code == 404
    with TestClient(auth_app) as other:
        account = {'nombre':'Otro','apellido':'Prueba','email':'otro@example.com','password':'Password de prueba 123'}
        assert other.post('/api/auth/registro', json=account).status_code == 201
        assert other.post('/api/auth/login', json={key:account[key] for key in ('email','password')}).status_code == 200
        other_patient = other.post('/api/pacientes', json=PATIENT).json()['id']
        assert other.get(path).status_code == 404
        assert other.post(path, json=case['body']).status_code == 404
        assert other.get(f'{path}/{child_id}').status_code == 404
        assert other.patch(f'{path}/{child_id}', json={}).status_code == 404
        assert other.patch(f'/api/pacientes/{other_patient}/{resource}/{child_id}', json={}).status_code == 404
        assert other.get(f'/api/pacientes/{other_patient}/{resource}').json()['total'] == 0
    assert client.get(f'{path}/{child_id}').json() == created


def test_period_blank_optionals_and_combined_date_edit(period):
    client, resource, path, case = period
    body = case['body'] | {'fecha_fin':' ', 'observaciones':' '}
    created = client.post(path, json=body)
    assert created.status_code == 201
    assert created.json()['fecha_fin'] is None and created.json()['observaciones'] is None
    detail = f"{path}/{created.json()['id']}"
    changes = {'fecha_inicio':'2027-01-01', 'fecha_fin':'2028-01-01'}
    updated = client.patch(detail, json=changes)
    assert updated.status_code == 200
    assert client.get(detail).json() == created.json() | changes
