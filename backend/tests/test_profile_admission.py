from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import event
from sqlmodel import Session, select

from app.models import Admision


pytestmark = pytest.mark.integration
PATIENT = {'nombre':'Nombre', 'apellido':'Prueba', 'fecha_nacimiento':'2015-01-01', 'fecha_inicio_seguimiento':'2026-01-01'}
ADMISSION = {'fecha':'2026-01-01', 'motivo_consulta':' Motivo ficticio ', 'antecedentes_personales':'   ', 'observaciones':' Nota ficticia '}


def admission_path(client):
    patient = client.post('/api/pacientes', json=PATIENT)
    assert patient.status_code == 201
    return f"/api/pacientes/{patient.json()['id']}/admision"


def test_admission_absent_create_replace_and_optional_nulls(profile_client, auth_app):
    path = admission_path(profile_client)
    assert profile_client.get(path).status_code == 404
    created = profile_client.put(path, json=ADMISSION)
    assert created.status_code == 201
    assert created.json()['motivo_consulta'] == 'Motivo ficticio'
    assert created.json()['antecedentes_personales'] is None
    assert created.json()['observaciones'] == 'Nota ficticia'
    assert profile_client.get(path).json() == created.json()
    replaced = profile_client.put(path, json={'fecha':'2026-02-01', 'motivo_consulta':'Nuevo motivo'})
    assert replaced.status_code == 200
    assert replaced.json()['id'] == created.json()['id']
    assert replaced.json()['observaciones'] is None
    assert profile_client.get(path).json() == replaced.json()
    with Session(auth_app.state.engine) as session:
        assert len(session.exec(select(Admision)).all()) == 1


@pytest.mark.parametrize('invalid', [{'fecha':'incorrecta'}, {'fecha':0}, {'fecha':None}, {'motivo_consulta':'   '}, {'motivo_consulta':None}, {'id':1}, {'paciente_id':1}, {'profesional_id':1}, {'observaciones':123}])
def test_invalid_admission_replacement_preserves_record(profile_client, invalid):
    path = admission_path(profile_client)
    before = profile_client.put(path, json=ADMISSION).json()
    response = profile_client.put(path, json=ADMISSION | invalid)
    assert response.status_code == 422
    assert profile_client.get(path).json() == before


def test_concurrent_admission_creation_returns_safe_conflict_and_recovers(profile_client, auth_app):
    path = admission_path(profile_client)
    barrier = Barrier(2)

    def after_select(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().startswith('SELECT ') and 'WHERE admision.paciente_id' in statement:
            barrier.wait(timeout=15)

    engine = auth_app.state.engine
    event.listen(engine, 'after_cursor_execute', after_select)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(profile_client.put, path, json=ADMISSION) for _ in range(2)]
            responses = [future.result(timeout=25) for future in futures]
    finally:
        event.remove(engine, 'after_cursor_execute', after_select)
    assert sorted(response.status_code for response in responses) == [201,409]
    conflict = next(response for response in responses if response.status_code == 409)
    assert conflict.json() == {'detail':'Conflicto de integridad'}
    assert 'INSERT' not in conflict.text and 'Motivo ficticio' not in conflict.text
    with Session(engine) as session:
        assert len(session.exec(select(Admision)).all()) == 1
    assert profile_client.put(path, json=ADMISSION).status_code == 200
    assert profile_client.get(path).status_code == 200
