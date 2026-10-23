"""Hash de contraseñas y tokens opacos, independientes del transporte HTTP."""

from functools import lru_cache
import hashlib
import secrets

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hasher.verify(password, hashed)
    except (UnknownHashError, ValueError):
        # Un hash previo inválido no permite el acceso ni expone su contenido.
        return False


@lru_cache(maxsize=1)
def dummy_password_hash() -> str:
    # Permite verificar también cuando el correo no existe.
    return hash_password(secrets.token_urlsafe(32))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
