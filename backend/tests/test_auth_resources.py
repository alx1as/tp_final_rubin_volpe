from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, select

from app.models import Profesional


pytestmark = pytest.mark.integration
PASSWORD = 'Password de prueba 123'
PATIENT = {'nombre': 'Paciente', 'apellido': 'Prueba', 'fecha_nacimiento': '2015-01-01', 'fecha_inicio_seguimiento': '2026-01-01'}
ADMISSION = {'fecha': '2026-01-01', 'motivo_consulta': 'Motivo ficticio'}
CHILDREN = {
    'escolaridades': {'institucion': 'Institucion ficticia', 'nivel': 'Primario', 'grado_anio_sala': '1', 'modalidad': 'Comun', 'fecha_inicio': '2026-01-01'},
    'profesionales-tratantes': {'nombre': 'Contacto ficticio', 'especialidad': 'Especialidad', 'fecha_inicio': '2026-01-01'},
    'objetivos': {'descripcion': 'Objetivo ficticio', 'fecha_inicio': '2026-01-01'},
}
OPERATIONS = [('GET', '/api/pacientes'), ('POST', '/api/pacientes'), ('GET', '/api/pacientes/1/admision'), ('PUT', '/api/pacientes/1/admision')]
for child in CHILDREN:
    OPERATIONS.extend([('GET', f'/api/pacientes/1/{child}'), ('POST', f'/api/pacientes/1/{child}'), ('PUT', f'/api/pacientes/1/{child}/1')])


def authenticate(client, email):
    response = client.post('/api/auth/registro', json={'nombre': 'Nombre', 'apellido': 'Prueba', 'email': email, 'password': PASSWORD})
    assert response.status_code == 201
    assert client.post('/api/auth/login', json={'email': email, 'password': PASSWORD}).status_code == 200
    return response.json()['id']


@pytest.mark.parametrize('method,path', OPERATIONS)
def test_all_existing_domain_operations_require_session(auth_app, method, path):
    with TestClient(auth_app) as client:
        response = client.request(method, path, json={} if method != 'GET' else None)
        assert response.status_code == 401


def test_all_existing_domain_operations_recheck_professional_active(auth_app):
    with TestClient(auth_app) as client:
        user_id = authenticate(client, 'inactivo@example.com')
        with Session(auth_app.state.engine) as session:
            user = session.get(Profesional, user_id)
            user.activo = False
            session.add(user)
            session.commit()
        for method, path in OPERATIONS:
            response = client.request(method, path, json={} if method != 'GET' else None)
            assert response.status_code == 401, (method, path)


def test_domain_isolation_between_professionals_and_nested_patients(auth_app):
    with TestClient(auth_app) as first, TestClient(auth_app) as second:
        first_id = authenticate(first, 'primero@example.com')
        second_id = authenticate(second, 'segundo@example.com')
        assert first_id != second_id
        own = first.post('/api/pacientes', json=PATIENT)
        assert own.status_code == 201
        own_id = own.json()['id']
        sibling_id = first.post('/api/pacientes', json=PATIENT | {'nombre': 'Otro'}).json()['id']
        other_id = second.post('/api/pacientes', json=PATIENT).json()['id']
        assert {item['id'] for item in first.get('/api/pacientes').json()} == {own_id, sibling_id}
        assert [item['id'] for item in second.get('/api/pacientes').json()] == [other_id]
        assert first.post('/api/pacientes', json=PATIENT | {'profesional_id': second_id}).status_code == 422
        path = f'/api/pacientes/{own_id}'
        assert first.put(path + '/admision', json=ADMISSION).status_code == 200
        assert second.get(path + '/admision').status_code == 404
        assert second.put(path + '/admision', json=ADMISSION).status_code == 404
        for resource, body in CHILDREN.items():
            created = first.post(path + '/' + resource, json=body)
            assert created.status_code == 201
            child_id = created.json()['id']
            assert first.get(path + '/' + resource).json()[0]['id'] == child_id
            assert second.get(path + '/' + resource).status_code == 404
            assert second.post(path + '/' + resource, json=body).status_code == 404
            assert second.put(path + f'/{resource}/{child_id}', json=body).status_code == 404
            assert second.put(f'/api/pacientes/{other_id}/{resource}/{child_id}', json=body).status_code == 404
            assert first.put(f'/api/pacientes/{sibling_id}/{resource}/{child_id}', json=body).status_code == 404
            assert first.put(path + f'/{resource}/{child_id}', json=body).status_code == 200
            assert second.get(f'/api/pacientes/{other_id}/{resource}').json() == []
            assert first.get(f'/api/pacientes/2147483647/{resource}').status_code == 404
        assert first.get('/api/pacientes/2147483647/admision').status_code == 404
