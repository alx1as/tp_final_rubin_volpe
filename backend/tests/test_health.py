import socket

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, text
from sqlmodel import Session

from app.core.config import Settings
from app.main import create_app


OK = {"estado": "ok", "postgresql": "conectado"}
UNAVAILABLE = {"estado": "error", "postgresql": "no_disponible"}


def test_unavailable_database_does_not_prevent_startup_or_expose_url():
    # Mantener el puerto reservado sin escuchar evita colisiones con otros servicios.
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
        settings = Settings(
            _env_file=None,
            database_url=f"postgresql+psycopg://test_user:synthetic_secret@127.0.0.1:{port}/e1_test",
        )
        app = create_app(settings)
        with TestClient(app) as client:
            assert client.get("/docs").status_code == 200
            response = client.get("/api/salud")
            assert response.status_code == 503
            assert response.json() == UNAVAILABLE
            assert "synthetic_secret" not in response.text
            assert app.state.engine.pool.checkedout() == 0
            schema = client.get("/openapi.json").json()
            assert "503" in schema["paths"]["/api/salud"]["get"]["responses"]


@pytest.mark.integration
def test_health_queries_every_request_without_writes_or_ddl(postgres_app):
    engine = postgres_app.state.engine
    statements = []
    with Session(engine) as session:
        tables_before = session.exec(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )).all()

    def record_statement(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record_statement)
    with TestClient(postgres_app) as client:
        for _ in range(3):
            response = client.get("/api/salud")
            assert response.status_code == 200
            assert response.json() == OK
            assert engine.pool.checkedout() == 0
    assert len(statements) == 3
    assert all(statement.strip().upper().startswith("SELECT ") for statement in statements)
    event.remove(engine, "before_cursor_execute", record_statement)
    with Session(engine) as session:
        assert session.exec(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )).all() == tables_before


@pytest.mark.integration
def test_health_returns_503_when_pool_is_full_then_recovers(postgres_app):
    engine = postgres_app.state.engine
    with TestClient(postgres_app) as client:
        connections = []
        try:
            # Ocupar las cinco conexiones y las cinco adicionales del pool.
            for _ in range(10):
                connections.append(engine.connect())
            response = client.get("/api/salud")
            assert response.status_code == 503
            assert response.json() == UNAVAILABLE
        finally:
            for connection in connections:
                connection.close()
        assert engine.pool.checkedout() == 0
        response = client.get("/api/salud")
        assert response.status_code == 200
        assert response.json() == OK
