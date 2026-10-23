from datetime import date

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import pytest

from app.schemas.comun import Paginacion, validar_edicion
from app.schemas.escolaridad import EscolaridadEditar, EscolaridadGuardar
from app.schemas.paciente import PacienteDatos, PacienteEditar
from app.schemas.profesional_tratante import ProfesionalTratanteEditar


@pytest.mark.parametrize('schema,field', [(PacienteEditar,'nombre'), (PacienteEditar,'activo'), (PacienteEditar,'fecha_nacimiento'), (EscolaridadEditar,'institucion'), (EscolaridadEditar,'fecha_inicio'), (ProfesionalTratanteEditar,'especialidad')])
def test_partial_updates_reject_explicit_null_for_required_fields(schema, field):
    assert schema().model_dump(exclude_unset=True) == {}
    with pytest.raises(ValidationError):
        schema.model_validate({field: None})


@pytest.mark.parametrize('values', [{'offset': -1}, {'limit': 0}, {'limit': 101}])
def test_pagination_limits(values):
    with pytest.raises(ValidationError):
        Paginacion(**values)


def test_partial_update_checks_complete_patient_and_preserves_omitted_fields():
    actual = {'nombre':'Original', 'apellido':'Prueba', 'fecha_nacimiento':date(2015,1,1), 'fecha_inicio_seguimiento':date(2026,1,1), 'activo': True}
    assert validar_edicion(actual, PacienteEditar(nombre=' Nuevo '), PacienteDatos) == {'nombre':'Nuevo'}
    assert validar_edicion(actual, PacienteEditar(activo=False), PacienteDatos) == {'activo':False}
    with pytest.raises(RequestValidationError) as error:
        validar_edicion(actual, PacienteEditar(fecha_nacimiento='2027-01-01'), PacienteDatos)
    assert error.value.errors()[0]['loc'][0] == 'body'
    assert actual['fecha_nacimiento'] == date(2015,1,1)


def test_partial_period_checks_saved_dates_and_normalizes_optionals():
    actual = {'institucion':'Institucion', 'nivel':'Primario', 'grado_anio_sala':'1', 'modalidad':'Comun', 'fecha_inicio':date(2026,1,1), 'fecha_fin':date(2026,12,1)}
    changes = EscolaridadEditar(fecha_fin='  ', observaciones='   ')
    assert validar_edicion(actual, changes, EscolaridadGuardar) == {'fecha_fin':None, 'observaciones':None}
    with pytest.raises(RequestValidationError):
        validar_edicion(actual, EscolaridadEditar(fecha_inicio='2027-01-01'), EscolaridadGuardar)


@pytest.mark.parametrize('value', [0, True, '2026-01-01T00:00:00', '01/01/2026'])
def test_domain_dates_require_iso_date(value):
    with pytest.raises(ValidationError):
        PacienteEditar(fecha_nacimiento=value)


@pytest.mark.parametrize('field', ['id','profesional_id','paciente_id'])
def test_updates_reject_identity_and_parent_fields(field):
    for schema in [PacienteEditar, EscolaridadEditar, ProfesionalTratanteEditar]:
        with pytest.raises(ValidationError):
            schema.model_validate({field: 1})
