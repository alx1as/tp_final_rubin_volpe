"""Pruebas aisladas con SQLite, sin servicios de IA ni datos reales."""

from datetime import date
from io import BytesIO
import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine, select

from app.models import Objetivo, Observacion, Sesion
from app.schemas.sesion_completa import RegistroSesion
from app.integrations.groq_registro import OrganizadorRegistroGroq
from app.services.registro_sesion import guardar_registro


def datos_sesion(**extra):
    return RegistroSesion.model_validate({
        "fecha": "2026-11-05", "presente": True, "nota_general": "Nota de prueba",
        "observaciones": [
            {"objetivo_id": None, "contexto": "En clase", "resultado": "Completó una tarea"},
            {"objetivo_id": None, "intervencion": "Se ofrecieron apoyos"},
        ], **extra,
    })


def test_guardado_atomico_con_varias_observaciones_y_edicion():
    motor = create_engine("sqlite://")
    SQLModel.metadata.create_all(motor, tables=[Sesion.__table__, Objetivo.__table__, Observacion.__table__])
    with Session(motor) as db:
        primero = guardar_registro(db, 1, datos_sesion())
        assert len(primero.observaciones) == 2
        assert primero.sesion.id is not None
        id_primero, id_segundo = (obs.id for obs in primero.observaciones)
        editado = RegistroSesion.model_validate({
            "fecha": "2026-11-06", "presente": False, "nota_general": "Cambio",
            "observaciones": [
                {"id": id_primero, "contexto": "Contexto modificado"},
                {"nota_libre": "Otra observación"},
            ],
            "observaciones_eliminar": [id_segundo],
        })
        segundo = guardar_registro(db, 1, editado, db.get(Sesion, primero.sesion.id))
        assert segundo.sesion.presente is False
        assert len(segundo.observaciones) == 2
        assert segundo.observaciones[0].id == id_primero
        assert segundo.observaciones[0].contexto == "Contexto modificado"
        assert db.get(Observacion, id_segundo) is None
        assert len(db.exec(select(Sesion)).all()) == 1


def test_objetivo_ajeno_rechazado_no_deja_sesion_ni_observaciones():
    motor = create_engine("sqlite://")
    SQLModel.metadata.create_all(motor, tables=[Sesion.__table__, Objetivo.__table__, Observacion.__table__])
    with Session(motor) as db:
        objetivo = Objetivo(paciente_id=2, descripcion="Objetivo ajeno", fecha_inicio=date(2026, 1, 1))
        db.add(objetivo)
        db.commit()
        try:
            guardar_registro(db, 1, RegistroSesion.model_validate({
                "fecha": "2026-11-05", "presente": True,
                "observaciones": [{"objetivo_id": objetivo.id, "nota_libre": "Prueba"}],
            }))
            raise AssertionError("No rechazó un objetivo ajeno")
        except HTTPException as error:
            assert error.status_code == 404
        assert db.exec(select(Sesion)).all() == []
        assert db.exec(select(Observacion)).all() == []


def test_edicion_con_observacion_ajena_no_cambia_registros():
    motor = create_engine("sqlite://")
    SQLModel.metadata.create_all(motor, tables=[Sesion.__table__, Objetivo.__table__, Observacion.__table__])
    with Session(motor) as db:
        a = guardar_registro(db, 1, datos_sesion())
        b = guardar_registro(db, 1, datos_sesion())
        try:
            guardar_registro(db, 1, RegistroSesion.model_validate({
                "fecha": "2026-12-01", "presente": False,
                "observaciones": [{"id": b.observaciones[0].id, "nota_libre": "Ajena"}],
            }), db.get(Sesion, a.sesion.id))
            raise AssertionError("No rechazó la observación de otra sesión")
        except HTTPException as error:
            assert error.status_code == 404
        db.expire_all()
        assert db.get(Sesion, a.sesion.id).fecha == date(2026, 11, 5)
        assert len(db.exec(select(Observacion)).all()) == 4


def test_esquema_rechaza_ids_repetidos_o_bloques_vacios():
    for observaciones, eliminar in [
        ([{"id": 1, "nota_libre": "Algo"}, {"id": 1, "nota_libre": "Otro"}], []),
        ([{"id": 1, "nota_libre": "Algo"}], [1]),
        ([{"contexto": " "}], []),
    ]:
        try:
            RegistroSesion.model_validate({"fecha": "2026-11-05", "presente": True,
                                           "observaciones": observaciones,
                                           "observaciones_eliminar": eliminar})
            raise AssertionError("No rechazó datos inválidos")
        except ValidationError:
            pass


def test_organizador_ofrece_varias_observaciones_y_filtra_objetivo_desconocido(monkeypatch):
    capturado = {}

    def responder(peticion, timeout):
        capturado["peticion"] = json.loads(peticion.data)
        resultado = {
            "nota_general": None,
            "observaciones": [
                {"objetivo_id": 2, "contexto": "Lectura", "conducta_observable": "Leyó texto",
                 "intervencion": None, "resultado": None, "nota_libre": None},
                {"objetivo_id": 999, "contexto": "Organización", "conducta_observable": None,
                 "intervencion": "Se guió", "resultado": None, "nota_libre": None},
            ],
        }
        return BytesIO(json.dumps({"choices": [{"message": {"content": json.dumps(resultado)}}]}).encode())

    monkeypatch.setattr("app.integrations.groq_registro.urlopen", responder)
    salida = OrganizadorRegistroGroq("clave_ficticia").organizar(
        "Lectura y organización", [{"id": 2, "descripcion": "Comprender consignas"}],
    )
    assert len(salida.observaciones) == 2
    assert salida.observaciones[0].objetivo_id == 2
    assert salida.observaciones[1].objetivo_id is None
    assert capturado["peticion"]["response_format"]["json_schema"]["strict"] is True


def test_error_durante_escritura_restaura_toda_la_transaccion():
    from sqlalchemy import event

    motor = create_engine("sqlite://")
    SQLModel.metadata.create_all(motor, tables=[Sesion.__table__, Objetivo.__table__, Observacion.__table__])
    with Session(motor) as db:
        def forzar_error(session, flush_context, instances):
            if any(isinstance(registro, Observacion) for registro in session.new):
                raise RuntimeError("Error de prueba al insertar observaciones")

        event.listen(db, "before_flush", forzar_error)
        try:
            try:
                guardar_registro(db, 1, datos_sesion())
                raise AssertionError("No se propagó el error simulado")
            except RuntimeError as error:
                assert "Error de prueba" in str(error)
        finally:
            event.remove(db, "before_flush", forzar_error)
        assert db.exec(select(Sesion)).all() == []
        assert db.exec(select(Observacion)).all() == []
