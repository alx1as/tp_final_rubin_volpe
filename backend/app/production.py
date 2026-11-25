"""Publicación de frontend y API bajo un mismo origen HTTP."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import Settings
from app.main import create_app


def create_production_app(settings: Settings | None = None, frontend_dir: Path | None = None) -> FastAPI:
    directorio = frontend_dir or Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if not (directorio / "index.html").is_file():
        raise RuntimeError("No se encontró el frontend compilado. Ejecutar npm run build en frontend.")
    app = create_app(settings)
    # Se registra al final: las rutas /api y Swagger conservan su prioridad.
    app.mount("/", StaticFiles(directory=directorio, html=True), name="frontend")
    return app
