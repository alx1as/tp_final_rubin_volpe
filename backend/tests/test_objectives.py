from datetime import date

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Objetivo
from app.services.perfil import guardar


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre','apellido':'Prueba','fecha_nacimiento':'2015-01-01','fecha_inicio_seguimiento':'2026-01-01'}
OBJECTIVE = {'descripcion':' Objetivo ficticio ','fecha_inicio':'2026-01-01','observaciones_generales':'  '}


@pytest.fixture
def objectives(profile_client):
    response = profile_client.post('/api/pacientes',json=PATIENT)
    assert response.status_code == 201
    return profile_client, f"/api/pacientes/{response.json()['id']}/objetivos"


def test_objectives_create_paginate_consult_patch_and_replace(objectives):
    client,path = objectives
    assert client.get(path).json() == {'items':[],'total':0,'offset':0,'limit':20}
    responses = [
        client.post(path,json=OBJECTIVE),
        client.post(path,json=OBJECTIVE | {'estado':'cumplido','fecha_cierre':'2026-02-01'}),
        client.post(path,json=OBJECTIVE | {'estado':'cerrado','fecha_inicio':'2027-01-01','fecha_cierre':'2027-02-01'}),
    ]
    assert all(response.status_code == 201 for response in responses)
    records = [response.json() for response in responses]
    ids = [record['id'] for record in records]
    assert records[0]['descripcion'] == 'Objetivo ficticio'
    assert records[0]['observaciones_generales'] is None
    assert records[0]['estado'] == 'activo' and records[0]['fecha_cierre'] is None
    assert [item['id'] for item in client.get(path+'?limit=100').json()['items']] == ids[::-1]
    page = client.get(path+'?offset=1&limit=1').json()
    assert page['total'] == 3 and page['offset'] == page['limit'] == 1
    assert page['items'][0]['id'] == ids[1]
    assert client.get(path+'?offset=99').json() == {'items':[],'total':3,'offset':99,'limit':20}
    detail = f'{path}/{ids[0]}'
    assert client.get(detail).json() == records[0]
    updated = client.patch(detail,json={'descripcion':' Revisado ','observaciones_generales':' Nota ficticia '})
    assert updated.status_code == 200
    assert updated.json() == records[0] | {'descripcion':'Revisado','observaciones_generales':'Nota ficticia'}
    assert client.patch(detail,json={}).json() == updated.json()
    assert client.patch(detail,json={'observaciones_generales':None}).json()['observaciones_generales'] is None
    replaced = client.put(detail,json={'descripcion':'Reemplazo','fecha_inicio':'2026-03-01'})
    assert replaced.status_code == 200 and replaced.json()['id'] == ids[0]
    assert replaced.json()['observaciones_generales'] is None
    assert client.get(detail).json() == replaced.json()
    assert client.put(detail,json={'observaciones_generales':'Parcial'}).status_code == 422
    assert client.delete(detail).status_code == 405
    assert client.get(detail).json() == replaced.json()


@pytest.mark.parametrize('state',['cumplido','cerrado'])
def test_objective_closes_atomically_and_reopens_with_valid_pair(objectives,auth_app,state):
    client,path = objectives
    created = client.post(path,json=OBJECTIVE).json()
    detail = f"{path}/{created['id']}"
    assert client.patch(detail,json={'estado':state}).status_code == 422
    assert client.patch(detail,json={'fecha_cierre':'2026-02-01'}).status_code == 422
    assert client.get(detail).json() == created
    statements = []

    def record_update(connection,cursor,statement,parameters,context,executemany):
        if statement.lstrip().startswith('UPDATE objetivo '):
            statements.append(statement)

    engine = auth_app.state.engine
    event.listen(engine,'before_cursor_execute',record_update)
    try:
        changes = {'estado':state,'fecha_cierre':'2026-02-01'}
        response = client.patch(detail,json=changes)
    finally:
        event.remove(engine,'before_cursor_execute',record_update)
    assert response.status_code == 200
    assert response.json() == created | changes
    assert len(statements) == 1 and 'estado=' in statements[0] and 'fecha_cierre=' in statements[0]
    assert client.patch(detail,json={'estado':'activo'}).status_code == 422
    assert client.get(detail).json() == response.json()
    reopened = client.patch(detail,json={'estado':'activo','fecha_cierre':None})
    assert reopened.status_code == 200 and reopened.json() == created


