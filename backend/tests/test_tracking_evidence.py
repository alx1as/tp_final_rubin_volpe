from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session

from app.models import Observacion


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre','apellido':'Prueba','fecha_nacimiento':'2015-01-01','fecha_inicio_seguimiento':'2026-01-01'}
GOAL = {'descripcion':'Objetivo ficticio','fecha_inicio':'2026-01-01'}


def test_evidence_order_pagination_filters_and_current_session_date(profile_client,auth_app):
    client = profile_client
    patient = client.post('/api/pacientes',json=PATIENT).json()['id']
    base = f'/api/pacientes/{patient}'
    goal = client.post(base+'/objetivos',json=GOAL).json()['id']
    other_goal = client.post(base+'/objetivos',json=GOAL).json()['id']
    path = f'{base}/objetivos/{goal}/observaciones'
    assert client.get(path).json() == {'items':[],'total':0,'offset':0,'limit':20}
    sessions = [client.post(base+'/sesiones',json={'fecha':day,'presente':True}).json()['id'] for day in ['2026-01-01','2026-02-01','2026-02-01']]
    records = []
    for session_id in [sessions[0],sessions[2],sessions[1]]:
        response = client.post(f'{base}/sesiones/{session_id}/observaciones',json={'nota_libre':'Nota ficticia','objetivo_id':goal})
        assert response.status_code == 201
        records.append(response.json())
    other_path = f'{base}/sesiones/{sessions[1]}/observaciones'
    assert client.post(other_path,json={'nota_libre':'Sin objetivo'}).status_code == 201
    assert client.post(other_path,json={'nota_libre':'Otro objetivo','objetivo_id':other_goal}).status_code == 201
    # Una referencia cruzada introducida fuera de la API tampoco debe filtrarse
    # en la consulta. La base solo tiene FK; la regla de paciente es de la API.
    sibling = client.post('/api/pacientes',json=PATIENT).json()['id']
    sibling_session = client.post(f'/api/pacientes/{sibling}/sesiones',json={'fecha':'2027-01-01','presente':True}).json()['id']
    crossed = client.post(f'/api/pacientes/{sibling}/sesiones/{sibling_session}/observaciones',json={'nota_libre':'Nota ficticia'}).json()['id']
    with Session(auth_app.state.engine) as session:
        record = session.get(Observacion,crossed)
        record.objetivo_id = goal
        session.add(record)
        session.commit()
    result = client.get(path).json()
    assert result['total'] == 3
    assert [item['id'] for item in result['items']] == [record['id'] for record in records[::-1]]
    assert [item['fecha_sesion'] for item in result['items']] == ['2026-02-01','2026-02-01','2026-01-01']
    page = client.get(path+'?offset=1&limit=1').json()
    assert page['total'] == 3 and page['items'][0]['id'] == records[1]['id']
    assert client.get(path+'?offset=99').json()['items'] == []
    assert client.patch(f'{base}/sesiones/{sessions[0]}',json={'fecha':'2026-03-01'}).status_code == 200
    assert client.get(path).json()['items'][0]['id'] == records[0]['id']
    first_path = f"{base}/sesiones/{sessions[0]}/observaciones/{records[0]['id']}"
    assert client.patch(first_path,json={'objetivo_id':None}).status_code == 200
    assert client.get(path).json()['total'] == 2


def test_evidence_hides_foreign_goal_parent_and_missing_goal(profile_client,auth_app):
    client = profile_client
    patient = client.post('/api/pacientes',json=PATIENT).json()['id']
    sibling = client.post('/api/pacientes',json=PATIENT).json()['id']
    goal = client.post(f'/api/pacientes/{patient}/objetivos',json=GOAL).json()['id']
    path = f'/api/pacientes/{patient}/objetivos/{goal}/observaciones'
    assert client.get(f'/api/pacientes/{sibling}/objetivos/{goal}/observaciones').status_code == 404
    assert client.get(f'/api/pacientes/{patient}/objetivos/2147483647/observaciones').status_code == 404
    with TestClient(auth_app) as other:
        account = {'nombre':'Otro','apellido':'Prueba','email':'otro@example.com','password':'Password de prueba 123'}
        assert other.post('/api/auth/registro',json=account).status_code == 201
        assert other.post('/api/auth/login',json={key:account[key] for key in ('email','password')}).status_code == 200
        assert other.get(path).status_code == 404


@pytest.mark.parametrize('query',['offset=-1','limit=0','limit=101'])
def test_evidence_rejects_invalid_pagination(profile_client,query):
    patient = profile_client.post('/api/pacientes',json=PATIENT).json()['id']
    goal = profile_client.post(f'/api/pacientes/{patient}/objetivos',json=GOAL).json()['id']
    assert profile_client.get(f'/api/pacientes/{patient}/objetivos/{goal}/observaciones?{query}').status_code == 422
