from datetime import date

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Paciente, Profesional
from app.schemas.comun import Paginacion
from app.schemas.paciente import PacienteDatos, PacienteEditar
from app.services.perfil import buscar_paciente, editar, guardar, paginar


pytestmark = pytest.mark.integration


def professional(email):
    return Profesional(nombre='Nombre', apellido='Prueba', email=email, password_hash='hash_ficticio')


def test_pagination_counts_only_authorized_rows_before_offset(auth_app):
    with Session(auth_app.state.engine) as session:
        first = guardar(session, professional('primero@example.com'))
        second = guardar(session, professional('segundo@example.com'))
        query = select(Paciente).where(Paciente.profesional_id == first.id).order_by(Paciente.id)
        empty = paginar(session, query, Paginacion())
        assert empty.model_dump() == {'items': [], 'total': 0, 'offset': 0, 'limit': 20}
        ids = []
        for owner in [first, second, first]:
            record = guardar(session, Paciente(profesional_id=owner.id, nombre='Paciente', apellido='Prueba', fecha_nacimiento=date(2015,1,1), fecha_inicio_seguimiento=date(2026,1,1)))
            if owner.id == first.id:
                ids.append(record.id)
        page = paginar(session, query, Paginacion(offset=1, limit=1))
        assert page.total == 2 and page.items[0].id == ids[1]
        assert paginar(session, query, Paginacion(offset=99)).total == 2
        assert paginar(session, query, Paginacion(offset=99)).items == []
        assert buscar_paciente(session, first.id, ids[0]).id == ids[0]
        with pytest.raises(HTTPException) as error:
            buscar_paciente(session, second.id, ids[0])
        assert error.value.status_code == 404


def test_invalid_partial_edit_does_not_mutate_or_persist(auth_app):
    with Session(auth_app.state.engine) as session:
        owner = guardar(session, professional('edicion@example.com'))
        record = guardar(session, Paciente(profesional_id=owner.id, nombre='Original', apellido='Prueba', fecha_nacimiento=date(2015,1,1), fecha_inicio_seguimiento=date(2026,1,1)))
        with pytest.raises(RequestValidationError):
            editar(session, record, PacienteEditar(nombre='Cambio', fecha_nacimiento='2027-01-01'), PacienteDatos)
        assert record.nombre == 'Original'
        session.refresh(record)
        assert record.nombre == 'Original' and record.fecha_nacimiento == date(2015,1,1)


def test_integrity_conflict_rolls_back_and_session_can_continue(auth_app):
    with Session(auth_app.state.engine) as session:
        guardar(session, professional('duplicado@example.com'))
        with pytest.raises(IntegrityError):
            guardar(session, professional('duplicado@example.com'))
        assert session.is_active
        assert len(session.exec(select(Profesional)).all()) == 1
        assert guardar(session, professional('distinto@example.com')).id is not None
