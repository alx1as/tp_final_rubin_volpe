"""Operaciones de cuentas y sesiones de acceso."""

from datetime import datetime, timedelta, timezone
import secrets
import re

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.security import dummy_password_hash, hash_password, hash_token, verify_password
from app.models import Profesional, SesionAutenticacion
from app.schemas.auth import Credenciales, Registro


SESSION_SECONDS = 8 * 60 * 60


def registrar_profesional(datos: Registro, session: Session) -> Profesional:
    profesional = Profesional(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=str(datos.email).lower(),
        password_hash=hash_password(datos.password.get_secret_value()),
    )
    session.add(profesional)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se pudo registrar el correo indicado") from None
    session.refresh(profesional)
    return profesional


def iniciar_sesion(datos: Credenciales, session: Session) -> tuple[Profesional, str, datetime]:
    profesional = session.exec(select(Profesional).where(
        func.lower(func.btrim(Profesional.email)) == str(datos.email).lower()
    )).first()
    password_hash = profesional.password_hash if profesional is not None else dummy_password_hash()
    valid_password = verify_password(datos.password.get_secret_value(), password_hash)
    if profesional is None or not valid_password or not profesional.activo:
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(seconds=SESSION_SECONDS)
    session.add(SesionAutenticacion(
        profesional_id=profesional.id, token_hash=hash_token(token),
        creada_en=now, vence_en=expiration,
    ))
    session.commit()
    return profesional, token, expiration


def validar_sesion(token: str | None, session: Session) -> tuple[SesionAutenticacion, Profesional]:
    if token is None or re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is None:
        raise HTTPException(status_code=401, detail="Se requiere una sesión válida")
    result = session.exec(
        select(SesionAutenticacion, Profesional)
        .join(Profesional, Profesional.id == SesionAutenticacion.profesional_id)
        .where(
            SesionAutenticacion.token_hash == hash_token(token),
            SesionAutenticacion.vence_en > datetime.now(timezone.utc),
            SesionAutenticacion.revocada_en.is_(None),
            Profesional.activo.is_(True),
        )
    ).first()
    if result is None:
        raise HTTPException(status_code=401, detail="Se requiere una sesión válida")
    return result[0], result[1]


def revocar_sesion(sesion: SesionAutenticacion, session: Session) -> None:
    sesion.revocada_en = datetime.now(timezone.utc)
    session.add(sesion)
    session.commit()
