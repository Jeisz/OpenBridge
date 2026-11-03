"""Configuración explícita; no abre conexiones al importar."""
from dataclasses import dataclass, field
import os

DEFAULT_PAGE_SIZE = 20
DEFAULT_MAX_PAGE_SIZE = 100
DEFAULT_CONNECT_TIMEOUT_SECONDS = 5
DEFAULT_STATEMENT_TIMEOUT_MS = 8000


def _int_env(name: str, default: int, *, minimum: int = 1) -> int:
    """Lee un entero positivo del entorno y falla explícitamente si no sirve."""
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un número entero.") from exc
    if value < minimum:
        raise ValueError(f"{name} debe ser mayor o igual a {minimum}.")
    return value


@dataclass(frozen=True)
class Settings:
    """Variables de entorno de la API. Ningún valor por defecto es una credencial."""

    database_url: str | None = field(default=None, repr=False)
    cors_origins: tuple[str, ...] = ()
    default_page_size: int = DEFAULT_PAGE_SIZE
    max_page_size: int = DEFAULT_MAX_PAGE_SIZE
    db_connect_timeout: int = DEFAULT_CONNECT_TIMEOUT_SECONDS
    db_statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS

    def __post_init__(self) -> None:
        if self.default_page_size < 1:
            raise ValueError("default_page_size debe ser mayor o igual a 1.")
        if self.max_page_size < self.default_page_size:
            raise ValueError("max_page_size no puede ser menor que default_page_size.")
        if self.db_connect_timeout < 1:
            raise ValueError("db_connect_timeout debe ser mayor o igual a 1.")
        if self.db_statement_timeout_ms < 1:
            raise ValueError("db_statement_timeout_ms debe ser mayor o igual a 1.")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("DATABASE_URL") or None,
            cors_origins=tuple(
                origin.strip()
                for origin in os.getenv("CORS_ORIGINS", "").split(",")
                if origin.strip()
            ),
            default_page_size=_int_env("CATALOG_PAGE_SIZE", DEFAULT_PAGE_SIZE),
            max_page_size=_int_env("CATALOG_MAX_PAGE_SIZE", DEFAULT_MAX_PAGE_SIZE),
            db_connect_timeout=_int_env(
                "DB_CONNECT_TIMEOUT", DEFAULT_CONNECT_TIMEOUT_SECONDS
            ),
            db_statement_timeout_ms=_int_env(
                "DB_STATEMENT_TIMEOUT_MS", DEFAULT_STATEMENT_TIMEOUT_MS
            ),
        )
