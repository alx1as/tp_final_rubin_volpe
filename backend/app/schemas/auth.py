"""Entradas privadas y respuesta pública de las cuentas profesionales."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class Credenciales(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=1024)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class Registro(Credenciales):
    nombre: str
    apellido: str
    password: SecretStr = Field(min_length=8, max_length=1024)

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo es obligatorio")
        return value

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("La contraseña no puede estar vacía")
        return value


class ProfesionalPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    email: str
    activo: bool
