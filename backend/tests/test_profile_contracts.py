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


@pytest.mark.parametrize('path', [
    '/api/pacientes', '/api/pacientes/1/cronologia',
    '/api/pacientes/1/informes', '/api/pacientes/1/informes/1',
])
def test_profile_database_unavailable_is_not_an_empty_list(path):
    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1',0))
        app = create_app(Settings(_env_file=None, database_url=f'postgresql+psycopg://test_user:synthetic_secret@127.0.0.1:{reserved.getsockname()[1]}/offline_test'))
        with TestClient(app) as client:
            client.cookies.set('sesion','x'*43)
            response = client.get(path)
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


def test_chronology_openapi_exposes_dates_and_nested_observations(openapi):
    operation = openapi['paths']['/api/pacientes/{paciente_id}/cronologia']['get']
    params = {item['name']: item['schema'] for item in operation['parameters']}
    for field in ['desde', 'hasta']:
        assert {'type': 'string', 'format': 'date'} in params[field]['anyOf']
    assert params['limit']['maximum'] == 100
    entry = openapi['components']['schemas']['EntradaCronologia']
    assert {'id', 'paciente_id', 'fecha', 'presente', 'nota_general', 'observaciones'} == set(entry['properties'])


def test_report_openapi_documents_draft_creation_and_explicit_finalization(openapi):
    paths = openapi['paths']
    assert set(paths['/api/pacientes/{paciente_id}/informes']) == {'get', 'post'}
    assert set(paths['/api/pacientes/{paciente_id}/informes/{informe_id}']) == {'get', 'patch'}
    assert '201' in paths['/api/pacientes/{paciente_id}/informes']['post']['responses']
    schemas = openapi['components']['schemas']
    assert set(schemas['InformeCrear']['required']) == {'titulo', 'periodo_desde', 'periodo_hasta', 'contenido'}
    assert schemas['InformeCrear']['properties']['estado']['const'] == 'borrador'
    assert schemas['InformeCrear']['properties']['asistido_ia']['default'] is False
    assert schemas['InformeCrear']['additionalProperties'] is False
    assert schemas['InformeEditar']['additionalProperties'] is False


def test_integration_openapi_documents_multipart_and_temporary_draft(openapi):
    paths = openapi['paths']
    transcription = paths['/api/transcripciones']['post']
    body = transcription['requestBody']
    assert body['required'] is True
    ref = body['content']['multipart/form-data']['schema']['$ref']
    schema = openapi['components']['schemas'][ref.rsplit('/', 1)[1]]
    assert schema['required'] == ['audio']
    assert schema['properties']['audio']['type'] == 'string'
    assert schema['properties']['audio']['contentMediaType'] == 'application/octet-stream'
    generation = paths['/api/pacientes/{paciente_id}/informes/generar']['post']
    assert generation['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/BorradorGenerado')
    schemas = openapi['components']['schemas']
    draft = schemas['BorradorGenerado']['properties']
    assert not {'id', 'paciente_id'} & draft.keys()
    assert draft['estado']['const'] == 'borrador'
    assert draft['asistido_ia']['const'] is True
    assert schemas['SolicitudBorrador']['additionalProperties'] is False
    assert set(schemas['SolicitudBorrador']['required']) == {'titulo', 'periodo_desde', 'periodo_hasta'}


@pytest.mark.parametrize('path', ['/api/transcripciones', '/api/pacientes/1/informes/generar'])
def test_integration_routes_report_database_outage_without_private_details(path):
    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1', 0))
        app = create_app(Settings(_env_file=None, database_url=f'postgresql+psycopg://test_user:synthetic_secret@127.0.0.1:{reserved.getsockname()[1]}/offline_test'))
        with TestClient(app) as client:
            client.cookies.set('sesion', 'x' * 43)
            kwargs = {'files': {'audio': ('nota.webm', b'Audio ficticio', 'audio/webm')}} if path == '/api/transcripciones' else {
                'json': {'titulo': 'Informe ficticio', 'periodo_desde': '2026-01-01', 'periodo_hasta': '2026-01-31'},
            }
            response = client.post(path, **kwargs)
            assert response.status_code == 503
            assert response.json() == {'detail': 'Base de datos no disponible'}
            assert 'synthetic_secret' not in response.text
