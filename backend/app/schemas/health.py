from typing import Literal

from pydantic import BaseModel


class HealthOK(BaseModel):
    estado: Literal["ok"] = "ok"
    postgresql: Literal["conectado"] = "conectado"


class HealthUnavailable(BaseModel):
    estado: Literal["error"] = "error"
    postgresql: Literal["no_disponible"] = "no_disponible"
