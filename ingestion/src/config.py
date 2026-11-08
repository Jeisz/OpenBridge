
"""Configuración de PostgreSQL para OpenBridge y Supabase.

Las credenciales y el host se leen de variables de entorno: este módulo se
publica en un repositorio compartido y no debe contener datos del proyecto.
Acepta los nombres `SUPABASE_DB_*` y, por compatibilidad con el pipeline
histórico, también `DB_*`.
"""

import os
from collections.abc import Mapping
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

# =========================================================
# CONFIGURACION DE SUPABASE
# =========================================================

SUPABASE_SETTINGS = {
    "DB_HOST": os.getenv("SUPABASE_DB_HOST") or os.getenv("DB_HOST", ""),
    "DB_PORT": os.getenv("SUPABASE_DB_PORT") or os.getenv("DB_PORT", "5432"),
    "DB_NAME": os.getenv("SUPABASE_DB_NAME") or os.getenv("DB_NAME", "postgres"),
    "DB_USER": os.getenv("SUPABASE_DB_USER") or os.getenv("DB_USER", ""),
    "DB_PASSWORD": os.getenv("SUPABASE_DB_PASSWORD") or os.getenv("DB_PASSWORD", ""),
}

# Variables conservadas para compatibilidad con OpenBridge.
DB_HOST = SUPABASE_SETTINGS["DB_HOST"]
DB_PORT = SUPABASE_SETTINGS["DB_PORT"]
DB_NAME = SUPABASE_SETTINGS["DB_NAME"]
DB_USER = SUPABASE_SETTINGS["DB_USER"]
DB_PASSWORD = SUPABASE_SETTINGS["DB_PASSWORD"]

_REQUIRED = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
)


def build_database_url(
    settings: Mapping[str, str] | None = None,
) -> URL:
    """Construye la URL de conexión sin exponer la contraseña."""

    values = SUPABASE_SETTINGS if settings is None else settings

    missing = [
        key
        for key in _REQUIRED
        if not str(values.get(key) or "").strip()
    ]

    if missing:
        raise ValueError(
            "Faltan variables de conexión: "
            + ", ".join(missing)
        )

    try:
        port = int(values["DB_PORT"])
    except (ValueError, TypeError) as exc:
        raise ValueError(
            "DB_PORT debe ser un número entero."
        ) from exc

    if not 1 <= port <= 65535:
        raise ValueError(
            "DB_PORT debe estar entre 1 y 65535."
        )

    return URL.create(
        "postgresql+psycopg",
        username=values["DB_USER"],
        password=values["DB_PASSWORD"],
        host=values["DB_HOST"],
        port=port,
        database=values["DB_NAME"],
        query={"sslmode": "require"},
    )


DATABASE_URL = build_database_url()
