"""Cronología autorizada con filtros de fecha inclusivos."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencies import PacienteAutorizado, ParametrosPagina, SesionDB
from app.schemas.comun import FechaDominio, Pagina
from app.schemas.cronologia import EntradaCronologia
from app.services.cronologia import consultar_cronologia


router = APIRouter(prefix="/pacientes/{paciente_id}/cronologia", tags=["Cronología"])


@router.get("", response_model=Pagina[EntradaCronologia])
def listar_cronologia(
    paciente: PacienteAutorizado, session: SesionDB, pagina: ParametrosPagina,
    desde: Annotated[FechaDominio | None, Query()] = None,
    hasta: Annotated[FechaDominio | None, Query()] = None,
):
    if desde is not None and hasta is not None and hasta < desde:
        raise HTTPException(status_code=422, detail="Hasta no puede ser anterior a desde")
    return consultar_cronologia(session, paciente.id, pagina, desde, hasta)
