from fastapi.testclient import TestClient
import pytest


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre','apellido':'Prueba','fecha_nacimiento':'2015-01-01','fecha_inicio_seguimiento':'2026-01-01'}
SESSION = {'fecha':'2026-01-01','presente':True}
OBJECTIVE = {'descripcion':'Objetivo ficticio','fecha_inicio':'2026-01-01'}


@pytest.fixture
def observations(profile_client):
    patient = profile_client.post('/api/pacientes',json=PATIENT).json()['id']
    session = profile_client.post(f'/api/pacientes/{patient}/sesiones',json=SESSION).json()['id']
    return profile_client,patient,session,f'/api/pacientes/{patient}/sesiones/{session}/observaciones'


def test_observations_persist_multiple_entries_and_optional_objective(observations):
    client,patient,session,path = observations
    assert client.get(path).json()['total'] == 0
    first = client.post(path,json={'contexto':' Contexto ficticio ','nota_libre':' '})
    second = client.post(path,json={'resultado':'Resultado ficticio'})
    assert first.status_code == second.status_code == 201
    assert first.json()['contexto'] == 'Contexto ficticio' and first.json()['nota_libre'] is None
    assert first.json()['objetivo_id'] is None
    assert [item['id'] for item in client.get(path).json()['items']] == [first.json()['id'],second.json()['id']]
    page = client.get(path+'?offset=1&limit=1').json()
    assert page['total'] == 2 and page['items'] == [second.json()]
    detail = f"{path}/{first.json()['id']}"
    assert client.get(detail).json() == first.json()
    changed = client.patch(detail,json={'resultado':'Nuevo resultado','contexto':None})
    assert changed.status_code == 200
    assert changed.json() == first.json() | {'resultado':'Nuevo resultado','contexto':None}
    assert client.patch(detail,json={'resultado':' '}).status_code == 422
    assert client.get(detail).json() == changed.json()
    assert client.patch(detail,json={}).json() == changed.json()


@pytest.mark.parametrize('body',[{}, {'nota_libre':' '}, {'contexto':None}, {'contexto':' ','resultado':'\t'}, {'nota_libre':123}, {'objetivo_id':0,'nota_libre':'Nota'}, {'objetivo_id':True,'nota_libre':'Nota'}, {'id':1,'nota_libre':'Nota'}, {'sesion_id':1,'nota_libre':'Nota'}, {'paciente_id':1,'nota_libre':'Nota'}])
def test_invalid_observation_creation_does_not_insert(observations,body):
    client,patient,session,path = observations
    assert client.post(path,json=body).status_code == 422
    assert client.get(path).json()['total'] == 0


def test_observation_can_link_change_and_unlink_objective_of_same_patient(observations):
    client,patient,session,path = observations
    objective_path = f'/api/pacientes/{patient}/objetivos'
    first = client.post(objective_path,json=OBJECTIVE).json()['id']
    second = client.post(objective_path,json=OBJECTIVE).json()['id']
    record = client.post(path,json={'nota_libre':'Nota ficticia','objetivo_id':first}).json()
    detail = f"{path}/{record['id']}"
    assert client.patch(detail,json={'objetivo_id':second}).json()['objetivo_id'] == second
    assert client.patch(detail,json={'objetivo_id':None}).json()['objetivo_id'] is None
    assert client.get(detail).json()['nota_libre'] == 'Nota ficticia'


def test_observation_rejects_objective_of_other_patient_even_same_professional(observations):
    client,patient,session,path = observations
    sibling = client.post('/api/pacientes',json=PATIENT).json()['id']
    wrong = client.post(f'/api/pacientes/{sibling}/objetivos',json=OBJECTIVE).json()['id']
    before = client.post(path,json={'nota_libre':'Nota ficticia'}).json()
    for target in [wrong,2147483647]:
        body = {'nota_libre':'Cambio ficticio','objetivo_id':target}
        assert client.post(path,json=body).status_code == 404
        assert client.patch(f"{path}/{before['id']}",json=body).status_code == 404
        assert client.get(f"{path}/{before['id']}").json() == before
    assert client.get(path).json()['total'] == 1


def test_observations_cannot_move_to_other_session_or_professional(observations,auth_app):
    client,patient,session,path = observations
    before = client.post(path,json={'nota_libre':'Nota ficticia'}).json()
    detail = f"{path}/{before['id']}"
    other_session = client.post(f'/api/pacientes/{patient}/sesiones',json=SESSION).json()['id']
    sibling_path = f"/api/pacientes/{patient}/sesiones/{other_session}/observaciones/{before['id']}"
    assert client.get(sibling_path).status_code == 404
    assert client.patch(sibling_path,json={}).status_code == 404
    assert client.patch(detail,json={'sesion_id':other_session}).status_code == 422
    with TestClient(auth_app) as other:
        account = {'nombre':'Otro','apellido':'Prueba','email':'otro@example.com','password':'Password de prueba 123'}
        assert other.post('/api/auth/registro',json=account).status_code == 201
        assert other.post('/api/auth/login',json={key:account[key] for key in ('email','password')}).status_code == 200
        own = other.post('/api/pacientes',json=PATIENT).json()['id']
        foreign_goal = other.post(f'/api/pacientes/{own}/objetivos',json=OBJECTIVE).json()['id']
        assert client.post(path,json={'nota_libre':'Nota','objetivo_id':foreign_goal}).status_code == 404
        assert client.patch(detail,json={'objetivo_id':foreign_goal}).status_code == 404
        assert other.get(path).status_code == 404
        assert other.post(path,json={'nota_libre':'Nota'}).status_code == 404
        assert other.get(detail).status_code == 404
        assert other.patch(detail,json={}).status_code == 404
    assert client.get(detail).json() == before
