from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.health import HealthOK, HealthUnavailable
from app.services.health import check_database

router = APIRouter()


@router.get(
    "/salud",
    tags=["Salud"],
    response_model=HealthOK,
    responses={503: {"model": HealthUnavailable, "description": "PostgreSQL no disponible"}},
)
def health(session: Annotated[Session, Depends(get_session)]):
    try:
        if check_database(session):
            return HealthOK()
    except SQLAlchemyError:
        pass
    return JSONResponse(status_code=503, content=HealthUnavailable().model_dump())
