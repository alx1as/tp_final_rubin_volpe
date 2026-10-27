"""Consulta de cronología, paginada por sesión sin duplicar registros fuente."""

from datetime import date

from sqlmodel import Session, select

from app.models import Observacion, Sesion
from app.schemas.comun import Pagina, Paginacion
from app.schemas.cronologia import EntradaCronologia
from app.services.perfil import paginar


def consultar_cronologia(
    session: Session, paciente_id: int, pagina: Paginacion,
    desde: date | None = None, hasta: date | None = None,
) -> Pagina[EntradaCronologia]:
    consulta = select(Sesion).where(Sesion.paciente_id == paciente_id)
    if desde is not None:
        consulta = consulta.where(Sesion.fecha >= desde)
    if hasta is not None:
        consulta = consulta.where(Sesion.fecha <= hasta)
    consulta = consulta.order_by(Sesion.fecha.desc(), Sesion.id.desc())
    resultado = paginar(session, consulta, pagina)
    if not resultado.items:
        return resultado

    # La paginación se aplica antes de buscar observaciones. Una sesión nunca
    # se divide entre páginas y el número de consultas no crece por sesión.
    por_sesion = {registro.id: [] for registro in resultado.items}
    observaciones = session.exec(
        select(Observacion)
        .where(Observacion.sesion_id.in_(list(por_sesion)))
        .order_by(Observacion.id)
    ).all()
    for observacion in observaciones:
        por_sesion[observacion.sesion_id].append(observacion)
    resultado.items = [
        EntradaCronologia(**registro.model_dump(), observaciones=por_sesion[registro.id])
        for registro in resultado.items
    ]
    return resultado
