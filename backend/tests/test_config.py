import pytest
from pydantic import ValidationError

from app.core.config import Settings, load_settings


def test_loads_dotenv_and_environment_takes_priority(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    env_file = tmp_path / ".env"
    file_url = "postgresql+psycopg://localhost/from_file"
    env_file.write_text(f"DATABASE_URL={file_url}\n", encoding="utf-8")
    assert Settings(_env_file=env_file).database_url.get_secret_value() == file_url
    env_url = "postgresql+psycopg://localhost/from_environment"
    monkeypatch.setenv("DATABASE_URL", env_url)
    assert Settings(_env_file=env_file).database_url.get_secret_value() == env_url


@pytest.mark.parametrize(
    "url",
    ["", "invalid", "sqlite:///local.db", "postgresql://localhost/db",
     "postgresql+psycopg:///db", "postgresql+psycopg://localhost",
     "postgresql+psycopg://localhost:invalid/db",
     "postgresql+psycopg://localhost:70000/db"],
)
def test_rejects_invalid_urls_without_exposing_input(url):
    with pytest.raises(ValidationError) as caught:
        Settings(_env_file=None, database_url=url)
    assert "input_value" not in str(caught.value)


def test_settings_repr_masks_url():
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://test_user:synthetic_secret@localhost/test_db",
    )
    assert "synthetic_secret" not in repr(settings)
    assert "test_user" not in repr(settings)


@pytest.mark.parametrize("value", [None, "bad://user:synthetic_secret@localhost/db"])
def test_factory_configuration_error_is_safe(monkeypatch, tmp_path, value):
    from app.main import create_app

    monkeypatch.setitem(Settings.model_config, "env_file", tmp_path / "absent.env")
    if value is None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("DATABASE_URL", value)
    with pytest.raises(RuntimeError, match="revise DATABASE_URL") as caught:
        create_app()
    assert "synthetic_secret" not in str(caught.value)
    assert caught.value.__suppress_context__
