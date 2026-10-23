from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Escolaridad, Paciente, ProfesionalTratante
from app.services.perfil import guardar


pytestmark = pytest.mark.integration


@pytest.mark.parametrize('invalid', ['patient_dates','patient_empty_name','school_dates','contact_dates'])
def test_postgresql_keeps_domain_constraints_after_invalid_insert(profile_client, auth_app, invalid):
    body = {'nombre':'Nombre','apellido':'Prueba','fecha_nacimiento':'2015-01-01','fecha_inicio_seguimiento':'2026-01-01'}
    patient_id = profile_client.post('/api/pacientes', json=body).json()['id']
    with Session(auth_app.state.engine) as session:
        patient = session.get(Paciente, patient_id)
        if invalid.startswith('patient_'):
            values = {'profesional_id':patient.profesional_id, 'nombre':'Nombre', 'apellido':'Prueba', 'fecha_nacimiento':date(2015,1,1), 'fecha_inicio_seguimiento':date(2026,1,1)}
            values |= {'fecha_inicio_seguimiento':date(2010,1,1)} if invalid == 'patient_dates' else {'nombre':''}
            record = Paciente(**values)
        elif invalid == 'school_dates':
            record = Escolaridad(paciente_id=patient_id, institucion='Institucion', nivel='Nivel', grado_anio_sala='1', modalidad='Comun', fecha_inicio=date(2026,1,1), fecha_fin=date(2025,1,1))
        else:
            record = ProfesionalTratante(paciente_id=patient_id, nombre='Contacto', especialidad='Especialidad', fecha_inicio=date(2026,1,1), fecha_fin=date(2025,1,1))
        with pytest.raises(IntegrityError):
            guardar(session,record)
        assert session.is_active
        assert session.get(Paciente,patient_id).nombre == 'Nombre'
    assert profile_client.get('/api/pacientes').json()['total'] == 1
