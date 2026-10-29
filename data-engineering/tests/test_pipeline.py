"""Pruebas aisladas de configuración y motor; no acceden a PostgreSQL."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import URL

SRC = Path(__file__).resolve().parents[1] / "src"


@pytest.fixture
def config(monkeypatch):
    # Aislamos la prueba de cualquier .env real presente en el equipo.
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)
    valores = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "openbridge_test",
        "DB_USER": "usuario_prueba",
        "DB_PASSWORD": "clave_de_prueba",
    }
    for key, value in valores.items():
        monkeypatch.setenv(key, value)

    spec = importlib.util.spec_from_file_location("config_prueba", SRC / "config.py")
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_url_admite_caracteres_especiales(config):
    url = config.build_database_url({
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "openbridge_test",
        "DB_USER": "usuario_prueba",
        "DB_PASSWORD": "clave:@/#de_prueba",
    })
    assert isinstance(url, URL)
    assert url.password == "clave:@/#de_prueba"
    assert url.port == 5432
    assert url.drivername == "postgresql+psycopg"


def test_variable_obligatoria_ausente(config):
    valores = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    with pytest.raises(ValueError, match="DB_NAME"):
        config.build_database_url(valores)


@pytest.mark.parametrize("puerto", ["texto", "0", "65536"])
def test_puerto_invalido(config, puerto):
    valores = {
        "DB_HOST": "localhost",
        "DB_PORT": puerto,
        "DB_NAME": "openbridge_test",
        "DB_USER": "usuario_prueba",
        "DB_PASSWORD": "clave_de_prueba",
    }
    with pytest.raises(ValueError, match="DB_PORT"):
        config.build_database_url(valores)


def test_motor_y_consulta_sin_postgresql(monkeypatch, capsys):
    url = URL.create("postgresql+psycopg", username="prueba", password="ficticia",
                     host="localhost", port=5432, database="openbridge_test")
    config_falso = ModuleType("config")
    config_falso.DATABASE_URL = url
    monkeypatch.setitem(sys.modules, "config", config_falso)

    motor_falso = MagicMock()
    conexion = motor_falso.connect.return_value.__enter__.return_value
    conexion.execute.return_value.scalar_one.return_value = "openbridge_test"
    crear_motor = MagicMock(return_value=motor_falso)
    monkeypatch.setattr("sqlalchemy.create_engine", crear_motor)

    spec = importlib.util.spec_from_file_location("database_prueba", SRC / "database.py")
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    assert modulo.test_connection() == "openbridge_test"
    crear_motor.assert_called_once_with(
        url,
        pool_pre_ping=True,
        pool_timeout=10,
        connect_args={"connect_timeout": 10},
    )
    assert "Conexión exitosa" in capsys.readouterr().out
    conexion.execute.assert_called_once()
