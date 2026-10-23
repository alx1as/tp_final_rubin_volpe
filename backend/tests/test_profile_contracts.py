import socket

from fastapi.testclient import TestClient
import pytest

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def openapi():
    app = create_app(Settings(_env_file=None, database_url='postgresql+psycopg://localhost:1/contracts_test'))
    with TestClient(app) as client:
        response = client.get('/openapi.json')
        assert response.status_code == 200
        return response.json()


@pytest.mark.parametrize('path', ['/api/pacientes', '/api/pacientes/{paciente_id}/escolaridades', '/api/pacientes/{paciente_id}/profesionales-tratantes', '/api/pacientes/{paciente_id}/objetivos', '/api/pacientes/{paciente_id}/sesiones', '/api/pacientes/{paciente_id}/sesiones/{sesion_id}/observaciones', '/api/pacientes/{paciente_id}/objetivos/{objetivo_id}/observaciones'])
def test_profile_lists_expose_paginated_contract_and_limits(openapi, path):
    operation = openapi['paths'][path]['get']
    params = {item['name']:item['schema'] for item in operation['parameters']}
    assert params['offset']['default'] == 0 and params['offset']['minimum'] == 0
    assert params['limit']['default'] == 20 and params['limit']['minimum'] == 1 and params['limit']['maximum'] == 100
    ref = operation['responses']['200']['content']['application/json']['schema']['$ref']
    page = openapi['components']['schemas'][ref.rsplit('/',1)[1]]
    assert set(page['properties']) == {'items','total','offset','limit'}


def test_openapi_documents_put_compatibility_and_admission_codes(openapi):
    paths = openapi['paths']
    for path in ['/api/pacientes/{paciente_id}/escolaridades/{escolaridad_id}', '/api/pacientes/{paciente_id}/profesionales-tratantes/{profesional_tratante_id}', '/api/pacientes/{paciente_id}/objetivos/{objetivo_id}']:
        assert {'get','put','patch'} <= set(paths[path])
        assert paths[path]['put']['deprecated'] is True
        assert not paths[path]['patch'].get('deprecated',False)
    admission = paths['/api/pacientes/{paciente_id}/admision']
    assert {'200','201'} <= set(admission['put']['responses'])
    assert '$ref' in admission['get']['responses']['200']['content']['application/json']['schema']
    assert not any('delete' in operations for operations in paths.values())


def test_profile_database_unavailable_is_not_an_empty_list():
    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1',0))
        app = create_app(Settings(_env_file=None, database_url=f'postgresql+psycopg://test_user:synthetic_secret@127.0.0.1:{reserved.getsockname()[1]}/offline_test'))
        with TestClient(app) as client:
            client.cookies.set('sesion','x'*43)
            response = client.get('/api/pacientes')
            assert response.status_code == 503
            assert response.json() == {'detail':'Base de datos no disponible'}
            assert 'synthetic_secret' not in response.text


def test_followup_openapi_documents_attendance_and_derived_evidence_date(openapi):
    schemas = openapi['components']['schemas']
    assert {'fecha','presente'} <= set(schemas['SesionCrear']['required'])
    assert schemas['SesionCrear']['properties']['presente']['type'] == 'boolean'
    assert schemas['EvidenciaObjetivo']['properties']['fecha_sesion']['format'] == 'date'
    paths = openapi['paths']
    for path in ['/api/pacientes/{paciente_id}/sesiones/{sesion_id}', '/api/pacientes/{paciente_id}/sesiones/{sesion_id}/observaciones/{observacion_id}']:
        assert {'get','patch'} == set(paths[path])
