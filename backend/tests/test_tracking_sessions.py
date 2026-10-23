from fastapi.testclient import TestClient
import pytest


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre','apellido':'Prueba','fecha_nacimiento':'2015-01-01','fecha_inicio_seguimiento':'2026-01-01'}
SESSION = {'fecha':'2026-01-01','presente':True,'nota_general':' Nota ficticia '}


@pytest.fixture
def sessions(profile_client):
    patient = profile_client.post('/api/pacientes',json=PATIENT).json()
    return profile_client,f"/api/pacientes/{patient['id']}/sesiones"


def test_sessions_persist_absence_paginate_and_edit_without_observations(sessions):
    client,path = sessions
    assert client.get(path).json() == {'items':[],'total':0,'offset':0,'limit':20}
    responses = [client.post(path,json=SESSION),client.post(path,json=SESSION | {'presente':False,'nota_general':' '}),client.post(path,json=SESSION | {'fecha':'2026-02-01'})]
    assert all(response.status_code == 201 for response in responses)
    records = [response.json() for response in responses]
    assert records[1]['presente'] is False and records[1]['nota_general'] is None
    assert [item['id'] for item in client.get(path).json()['items']] == [record['id'] for record in records[::-1]]
    page = client.get(path+'?offset=1&limit=1').json()
    assert page['total'] == 3 and page['items'] == [records[1]]
    detail = f"{path}/{records[0]['id']}"
    assert client.get(detail).json() == records[0]
    changed = client.patch(detail,json={'presente':False,'nota_general':''})
    assert changed.status_code == 200
    assert changed.json() == records[0] | {'presente':False,'nota_general':None}
    assert client.patch(detail,json={}).json() == changed.json()
    assert client.get(detail).json() == changed.json()


@pytest.mark.parametrize('invalid',[{'fecha':None},{'fecha':0},{'fecha':'2026-01-01T00:00:00'},{'presente':None},{'presente':0},{'presente':'false'},{'nota_general':123},{'id':1},{'paciente_id':1},{'profesional_id':1}])
def test_invalid_session_changes_do_not_alter_data(sessions,invalid):
    client,path = sessions
    before = client.post(path,json=SESSION).json()
    detail = f"{path}/{before['id']}"
    assert client.patch(detail,json=invalid).status_code == 422
    assert client.post(path,json=SESSION | invalid).status_code == 422
    assert client.get(detail).json() == before
    assert client.get(path).json()['total'] == 1


def test_session_requires_explicit_attendance(sessions):
    client,path = sessions
    assert client.post(path,json={'fecha':'2026-01-01'}).status_code == 422
    assert client.get(path).json()['total'] == 0


def test_sessions_cannot_be_read_or_edited_through_another_parent(sessions,auth_app):
    client,path = sessions
    record = client.post(path,json=SESSION).json()
    sibling = client.post('/api/pacientes',json=PATIENT).json()['id']
    for method in ['GET','PATCH']:
        assert client.request(method,f"/api/pacientes/{sibling}/sesiones/{record['id']}",json={}).status_code == 404
        assert client.request(method,path+'/2147483647',json={}).status_code == 404
    with TestClient(auth_app) as other:
        account = {'nombre':'Otro','apellido':'Prueba','email':'otro@example.com','password':'Password de prueba 123'}
        assert other.post('/api/auth/registro',json=account).status_code == 201
        assert other.post('/api/auth/login',json={key:account[key] for key in ('email','password')}).status_code == 200
        assert other.get(path).status_code == 404
        assert other.post(path,json=SESSION).status_code == 404
        assert other.get(f"{path}/{record['id']}").status_code == 404
        assert other.patch(f"{path}/{record['id']}",json={}).status_code == 404
