"""Ejecución de proveedores sin filtrar errores ni aceptar contenido vacío."""

from collections.abc import Callable

from app.integrations.contratos import IntegracionNoDisponible


def ejecutar_integracion(operacion: Callable[[], str]) -> str:
    try:
        texto = operacion()
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("Respuesta de proveedor inválida")
        return texto.strip()
    except Exception:
        # El detalle del proveedor puede contener credenciales o contenido del
        # registro. No devolverlo, registrarlo ni incorporarlo a otro mensaje.
        raise IntegracionNoDisponible from None
