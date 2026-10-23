"""Consultar, crear y editar objetivos de un paciente."""

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, SesionDB
from app.models import Objetivo, Observacion, Sesion
from app.schemas.comun import Pagina
from app.schemas.objetivo import ObjetivoEditar, ObjetivoGuardar, ObjetivoRespuesta
from app.schemas.observacion import EvidenciaObjetivo
from app.services.perfil import buscar_hijo, editar, guardar, paginar

router = APIRouter(prefix="/pacientes/{paciente_id}/objetivos", tags=["Objetivos"])


@router.get("", response_model=Pagina[ObjetivoRespuesta])
def listar_objetivos(paciente: PacienteAutorizado, session: SesionDB, pagina: ParametrosPagina):
    consulta = (
        select(Objetivo)
        .where(Objetivo.paciente_id == paciente.id)
        .order_by(Objetivo.fecha_inicio.desc(), Objetivo.id.desc())
    )
    return paginar(session, consulta, pagina)


@router.post("", response_model=ObjetivoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_objetivo(
    datos: ObjetivoGuardar, paciente: PacienteAutorizado, session: SesionDB,
):
    registro = Objetivo(paciente_id=paciente.id, **datos.model_dump())
    return guardar(session, registro)


@router.put("/{objetivo_id}", response_model=ObjetivoRespuesta, deprecated=True)
def editar_objetivo(
    objetivo_id: int, datos: ObjetivoGuardar,
    paciente: PacienteAutorizado, session: SesionDB,
):
    registro = buscar_hijo(session, Objetivo, paciente.id, objetivo_id)
    for campo, valor in datos.model_dump().items():
        setattr(registro, campo, valor)
    return guardar(session, registro)


@router.get("/{objetivo_id}", response_model=ObjetivoRespuesta)
def consultar_objetivo(objetivo_id: int, paciente: PacienteAutorizado, session: SesionDB):
    return buscar_hijo(session, Objetivo, paciente.id, objetivo_id)


@router.patch("/{objetivo_id}", response_model=ObjetivoRespuesta)
def actualizar_objetivo(
    objetivo_id: int, datos: ObjetivoEditar,
    paciente: PacienteAutorizado, session: SesionDB,
):
    registro = buscar_hijo(session, Objetivo, paciente.id, objetivo_id)
    return editar(session, registro, datos, ObjetivoGuardar)


@router.get("/{objetivo_id}/observaciones", response_model=Pagina[EvidenciaObjetivo])
def listar_evidencias(
    objetivo_id: int, paciente: PacienteAutorizado, session: SesionDB, pagina: ParametrosPagina,
):
    objetivo = buscar_hijo(session, Objetivo, paciente.id, objetivo_id)
    consulta = (
        select(Observacion, Sesion.fecha)
        .join(Sesion, Observacion.sesion_id == Sesion.id)
        .where(Observacion.objetivo_id == objetivo.id, Sesion.paciente_id == paciente.id)
        .order_by(Sesion.fecha.desc(), Observacion.id.desc())
    )
    resultado = paginar(session, consulta, pagina)
    resultado.items = [
        EvidenciaObjetivo(**observacion.model_dump(), fecha_sesion=fecha)
        for observacion, fecha in resultado.items
    ]
    return resultado
