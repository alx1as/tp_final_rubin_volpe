"""Interfaces de servicios externos; este módulo no elige ni ejecuta proveedores."""

from dataclasses import dataclass
from datetime import date
from typing import BinaryIO, Protocol

from app.schemas.cronologia import EntradaCronologia
from app.schemas.objetivo import ObjetivoRespuesta
from app.schemas.paciente import PacienteRespuesta


class IntegracionNoConfigurada(Exception):
    """No se registró un proveedor para la operación solicitada."""


class IntegracionNoDisponible(Exception):
    """El proveedor falló o devolvió una respuesta no utilizable."""


class Transcriptor(Protocol):
    def transcribir(
        self, audio: BinaryIO, *, nombre_archivo: str | None, tipo_contenido: str | None,
    ) -> str:
        """Leer un stream prestado y devolver texto, sin conservarlo ni cerrarlo.

        El llamador cierra el audio. El adaptador real debe limpiar los recursos
        adicionales que cree, fijar sus timeouts y traducir errores del proveedor.
        El nombre es metadato; nunca debe usarse como una ruta local de destino.
        """
        ...


@dataclass(frozen=True)
class ContextoInforme:
    """Datos públicos y copias separadas de las fuentes del período autorizado."""

    titulo: str
    periodo_desde: date
    periodo_hasta: date
    paciente: PacienteRespuesta
    sesiones: tuple[EntradaCronologia, ...]
    objetivos: tuple[ObjetivoRespuesta, ...]


class GeneradorInformes(Protocol):
    def generar(self, contexto: ContextoInforme) -> str:
        """Sintetizar solo las fuentes recibidas, sin diagnósticos ni persistencia.

        Devuelve contenido editable. Estado, identidad, fecha y marca de asistencia
        pertenecen a la aplicación. El adaptador real fija timeouts de su cliente.
        """
        ...
