"""Autenticación mediante cookie de sesión opaca y revocable."""

from fastapi import APIRouter, Request, Response, status

from app.api.dependencies import AccesoActual, ProfesionalActual, SesionDB
from app.schemas.auth import Credenciales, ProfesionalPublico, Registro
from app.services.auth import SESSION_SECONDS, iniciar_sesion, registrar_profesional, revocar_sesion


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=ProfesionalPublico, status_code=status.HTTP_201_CREATED)
def registrar(datos: Registro, session: SesionDB):
    return registrar_profesional(datos, session)


@router.post("/login", response_model=ProfesionalPublico)
def login(datos: Credenciales, request: Request, response: Response, session: SesionDB):
    profesional, token, expiration = iniciar_sesion(datos, session)
    response.set_cookie(
        "sesion", token, max_age=SESSION_SECONDS, expires=expiration,
        httponly=True, secure=request.app.state.settings.session_cookie_secure,
        samesite="lax", path="/",
    )
    return profesional


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    session: SesionDB,
    acceso: AccesoActual,
):
    revocar_sesion(acceso.sesion, session)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        "sesion", path="/", httponly=True, samesite="lax",
        secure=request.app.state.settings.session_cookie_secure,
    )
    return response


@router.get("/me", response_model=ProfesionalPublico)
def usuario_actual(profesional: ProfesionalActual):
    return profesional
