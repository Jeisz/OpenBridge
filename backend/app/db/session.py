"""Motor SQLAlchemy 2 Core de solo lectura; no conecta al importar."""
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from backend.app.core.config import Settings
from backend.app.core.errors import CatalogUnavailableError

POOL_SIZE = 5
MAX_OVERFLOW = 5


def normalize_dsn(url: str) -> str:
    """Acepta el DSN de Supabase tal cual y fuerza el driver psycopg 3."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def build_engine(settings: Settings) -> Engine | None:
    """Crea el motor sin abrir conexiones. Sin DATABASE_URL no hay motor."""
    if not settings.database_url:
        return None
    return create_engine(
        normalize_dsn(settings.database_url),
        pool_pre_ping=True,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        # La API solo lee: sin transacciones abiertas que bloqueen al ingestor.
        isolation_level="AUTOCOMMIT",
        connect_args={
            "connect_timeout": settings.db_connect_timeout,
            "application_name": "openbridge-api",
            "options": f"-c statement_timeout={settings.db_statement_timeout_ms}",
        },
    )


def get_engine(request: Request) -> Engine:
    """Dependencia de FastAPI: el motor vive en `app.state`."""
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        raise CatalogUnavailableError(
            "La API no tiene DATABASE_URL configurado; no hay catálogo que consultar."
        )
    return engine
