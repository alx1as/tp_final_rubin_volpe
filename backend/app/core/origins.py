"""Orígenes HTTP explícitos para CORS y operaciones con cookie."""

from urllib.parse import urlsplit

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


def normalize_origin(value: str) -> str:
    try:
        parts = urlsplit(value)
        if (
            parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username is not None or parts.password is not None
            or parts.path or parts.query or parts.fragment
            or value != value.strip() or any(char.isspace() for char in value)
        ):
            raise ValueError
        port = parts.port
        if port is not None and not 1 <= port <= 65535:
            raise ValueError
        host = parts.hostname.lower()
        if "*" in host or "%" in host or "\\" in host:
            raise ValueError
        if ":" in host:
            host = f"[{host}]"
        if port is not None and port != (443 if parts.scheme == "https" else 80):
            host += f":{port}"
        return f"{parts.scheme}://{host}"
    except (TypeError, ValueError):
        raise ValueError("Se requiere un origen http/https explícito, sin ruta ni credenciales") from None


class ValidateOriginMiddleware:
    def __init__(self, app: ASGIApp, allowed_origins: list[str]):
        self.app = app
        self.allowed_origins = set(allowed_origins)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and scope["method"] in {"POST", "PUT", "PATCH", "DELETE"}:
            request = Request(scope)
            origins = request.headers.getlist("origin")
            if origins:
                try:
                    origin = normalize_origin(origins[0]) if len(origins) == 1 else None
                    api_origin = normalize_origin(f"{request.url.scheme}://{request.url.netloc}")
                    allowed = origin == api_origin or origin in self.allowed_origins
                except ValueError:
                    allowed = False
                if not allowed:
                    response = JSONResponse(status_code=403, content={"detail": "Origen no permitido"})
                    await response(scope, receive, send)
                    return
        await self.app(scope, receive, send)
