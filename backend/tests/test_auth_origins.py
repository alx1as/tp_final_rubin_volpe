import socket

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def origin_client():
    app = create_app(Settings(_env_file=None, database_url='postgresql+psycopg://localhost:1/origin_test', allowed_origins=['http://localhost:5173']))

    @app.api_route('/mutation', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
    def mutation():
        return {'ok': True}

    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize('method', ['POST', 'PUT', 'PATCH', 'DELETE'])
@pytest.mark.parametrize('origin', ['https://externo.example', 'null', 'http://localhost:5173.evil.example', 'http://localhost:5173/path', 'http://usuario@localhost:5173'])
def test_mutations_reject_untrusted_origins(origin_client, method, origin):
    response = origin_client.request(method, '/mutation', headers={'Origin': origin})
    assert response.status_code == 403
    assert response.json() == {'detail': 'Origen no permitido'}


@pytest.mark.parametrize('origin', [None, 'http://localhost:5173', 'http://testserver', 'http://testserver:80'])
def test_mutations_accept_allowed_api_and_missing_origin(origin_client, origin):
    headers = {} if origin is None else {'Origin': origin}
    response = origin_client.post('/mutation', headers=headers)
    assert response.status_code == 200
    if origin == 'http://localhost:5173':
        assert response.headers['access-control-allow-origin'] == origin
        assert response.headers['access-control-allow-credentials'] == 'true'


def test_cors_preflight_allows_only_configured_origins(origin_client):
    headers = {'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'Content-Type'}
    allowed = origin_client.options('/api/auth/login', headers=headers)
    assert allowed.status_code == 200
    assert allowed.headers['access-control-allow-origin'] == headers['Origin']
    assert allowed.headers['access-control-allow-credentials'] == 'true'
    denied = origin_client.options('/api/auth/login', headers=headers | {'Origin': 'https://externo.example'})
    assert denied.status_code == 400
    assert 'access-control-allow-origin' not in denied.headers


def test_origin_guard_protects_auth_and_domain_before_database(origin_client):
    for path in ['/api/auth/registro', '/api/auth/login', '/api/auth/logout', '/api/pacientes']:
        response = origin_client.post(path, json={}, headers={'Origin': 'https://externo.example'})
        assert response.status_code == 403
    assert origin_client.get('/api/auth/me', headers={'Origin': 'https://externo.example'}).status_code == 401


@pytest.mark.parametrize('origin', ['*', 'https://*.example.com', 'null', 'file://localhost', 'http://localhost/path', 'http://user:pass@localhost', 'http://localhost:70000', 'http://localhost/'])
def test_settings_reject_non_explicit_origins(origin):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url='postgresql+psycopg://localhost/config_test', allowed_origins=[origin])


def test_auth_database_unavailable_returns_safe_503():
    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1', 0))
        port = reserved.getsockname()[1]
        app = create_app(Settings(_env_file=None, database_url=f'postgresql+psycopg://synthetic_user:synthetic_secret@127.0.0.1:{port}/offline_test'))
        with TestClient(app) as client:
            for path in ['/api/auth/login', '/api/auth/registro']:
                body = {'email': 'offline@example.com', 'password': 'Password de prueba 123', 'nombre': 'Nombre', 'apellido': 'Prueba'}
                if path.endswith('/login'):
                    body = {key: body[key] for key in ('email', 'password')}
                response = client.post(path, json=body)
                assert response.status_code == 503
                assert response.json() == {'detail': 'Base de datos no disponible'}
                assert 'synthetic_secret' not in response.text and body['password'] not in response.text
