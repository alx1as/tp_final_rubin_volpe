from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Observacion, Sesion
from app.services.perfil import guardar


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre','apellido':'Prueba','fecha_nacimiento':'2015-01-01','fecha_inicio_seguimiento':'2026-01-01'}


@pytest.fixture
def tracking(profile_client):
    patient = profile_client.post('/api/pacientes',json=PATIENT).json()['id']
    base = f'/api/pacientes/{patient}'
    session = profile_client.post(base+'/sesiones',json={'fecha':'2026-01-01','presente':True}).json()['id']
    return profile_client,patient,session,base


@pytest.mark.parametrize('field',['contexto','conducta_observable','intervencion','resultado','nota_libre'])
def test_each_observation_text_field_can_supply_minimum_content(tracking,field):
    client,patient,session,base = tracking
    path = f'{base}/sesiones/{session}/observaciones'
    response = client.post(path,json={field:' Texto ficticio '})
    assert response.status_code == 201 and response.json()[field] == 'Texto ficticio'
    assert client.get(f"{path}/{response.json()['id']}").json() == response.json()


@pytest.mark.parametrize('invalid',['missing_attendance','empty_observation','missing_session','missing_goal'])
def test_database_followup_constraints_and_rollback(tracking,auth_app,invalid):
    client,patient,session_id,base = tracking
    if invalid == 'missing_attendance':
        record = Sesion(paciente_id=patient,fecha=date(2026,1,1),presente=None)
    elif invalid == 'empty_observation':
        record = Observacion(sesion_id=session_id)
    elif invalid == 'missing_session':
        record = Observacion(sesion_id=2147483647,nota_libre='Nota ficticia')
    else:
        record = Observacion(sesion_id=session_id,objetivo_id=2147483647,nota_libre='Nota ficticia')
    with Session(auth_app.state.engine) as session:
        with pytest.raises(IntegrityError):
            guardar(session,record)
        assert session.is_active
    assert client.get(base+'/sesiones').json()['total'] == 1
    assert client.get(f'{base}/sesiones/{session_id}/observaciones').json()['total'] == 0


def test_deactivation_preserves_all_followup_sources_without_delete(tracking):
    client,patient,session,base = tracking
    goal = client.post(base+'/objetivos',json={'descripcion':'Objetivo ficticio','fecha_inicio':'2026-01-01'}).json()
    observations = f'{base}/sesiones/{session}/observaciones'
    observation = client.post(observations,json={'nota_libre':'Nota ficticia','objetivo_id':goal['id']}).json()
    session_before = client.get(f'{base}/sesiones/{session}').json()
    assert client.patch(base,json={'activo':False}).status_code == 200
    for path,expected in [(f"{base}/objetivos/{goal['id']}",goal),(f'{base}/sesiones/{session}',session_before),(f"{observations}/{observation['id']}",observation)]:
        assert client.delete(path).status_code == 405
        assert client.get(path).json() == expected
    evidence = client.get(f"{base}/objetivos/{goal['id']}/observaciones").json()
    assert evidence['total'] == 1 and evidence['items'][0]['id'] == observation['id']
