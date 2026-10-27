"""Persistencia de informes propios, disponible sin proveedores externos."""

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, SesionDB
from app.models import Informe
from app.integrations.dependencies import GeneradorActual
from app.schemas.comun import Pagina
from app.schemas.informe import InformeCrear, InformeDatos, InformeEditar, InformeRespuesta
from app.schemas.integraciones import BorradorGenerado, SolicitudBorrador
from app.services.generacion import generar_borrador
from app.services.perfil import buscar_hijo, editar, guardar, paginar


router = APIRouter(prefix="/pacientes/{paciente_id}/informes", tags=["Informes"])


@router.get("", response_model=Pagina[InformeRespuesta])
def listar_informes(paciente: PacienteAutorizado, session: SesionDB, pagina: ParametrosPagina):
    consulta = (
        select(Informe).where(Informe.paciente_id == paciente.id)
        .order_by(Informe.fecha.desc(), Informe.id.desc())
    )
    return paginar(session, consulta, pagina)


@router.post("", response_model=InformeRespuesta, status_code=status.HTTP_201_CREATED)
def crear_informe(datos: InformeCrear, paciente: PacienteAutorizado, session: SesionDB):
    return guardar(session, Informe(paciente_id=paciente.id, **datos.model_dump()))


@router.post("/generar", response_model=BorradorGenerado)
def generar_informe(
    datos: SolicitudBorrador, paciente: PacienteAutorizado, session: SesionDB, generador: GeneradorActual,
):
    return generar_borrador(session, paciente, datos, generador)


@router.get("/{informe_id}", response_model=InformeRespuesta)
def consultar_informe(informe_id: int, paciente: PacienteAutorizado, session: SesionDB):
    return buscar_hijo(session, Informe, paciente.id, informe_id)


@router.patch("/{informe_id}", response_model=InformeRespuesta)
def editar_informe(
    informe_id: int, datos: InformeEditar, paciente: PacienteAutorizado, session: SesionDB,
):
    registro = buscar_hijo(session, Informe, paciente.id, informe_id)
    return editar(session, registro, datos, InformeDatos)
