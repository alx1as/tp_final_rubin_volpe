"""Informes editables con período válido y creación como borrador."""

from datetime import date
from typing import Literal

from pydantic import ConfigDict, Field, StrictBool, model_validator

from app.schemas.comun import EdicionParcial, Entrada, FechaDominio, TextoRequerido


EstadoInforme = Literal["borrador", "finalizado"]


class InformeDatos(Entrada):
    titulo: TextoRequerido
    fecha: FechaDominio = Field(default_factory=date.today)
    periodo_desde: FechaDominio
    periodo_hasta: FechaDominio
    contenido: TextoRequerido
    estado: EstadoInforme = "borrador"
    asistido_ia: StrictBool = False

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.periodo_hasta < self.periodo_desde:
            raise ValueError("El final del período no puede ser anterior al inicio")
        return self


class InformeCrear(InformeDatos):
    estado: Literal["borrador"] = "borrador"


class InformeEditar(EdicionParcial):
    campos_no_nulos = frozenset({
        "titulo", "fecha", "periodo_desde", "periodo_hasta", "contenido", "estado", "asistido_ia",
    })

    titulo: TextoRequerido | None = None
    fecha: FechaDominio | None = None
    periodo_desde: FechaDominio | None = None
    periodo_hasta: FechaDominio | None = None
    contenido: TextoRequerido | None = None
    estado: EstadoInforme | None = None
    asistido_ia: StrictBool | None = None


class InformeRespuesta(InformeDatos):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
