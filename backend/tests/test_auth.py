from datetime import datetime, timedelta, timezone
from hashlib import sha256
import re

from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, select

from app.core.security import verify_password
from app.models import Profesional, SesionAutenticacion


pytestmark = pytest.mark.integration
PASSWORD = "Password de prueba 123"


def registration(email="registro@example.com"):
    return {"nombre": " Nombre ", "apellido": " Prueba ", "email": email, "password": PASSWORD}


def test_register_hashes_password_and_normalizes_account(auth_app):
    with TestClient(auth_app) as client:
        response = client.post('/api/auth/registro', json=registration(' REGISTRO@EXAMPLE.COM '))
        assert response.status_code == 201
        data = response.json()
        assert data == {'id': data['id'], 'nombre': 'Nombre', 'apellido': 'Prueba', 'email': 'registro@example.com', 'activo': True}
        assert 'set-cookie' not in response.headers
        assert PASSWORD not in response.text and 'password_hash' not in response.text
        with Session(auth_app.state.engine) as session:
            user = session.exec(select(Profesional)).one()
            assert user.password_hash.startswith('$argon2id$')
            assert verify_password(PASSWORD, user.password_hash)
            assert user.password_hash not in repr(user)
            assert not session.exec(select(SesionAutenticacion)).all()


def test_register_rejects_duplicate_normalized_email(auth_app):
    with TestClient(auth_app) as client:
        assert client.post('/api/auth/registro', json=registration()).status_code == 201
        response = client.post('/api/auth/registro', json=registration(' REGISTRO@EXAMPLE.COM '))
        assert response.status_code == 409
        assert 'INSERT' not in response.text and 'argon2' not in response.text
        with Session(auth_app.state.engine) as session:
            assert len(session.exec(select(Profesional)).all()) == 1


@pytest.mark.parametrize('invalid', [{'nombre': ' '}, {'apellido': ''}, {'email': 'incorrecto'}, {'password': 'corta'}, {'password': '        '}, {'id': 999}, {'activo': False}])
def test_register_rejects_invalid_input_without_echoing_password(auth_app, invalid):
    data = registration() | invalid
    with TestClient(auth_app) as client:
        response = client.post('/api/auth/registro', json=data)
        assert response.status_code == 422
        assert PASSWORD not in response.text
        assert all('input' not in error for error in response.json()['detail'])


def test_login_sets_cookie_and_persists_only_token_hash(auth_app):
    with TestClient(auth_app) as client:
        assert client.post('/api/auth/registro', json=registration()).status_code == 201
        response = client.post('/api/auth/login', json={'email': ' REGISTRO@EXAMPLE.COM ', 'password': PASSWORD})
        assert response.status_code == 200
        cookie = response.headers['set-cookie']
        assert 'HttpOnly' in cookie and 'SameSite=lax' in cookie and 'Path=/' in cookie and 'Max-Age=28800' in cookie
        token = client.cookies.get('sesion')
        assert re.fullmatch('[A-Za-z0-9_-]{43}', token)
        assert token not in response.text and PASSWORD not in response.text
        with Session(auth_app.state.engine) as session:
            record = session.exec(select(SesionAutenticacion)).one()
            assert record.token_hash == sha256(token.encode()).hexdigest()
            assert record.vence_en - record.creada_en == timedelta(hours=8)
        second = client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': PASSWORD})
        assert second.status_code == 200
        assert client.cookies.get('sesion') != token


def test_login_has_uniform_errors_and_no_session_for_inactive_account(auth_app):
    with TestClient(auth_app) as client:
        client.post('/api/auth/registro', json=registration())
        wrong = client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': 'incorrecta'})
        absent = client.post('/api/auth/login', json={'email': 'ausente@example.com', 'password': PASSWORD})
        with Session(auth_app.state.engine) as session:
            user = session.exec(select(Profesional)).one()
            user.activo = False
            session.add(user)
            session.commit()
        inactive = client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': PASSWORD})
        for response in (wrong, absent, inactive):
            assert response.status_code == 401
            assert response.json() == {'detail': 'Correo o contraseña inválidos'}
            assert 'set-cookie' not in response.headers
        with Session(auth_app.state.engine) as session:
            assert not session.exec(select(SesionAutenticacion)).all()


def test_login_secure_cookie_is_configurable(auth_app):
    auth_app.state.settings.session_cookie_secure = True
    with TestClient(auth_app, base_url='https://testserver') as client:
        client.post('/api/auth/registro', json=registration())
        response = client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': PASSWORD})
        assert response.status_code == 200
        assert 'Secure' in response.headers['set-cookie']


