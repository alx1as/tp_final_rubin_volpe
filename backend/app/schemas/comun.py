"""Tipos de dominio, listas y validación de ediciones parciales."""

from datetime import date
import re
from typing import Annotated, ClassVar, Generic, TypeVar

from fastapi.exceptions import RequestValidationError
from pydantic import (
    AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field,
    ValidationError, ValidationInfo, field_validator,
)


def texto_requerido(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("El campo es obligatorio")
    return value


def texto_opcional(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("El campo debe ser texto")
    return value.strip() or None


def fecha_dominio(value):
    if type(value) is date:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return value
    raise ValueError("La fecha debe usar el formato YYYY-MM-DD")


def fecha_vacia(value):
    if isinstance(value, str):
        return value.strip() or None
    return value


TextoRequerido = Annotated[str, AfterValidator(texto_requerido)]
TextoOpcional = Annotated[str | None, BeforeValidator(texto_opcional)]
FechaDominio = Annotated[date, BeforeValidator(fecha_dominio)]
FechaOpcional = Annotated[FechaDominio | None, BeforeValidator(fecha_vacia)]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EdicionParcial(Entrada):
    campos_no_nulos: ClassVar[frozenset[str]] = frozenset()

    @field_validator("*", mode="before")
    @classmethod
    def rechazar_null_obligatorio(cls, value, info: ValidationInfo):
        if value is None and info.field_name in cls.campos_no_nulos:
            raise ValueError("El campo no admite null")
        return value


class Paginacion(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int


def validar_edicion(actual: dict, cambios: BaseModel, esquema: type[BaseModel]) -> dict:
    enviados = cambios.model_dump(exclude_unset=True)
    try:
        completo = esquema.model_validate(actual | enviados)
    except ValidationError as error:
        errors = [item | {"loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from None
    return {campo: getattr(completo, campo) for campo in enviados}
