import os
from pathlib import Path
from uuid import uuid4

from psycopg import sql
import pytest
from sqlalchemy import event
from sqlalchemy.engine import make_url

from app.core.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def postgres_settings():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Configurar TEST_DATABASE_URL para PostgreSQL exclusivo de pruebas")
    settings = Settings(_env_file=None, database_url=url)
    if not make_url(settings.database_url.get_secret_value()).database.endswith("_test"):
        pytest.fail("La base de TEST_DATABASE_URL debe terminar en _test")
    return settings


@pytest.fixture
def postgres_app(postgres_settings):
    app = create_app(postgres_settings)
    try:
        yield app
    finally:
        app.state.engine.dispose()


@pytest.fixture
def isolated_database(postgres_settings):
    """Schema nuevo por prueba, exclusivamente en TEST_DATABASE_URL (_test).

    No usa .env ni inicializa las tablas existentes de la base. Solo elimina el
    schema aleatorio que este fixture creó, nunca public ni un schema recibido.
    """
    app = create_app(postgres_settings)
    engine = app.state.engine
    schema = "auth_test_" + uuid4().hex
    with engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    engine.dispose()

    def use_isolated_schema(dbapi_connection, connection_record):
        previous = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        try:
            with dbapi_connection.cursor() as cursor:
                cursor.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        finally:
            dbapi_connection.autocommit = previous

    event.listen(engine, "connect", use_isolated_schema)

    def execute_script(path):
        # El SQL incluye su propia transacción; autocommit permite respetarla.
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.exec_driver_sql(Path(path).read_text(encoding="utf-8"))

    app.state.execute_test_script = execute_script
    try:
        yield app
    finally:
        engine.dispose()
        event.remove(engine, "connect", use_isolated_schema)
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        finally:
            engine.dispose()


@pytest.fixture
def auth_app(isolated_database):
    isolated_database.state.execute_test_script(Path(__file__).resolve().parents[1] / "init.sql")
    return isolated_database


@pytest.fixture
def profile_client(auth_app):
    with TestClient(auth_app) as client:
        data = {"nombre": "Nombre", "apellido": "Prueba", "email": "perfil@example.com", "password": "Password de prueba 123"}
        assert client.post("/api/auth/registro", json=data).status_code == 201
        assert client.post("/api/auth/login", json={key: data[key] for key in ("email", "password")}).status_code == 200
        yield client
