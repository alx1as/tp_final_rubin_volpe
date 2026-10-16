import os

import pytest
from sqlalchemy.engine import make_url

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def postgres_settings():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Configurar TEST_DATABASE_URL para PostgreSQL exclusivo de pruebas")
    settings = Settings(_env_file=None, database_url=url)
    if not make_url(settings.database_url.get_secret_value()).database.endswith("_test"):
        pytest.fail("La base de TEST_DATABASE_URL debe terminar en _test")
    return settings


@pytest.fixture
def postgres_app(postgres_settings):
    app = create_app(postgres_settings)
    try:
        yield app
    finally:
        app.state.engine.dispose()
