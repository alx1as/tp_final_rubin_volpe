"""Configuración desde el entorno o backend/.env, sin exponer la URL."""

from pathlib import Path

from pydantic import SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    database_url: SecretStr

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
            if (
                url.drivername != "postgresql+psycopg"
                or not url.host
                or not url.database
                or (url.port is not None and not 1 <= url.port <= 65535)
            ):
                raise ValueError
        except (ArgumentError, ValueError, TypeError):
            raise ValueError(
                "DATABASE_URL debe ser una URL postgresql+psycopg con host y base válidos"
            ) from None
        return value


def load_settings() -> Settings:
    try:
        return Settings()
    except (ValidationError, SettingsError):
        raise RuntimeError(
            "Configuración inválida: revise DATABASE_URL en el entorno o backend/.env. "
            "Use backend/.env.example como referencia."
        ) from None
