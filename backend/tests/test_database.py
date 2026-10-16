import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from sqlmodel import Session
from starlette.requests import Request
from time import monotonic

from app.core.config import Settings
from app.db.session import build_engine, get_session
from app.main import create_app


def test_startup_and_docs_do_not_connect_to_database():
    settings = Settings(_env_file=None, database_url="postgresql+psycopg://localhost:1/e1_test")
    app = create_app(settings)

    @event.listens_for(app.state.engine, "do_connect")
    def forbid_connection(*args):
        pytest.fail("El arranque o la documentación intentaron conectar con PostgreSQL")

    with TestClient(app) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200


def test_connection_and_pool_timeouts():
    settings = Settings(_env_file=None, database_url="postgresql+psycopg://localhost/e1_test")
    engine = build_engine(settings)

    class ConnectionIntercepted(Exception):
        pass

    @event.listens_for(engine, "do_connect")
    def check_connect_arguments(dialect, record, args, kwargs):
        assert kwargs["connect_timeout"] == 3
        assert kwargs["options"] == "-c statement_timeout=3000"
        raise ConnectionIntercepted

    try:
        assert engine.pool.timeout() == 3
        with pytest.raises(ConnectionIntercepted):
            engine.connect()
    finally:
        engine.dispose()


@pytest.mark.integration
@pytest.mark.parametrize("fail", [False, True])
def test_sessions_release_connections_and_rollback(postgres_app, fail):
    engine = postgres_app.state.engine
    rollbacks = []
    event.listen(engine, "rollback", lambda connection: rollbacks.append(True))
    request = Request({"type": "http", "app": postgres_app})
    dependency = get_session(request)
    session = next(dependency)
    assert session.exec(text("SELECT 1")).scalar_one() == 1
    assert engine.pool.checkedout() == 1
    if fail:
        with pytest.raises(RuntimeError, match="fallo de prueba"):
            dependency.throw(RuntimeError("fallo de prueba"))
    else:
        dependency.close()
    assert engine.pool.checkedout() == 0
    assert rollbacks
    other_dependency = get_session(request)
    try:
        assert next(other_dependency) is not session
    finally:
        other_dependency.close()


@pytest.mark.integration
def test_postgresql_enforces_statement_timeout(postgres_app):
    with Session(postgres_app.state.engine) as session:
        assert session.exec(text("SHOW statement_timeout")).scalar_one() == "3s"
        started = monotonic()
        with pytest.raises(OperationalError):
            session.exec(text("SELECT pg_sleep(5)"))
        assert 2.5 <= monotonic() - started < 5
    assert postgres_app.state.engine.pool.checkedout() == 0
