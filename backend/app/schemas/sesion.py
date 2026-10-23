"""Creación, edición parcial y respuesta de sesiones de seguimiento."""

from pydantic import ConfigDict, StrictBool

from app.schemas.comun import EdicionParcial, Entrada, FechaDominio, TextoOpcional


class SesionCrear(Entrada):
    fecha: FechaDominio
    presente: StrictBool
    nota_general: TextoOpcional = None


class SesionEditar(EdicionParcial):
    campos_no_nulos = frozenset({"fecha", "presente"})

    fecha: FechaDominio | None = None
    presente: StrictBool | None = None
    nota_general: TextoOpcional = None


class SesionRespuesta(SesionCrear):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
