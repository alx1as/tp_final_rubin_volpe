"""Borradores desde fuentes autorizadas, sin modificar ni guardar registros."""

from sqlmodel import Session, select

from app.integrations.contratos import ContextoInforme, GeneradorInformes, IntegracionNoConfigurada
from app.models import Objetivo, Observacion, Paciente, Sesion
from app.schemas.cronologia import EntradaCronologia
from app.schemas.integraciones import BorradorGenerado, SolicitudBorrador
from app.schemas.objetivo import ObjetivoRespuesta
from app.schemas.paciente import PacienteRespuesta
from app.services.integraciones import ejecutar_integracion


def recopilar_contexto(session: Session, paciente: Paciente, datos: SolicitudBorrador) -> ContextoInforme:
    filtros = (
        Sesion.paciente_id == paciente.id,
        Sesion.fecha >= datos.periodo_desde,
        Sesion.fecha <= datos.periodo_hasta,
    )
    fuentes = session.exec(
        select(Sesion, Observacion)
        .outerjoin(Observacion, Observacion.sesion_id == Sesion.id)
        .where(*filtros)
        .order_by(Sesion.fecha.desc(), Sesion.id.desc(), Observacion.id)
    ).all()
    sesiones = {}
    por_sesion = {}
    objetivos_ids = set()
    # Una sola consulta fija sesiones y observaciones del intervalo en el mismo
    # snapshot, incluso si se carga una sesión nueva mientras se genera el informe.
    for registro, observacion in fuentes:
        sesiones[registro.id] = registro
        por_sesion.setdefault(registro.id, [])
        if observacion is not None:
            por_sesion[registro.id].append(observacion)
            if observacion.objetivo_id is not None:
                objetivos_ids.add(observacion.objetivo_id)
    objetivos = []
    if objetivos_ids:
        objetivos = session.exec(
            select(Objetivo).where(
                Objetivo.paciente_id == paciente.id, Objetivo.id.in_(objetivos_ids),
            ).order_by(Objetivo.id)
        ).all()

    # El adaptador recibe modelos públicos separados de las entidades ORM. Sus
    # cambios sobre estos datos nunca se confirman como cambios del seguimiento.
    return ContextoInforme(
        **datos.model_dump(), paciente=PacienteRespuesta.model_validate(paciente),
        sesiones=tuple(EntradaCronologia(
            **registro.model_dump(), observaciones=por_sesion[registro.id],
        ) for registro in sesiones.values()),
        objetivos=tuple(ObjetivoRespuesta.model_validate(objetivo) for objetivo in objetivos),
    )


def generar_borrador(
    session: Session, paciente: Paciente, datos: SolicitudBorrador, generador: GeneradorInformes | None,
) -> BorradorGenerado:
    if generador is None:
        raise IntegracionNoConfigurada
    contexto = recopilar_contexto(session, paciente, datos)
    contenido = ejecutar_integracion(lambda: generador.generar(contexto))
    return BorradorGenerado(**datos.model_dump(), contenido=contenido)