@pytest.mark.parametrize('invalid', [
    {'descripcion':None}, {'descripcion':' '}, {'estado':None}, {'estado':'invalido'},
    {'estado':'cumplido'}, {'estado':'cerrado'}, {'fecha_inicio':None},
    {'fecha_inicio':0}, {'fecha_inicio':'2026-01-01T00:00:00'},
    {'fecha_cierre':'2026-02-01'}, {'fecha_cierre':0}, {'observaciones_generales':123},
    {'id':999}, {'paciente_id':999}, {'profesional_id':999},
])
def test_invalid_objective_patch_and_creation_leave_data_intact(objectives,invalid):
    client,path = objectives
    created = client.post(path,json=OBJECTIVE).json()
    detail = f"{path}/{created['id']}"
    response = client.patch(detail,json=invalid)
    assert response.status_code == 422
    assert client.get(detail).json() == created
    assert client.post(path,json=OBJECTIVE | invalid).status_code == 422
    assert client.get(path).json()['total'] == 1
    assert all('input' not in error for error in response.json()['detail'])


@pytest.mark.parametrize('state',['cumplido','cerrado'])
def test_objective_dates_validate_against_complete_saved_state(objectives,state):
    client,path = objectives
    body = OBJECTIVE | {'estado':state,'fecha_cierre':'2026-03-01'}
    created = client.post(path,json=body).json()
    detail = f"{path}/{created['id']}"
    for invalid in [{'fecha_cierre':None},{'fecha_cierre':''},{'fecha_cierre':'2025-01-01'},{'fecha_inicio':'2027-01-01'}]:
        assert client.patch(detail,json=invalid).status_code == 422
        assert client.get(detail).json() == created
    changes = {'fecha_inicio':'2027-01-01','fecha_cierre':'2027-02-01'}
    assert client.patch(detail,json=changes).json() == created | changes
    assert client.get(detail).json() == created | changes


@pytest.mark.parametrize('query',['offset=-1','limit=0','limit=101','limit=abc'])
def test_objective_pagination_rejects_invalid_values(objectives,query):
    client,path = objectives
    assert client.get(path+'?'+query).status_code == 422


def test_objective_blank_closure_on_active_means_null(objectives):
    client,path = objectives
    created = client.post(path,json=OBJECTIVE | {'fecha_cierre':'  '})
    assert created.status_code == 201 and created.json()['fecha_cierre'] is None
    detail = f"{path}/{created.json()['id']}"
    assert client.patch(detail,json={'fecha_cierre':''}).json() == created.json()


def test_objective_ids_are_scoped_to_patient_and_professional(objectives,auth_app):
    client,path = objectives
    created = client.post(path,json=OBJECTIVE).json()
    objective_id = created['id']
    sibling_id = client.post('/api/pacientes',json=PATIENT).json()['id']
    sibling_path = f'/api/pacientes/{sibling_id}/objetivos/{objective_id}'
    assert client.get(sibling_path).status_code == 404
    assert client.patch(sibling_path,json={'descripcion':'Cambio'}).status_code == 404
    assert client.put(sibling_path,json=OBJECTIVE).status_code == 404
    with TestClient(auth_app) as other:
        account = {'nombre':'Otro','apellido':'Prueba','email':'otro@example.com','password':'Password de prueba 123'}
        assert other.post('/api/auth/registro',json=account).status_code == 201
        assert other.post('/api/auth/login',json={key:account[key] for key in ('email','password')}).status_code == 200
        other_id = other.post('/api/pacientes',json=PATIENT).json()['id']
        other_path = f'/api/pacientes/{other_id}/objetivos'
        assert other.post(other_path,json=OBJECTIVE).status_code == 201
        assert other.get(other_path).json()['total'] == 1
        assert other.get(path).status_code == 404
        assert other.post(path,json=OBJECTIVE).status_code == 404
        for bad_path in [f'{path}/{objective_id}',f'{other_path}/{objective_id}']:
            assert other.get(bad_path).status_code == 404
            assert other.patch(bad_path,json={}).status_code == 404
            assert other.put(bad_path,json=OBJECTIVE).status_code == 404
    assert client.get(path).json()['total'] == 1
    assert client.get(f'{path}/{objective_id}').json() == created
    for method in ['get','patch','put']:
        response = client.request(method.upper(),f'{path}/2147483647',json=OBJECTIVE if method == 'put' else {})
        assert response.status_code == 404


@pytest.mark.parametrize('invalid',[
    {'estado':'invalido'}, {'estado':'activo','fecha_cierre':date(2026,2,1)},
    {'estado':'cumplido'}, {'estado':'cerrado','fecha_cierre':date(2025,1,1)},
    {'descripcion':''},
])
def test_database_enforces_objective_constraints_and_rolls_back(objectives,auth_app,invalid):
    client,path = objectives
    patient_id = int(path.split('/')[3])
    values = {'paciente_id':patient_id,'descripcion':'Objetivo ficticio','fecha_inicio':date(2026,1,1)} | invalid
    with Session(auth_app.state.engine) as session:
        with pytest.raises(IntegrityError):
            guardar(session,Objetivo(**values))
        assert session.is_active
    assert client.get(path).json()['total'] == 0
