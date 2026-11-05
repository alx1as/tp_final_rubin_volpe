"""Escritura atómica de sesiones y observaciones vinculadas.

No modifica los endpoints de registro individual ni el esquema de PostgreSQL.
"""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Objetivo, Observacion, Sesion
from app.schemas.sesion_completa import RegistroSesion, RegistroSesionRespuesta
from app.services.perfil import buscar_hijo


CAMPOS_OBSERVACION = (
    "objetivo_id", "contexto", "conducta_observable", "intervencion", "resultado", "nota_libre",
)


def guardar_registro(
    session: Session, paciente_id: int, datos: RegistroSesion, sesion_actual: Sesion | None = None,
) -> RegistroSesionRespuesta:
    """Valida relaciones antes de escribir y confirma todos los cambios en un commit.

    Una falla revierte tanto la sesión como todas sus observaciones.
    """
    try:
        if sesion_actual is None and (
            datos.observaciones_eliminar or any(obs.id is not None for obs in datos.observaciones)
        ):
            raise HTTPException(422, "No se pueden editar observaciones en una sesión nueva")

        existentes: dict[int, Observacion] = {}
        if sesion_actual is not None:
            ids = [obs.id for obs in datos.observaciones if obs.id is not None]
            ids.extend(datos.observaciones_eliminar)
            if ids:
                registros = session.exec(select(Observacion).where(
                    Observacion.sesion_id == sesion_actual.id,
                    Observacion.id.in_(ids),
                )).all()
                existentes = {obs.id: obs for obs in registros}
                if len(existentes) != len(set(ids)):
                    raise HTTPException(404, "Observación no encontrada en esta sesión")

        # Verificar los objetivos contra el mismo paciente antes de tocar ningún registro.
        for objetivo_id in {obs.objetivo_id for obs in datos.observaciones if obs.objetivo_id is not None}:
            buscar_hijo(session, Objetivo, paciente_id, objetivo_id)

        sesion = sesion_actual or Sesion(paciente_id=paciente_id, fecha=datos.fecha,
                                         presente=datos.presente, nota_general=datos.nota_general)
        sesion.fecha = datos.fecha
        sesion.presente = datos.presente
        sesion.nota_general = datos.nota_general
        session.add(sesion)
        session.flush()  # Obtiene el ID sin hacer commit.

        for propuesta in datos.observaciones:
            observacion = existentes[propuesta.id] if propuesta.id is not None else Observacion(sesion_id=sesion.id)
            for campo in CAMPOS_OBSERVACION:
                setattr(observacion, campo, getattr(propuesta, campo))
            session.add(observacion)

        for id_eliminar in datos.observaciones_eliminar:
            session.delete(existentes[id_eliminar])

        session.flush()
        session.commit()
        session.refresh(sesion)
        observaciones = session.exec(select(Observacion).where(
            Observacion.sesion_id == sesion.id
        ).order_by(Observacion.id)).all()
        return RegistroSesionRespuesta(sesion=sesion, observaciones=observaciones)
    except Exception:
        session.rollback()
        raise
