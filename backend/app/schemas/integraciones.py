"""Solicitudes de generación y resultados temporales revisables."""

from typing import Literal

from pydantic import model_validator

from app.schemas.comun import Entrada, FechaDominio, TextoRequerido
from app.schemas.informe import InformeCrear


class SolicitudBorrador(Entrada):
    titulo: TextoRequerido
    periodo_desde: FechaDominio
    periodo_hasta: FechaDominio

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.periodo_hasta < self.periodo_desde:
            raise ValueError("El final del período no puede ser anterior al inicio")
        return self


class BorradorGenerado(InformeCrear):
    asistido_ia: Literal[True] = True


class TranscripcionRespuesta(Entrada):
    texto: TextoRequerido
