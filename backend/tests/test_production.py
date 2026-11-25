"""El despliegue sirve la interfaz sin modificar las rutas de la API."""
from fastapi.testclient import TestClient
import pytest

from app.core.config import Settings
from app.production import create_production_app


def test_frontend_y_api_comparten_origen(tmp_path):
    (tmp_path / "index.html").write_text("<html>TRAMA</html>", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('TRAMA');", encoding="utf-8")
    settings = Settings(_env_file=None, database_url="postgresql+psycopg://localhost/trama_test")
    with TestClient(create_production_app(settings, tmp_path)) as client:
        assert "TRAMA" in client.get("/").text
        assert client.get("/assets/app.js").status_code == 200
        assert "/api/auth/me" in client.get("/openapi.json").json()["paths"]
        assert client.get("/api/no-existe").status_code == 404


def test_sin_frontend_compilado_falla_de_forma_explicita(tmp_path):
    with pytest.raises(RuntimeError, match="frontend compilado"):
        create_production_app(frontend_dir=tmp_path)
