"""Sesión de acceso revocable; las tablas se instalan mediante SQL manual."""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class SesionAutenticacion(SQLModel, table=True):
    __tablename__ = "sesion_autenticacion"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_sesion_autenticacion_token_hash"),
        CheckConstraint("token_hash ~ '^[0-9a-f]{64}$'", name="ck_sesion_autenticacion_hash"),
        CheckConstraint("vence_en > creada_en", name="ck_sesion_autenticacion_vencimiento"),
        CheckConstraint(
            "revocada_en IS NULL OR revocada_en >= creada_en",
            name="ck_sesion_autenticacion_revocacion",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    profesional_id: int = Field(foreign_key="profesional.id", ondelete="RESTRICT")
    token_hash: str = Field(repr=False)
    creada_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True), nullable=False,
    )
    vence_en: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    revocada_en: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
