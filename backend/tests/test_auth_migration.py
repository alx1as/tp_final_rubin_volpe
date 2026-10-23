from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Profesional, SesionAutenticacion


BACKEND = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.integration


@pytest.mark.parametrize("install", ["new", "migration"])
def test_session_schema_and_model_work_on_both_installations(isolated_database, install):
    app = isolated_database
    execute = app.state.execute_test_script
    if install == "new":
        execute(BACKEND / "init.sql")
    else:
        execute(BACKEND / "tests/fixtures/schema_pre_auth.sql")
        with Session(app.state.engine) as session:
            # Un registro previo debe conservarse tras la migración.
            session.add(Profesional(nombre="Previo", apellido="Prueba", email="previo@example.com", password_hash="hash_ficticio"))
            session.commit()
        execute(BACKEND / "migrations/001_sesion_autenticacion.sql")
    with Session(app.state.engine) as session:
        tables = session.exec(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = current_schema() AND table_type = 'BASE TABLE'")).scalar_one()
        assert tables == 10
        if install == "migration":
            assert session.exec(select(Profesional).where(Profesional.email == "previo@example.com")).one().nombre == "Previo"
        professional = Profesional(nombre="Nombre", apellido="Prueba", email="modelo@example.com", password_hash="hash_ficticio")
        session.add(professional)
        session.commit()
        now = datetime.now(timezone.utc)
        record = SesionAutenticacion(profesional_id=professional.id, token_hash="a" * 64, creada_en=now, vence_en=now + timedelta(hours=8))
        session.add(record)
        session.commit()
        session.refresh(record)
        assert record.id is not None
        assert record.creada_en == now
        assert record.vence_en - record.creada_en == timedelta(hours=8)
        assert record.revocada_en is None
        assert "a" * 64 not in repr(record)
        record.revocada_en = now + timedelta(minutes=1)
        session.add(record)
        session.commit()
        session.refresh(record)
        assert record.revocada_en is not None
        columns = session.exec(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema=current_schema() AND table_name='sesion_autenticacion'")).all()
        types = dict(columns)
        assert all(types[name] == 'timestamp with time zone' for name in ['creada_en', 'vence_en', 'revocada_en'])
        with TestClient(app) as client:
            assert client.get('/docs').status_code == 200
        assert session.exec(select(SesionAutenticacion)).one().id == record.id


@pytest.mark.parametrize("invalid", ["hash", "duplicate", "foreign_key", "expiration", "revocation", "delete_professional"])
def test_database_enforces_session_constraints(auth_app, invalid):
    now = datetime.now(timezone.utc)
    with Session(auth_app.state.engine) as session:
        professional = Profesional(nombre="Nombre", apellido="Prueba", email="constraints@example.com", password_hash="hash_ficticio")
        session.add(professional)
        session.commit()
        record = SesionAutenticacion(profesional_id=professional.id, token_hash="a" * 64, creada_en=now, vence_en=now + timedelta(hours=8))
        session.add(record)
        session.commit()
        if invalid == 'delete_professional':
            session.delete(professional)
        else:
            values = dict(profesional_id=professional.id, token_hash="b" * 64, creada_en=now, vence_en=now + timedelta(hours=8))
            if invalid == 'hash':
                values['token_hash'] = 'not-a-sha256'
            elif invalid == 'duplicate':
                values['token_hash'] = 'a' * 64
            elif invalid == 'foreign_key':
                values['profesional_id'] = 2147483647
            elif invalid == 'expiration':
                values['vence_en'] = now
            elif invalid == 'revocation':
                values['revocada_en'] = now - timedelta(seconds=1)
            session.add(SesionAutenticacion(**values))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        assert len(session.exec(select(SesionAutenticacion)).all()) == 1