def login_client(client, email='registro@example.com'):
    assert client.post('/api/auth/registro', json=registration(email)).status_code == 201
    assert client.post('/api/auth/login', json={'email': email, 'password': PASSWORD}).status_code == 200
    return client.cookies.get('sesion')


def test_logout_revokes_only_current_session_and_clears_cookie(auth_app):
    with TestClient(auth_app) as client:
        first = login_client(client)
        assert client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': PASSWORD}).status_code == 200
        second = client.cookies.get('sesion')
        response = client.post('/api/auth/logout')
        assert response.status_code == 204 and response.content == b''
        assert 'Max-Age=0' in response.headers['set-cookie']
        assert client.cookies.get('sesion') is None
        with Session(auth_app.state.engine) as session:
            records = {item.token_hash: item for item in session.exec(select(SesionAutenticacion)).all()}
            assert records[sha256(first.encode()).hexdigest()].revocada_en is None
            assert records[sha256(second.encode()).hexdigest()].revocada_en is not None
        client.cookies.set('sesion', second)
        assert client.post('/api/auth/logout').status_code == 401
        client.cookies.clear()
        client.cookies.set('sesion', first)
        assert client.post('/api/auth/logout').status_code == 204


@pytest.mark.parametrize('reason', ['absent', 'malformed', 'unknown', 'expired', 'revoked', 'inactive'])
def test_logout_rejects_invalid_session(auth_app, reason):
    with TestClient(auth_app) as client:
        token = login_client(client)
        with Session(auth_app.state.engine) as session:
            record = session.exec(select(SesionAutenticacion)).one()
            if reason == 'expired':
                record.creada_en = datetime.now(timezone.utc) - timedelta(hours=9)
                record.vence_en = datetime.now(timezone.utc) - timedelta(seconds=1)
                session.add(record)
            elif reason == 'revoked':
                record.revocada_en = datetime.now(timezone.utc)
                session.add(record)
            elif reason == 'inactive':
                user = session.get(Profesional, record.profesional_id)
                user.activo = False
                session.add(user)
            session.commit()
        if reason in ('absent', 'malformed', 'unknown'):
            client.cookies.clear()
            if reason != 'absent':
                client.cookies.set('sesion', 'invalida' if reason == 'malformed' else 'x' * 43)
        response = client.post('/api/auth/logout')
        assert response.status_code == 401
        assert token not in response.text
        assert client.get('/api/auth/me').status_code == 401


def test_me_returns_authenticated_public_account_without_renewal(auth_app):
    with TestClient(auth_app) as first, TestClient(auth_app) as second:
        first_token = login_client(first, 'primero@example.com')
        second_token = login_client(second, 'segundo@example.com')
        with Session(auth_app.state.engine) as session:
            before = {record.token_hash: record.vence_en for record in session.exec(select(SesionAutenticacion)).all()}
        one = first.get('/api/auth/me')
        two = second.get('/api/auth/me')
        assert one.status_code == two.status_code == 200
        assert one.json()['id'] != two.json()['id']
        assert one.json()['email'] == 'primero@example.com'
        assert two.json()['email'] == 'segundo@example.com'
        for response in (one, two):
            assert set(response.json()) == {'id', 'nombre', 'apellido', 'email', 'activo'}
            assert 'set-cookie' not in response.headers
            assert first_token not in response.text and second_token not in response.text
        with Session(auth_app.state.engine) as session:
            assert {record.token_hash: record.vence_en for record in session.exec(select(SesionAutenticacion)).all()} == before


def test_login_rejects_legacy_invalid_hash_safely(auth_app):
    with Session(auth_app.state.engine) as session:
        session.add(Profesional(nombre='Previo', apellido='Prueba', email='previo@example.com', password_hash='hash_no_valido'))
        session.commit()
    with TestClient(auth_app) as client:
        response = client.post('/api/auth/login', json={'email': 'previo@example.com', 'password': PASSWORD})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Correo o contraseña inválidos'}
        assert 'hash_no_valido' not in response.text


def test_registration_and_login_preserve_password_spaces(auth_app):
    password = '  Password de prueba 123  '
    with TestClient(auth_app) as client:
        assert client.post('/api/auth/registro', json=registration() | {'password': password}).status_code == 201
        assert client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': password.strip()}).status_code == 401
        assert client.post('/api/auth/login', json={'email': 'registro@example.com', 'password': password}).status_code == 200
