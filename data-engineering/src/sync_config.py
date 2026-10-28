"""OpenBridge — configuración centralizada de la sincronización automática.

Reglas de este módulo:

* No contiene credenciales: se leen de variables de entorno y nunca se
  imprimen, registran ni serializan.
* Valida explícitamente host, puerto, usuario y base de datos del destino
  antes de permitir una conexión, y rechaza cuentas administrativas.
* No modifica ``config.py`` ni ``database.py``: esas piezas siguen sirviendo al
  pipeline histórico (una única URL con el usuario administrativo) y NO se
  usan para la ejecución diaria del catálogo.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import os
from pathlib import Path
import re

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PROJECT_ROOT.parent
DEFAULT_APPROVED_PATH = PROJECT_ROOT / "approved_repositories_100_verified.txt"

TARGET_LOCAL = "local"
TARGET_SUPABASE = "supabase"
TARGETS: tuple[str, ...] = (TARGET_LOCAL, TARGET_SUPABASE)
TARGET_ENV = "OPENBRIDGE_SYNC_TARGET"

WRITES_ENABLED_ENV = "OPENBRIDGE_SYNC_ALLOW_WRITES"
WRITE_CONFIRMATION_ENV = "OPENBRIDGE_SYNC_CONFIRMATION"
GITHUB_TOKEN_ENV = "GITHUB_TOKEN"

CONNECT_TIMEOUT_SECONDS = 10

_ADMIN_USER_PATTERN = re.compile(
    r"^(postgres|supabase_admin|supabase_auth_admin|pgbouncer|postgres\..+)$",
    re.IGNORECASE,
)
_SUPABASE_HOST_PATTERN = re.compile(
    r"^(?:[a-z0-9-]+\.)*pooler\.supabase\.com$|^db\.[a-z0-9]+\.supabase\.co$",
    re.IGNORECASE,
)
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

_TARGET_SETTINGS: dict[str, Mapping[str, object]] = {
    TARGET_LOCAL: {
        "host": ("OPENBRIDGE_LOCAL_DB_HOST", "localhost"),
        "port": ("OPENBRIDGE_LOCAL_DB_PORT", "5432"),
        "database": ("OPENBRIDGE_LOCAL_DB_NAME", "openbridge_db"),
        "user": ("OPENBRIDGE_LOCAL_DB_USER", ""),
        "password": ("OPENBRIDGE_LOCAL_DB_PASSWORD", ""),
        "sslmode": ("OPENBRIDGE_LOCAL_DB_SSLMODE", "prefer"),
        "allowed_ports": (5432,),
        "allowed_databases": ("openbridge_db",),
    },
    TARGET_SUPABASE: {
        "host": ("OPENBRIDGE_SUPABASE_DB_HOST", ""),
        "port": ("OPENBRIDGE_SUPABASE_DB_PORT", "5432"),
        "database": ("OPENBRIDGE_SUPABASE_DB_NAME", "postgres"),
        "user": ("OPENBRIDGE_SUPABASE_DB_USER", ""),
        "password": ("OPENBRIDGE_SUPABASE_DB_PASSWORD", ""),
        "sslmode": ("OPENBRIDGE_SUPABASE_DB_SSLMODE", "require"),
        "allowed_ports": (5432, 6543),
        "allowed_databases": ("postgres",),
    },
}


class SyncConfigError(ValueError):
    """Configuración incompleta o destino no autorizado.

    Los mensajes NUNCA incluyen contraseñas ni tokens.
    """


def is_admin_user(user: str) -> bool:
    """True si el usuario corresponde a una cuenta administrativa prohibida."""
    if not isinstance(user, str):
        return True
    return bool(_ADMIN_USER_PATTERN.match(user.strip()))


@dataclass(frozen=True)
class DatabaseTarget:
    """Destino autorizado. La contraseña no aparece en ``repr``/``str``."""

    name: str
    host: str
    port: int
    database: str
    user: str
    password: str = field(default="", repr=False)
    sslmode: str = "require"
    writes_allowed: bool = False

    def describe(self) -> str:
        """Resumen seguro (sin credenciales) para logs y resúmenes."""
        writes = "habilitadas" if self.writes_allowed else "deshabilitadas"
        return (
            f"target={self.name} host={self.host} port={self.port} "
            f"db={self.database} user={self.user} tls={self.sslmode} "
            f"escrituras={writes}"
        )

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.describe()

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"DatabaseTarget({self.describe()})"

    def url(self) -> URL:
        """URL de SQLAlchemy con TLS explícito; no se imprime en logs."""
        return URL.create(
            "postgresql+psycopg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query={"sslmode": self.sslmode},
        )



def _env(environ: Mapping[str, str], key: str, default: str = "") -> str:
    value = environ.get(key, default)
    if value is None:
        return default
    return str(value).strip()


def _validate_host(target: str, host: str) -> None:
    if not host:
        raise SyncConfigError("DB_HOST no está definido para el destino")
    if target == TARGET_LOCAL:
        if host.casefold() not in _LOCAL_HOSTS:
            raise SyncConfigError(
                "El destino local exige host localhost/127.0.0.1/::1"
            )
        return
    if not _SUPABASE_HOST_PATTERN.match(host):
        raise SyncConfigError(
            "El destino supabase exige un host *.pooler.supabase.com o "
            "db.<ref>.supabase.co"
        )


def _validate_user(target: str, user: str) -> None:
    if not user:
        raise SyncConfigError("DB_USER no está definido para el destino")
    if is_admin_user(user):
        raise SyncConfigError(
            "La ejecución diaria no admite cuentas administrativas "
            "(postgres/supabase_admin)"
        )
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,63}", user):
        raise SyncConfigError("DB_USER contiene caracteres no permitidos")


def load_target(
    name: str,
    *,
    environ: Mapping[str, str] | None = None,
    require_password: bool = True,
) -> DatabaseTarget:
    """Construye y valida un destino autorizado a partir del entorno.

    No abre conexiones, no imprime valores y no consulta la base de datos.
    """
    environment: Mapping[str, str] = os.environ if environ is None else environ
    if not isinstance(name, str) or name not in _TARGET_SETTINGS:
        raise SyncConfigError(
            "Destino no autorizado; valores admitidos: " + ", ".join(TARGETS)
        )
    settings = _TARGET_SETTINGS[name]

    def read(key: str) -> str:
        env_name, default = settings[key]  # type: ignore[misc]
        return _env(environment, str(env_name), str(default))

    host = read("host")
    user = read("user")
    password = read("password")
    database = read("database")
    sslmode = read("sslmode").casefold()

    _validate_host(name, host)
    _validate_user(name, user)
    if not database:
        raise SyncConfigError("DB_NAME no está definido para el destino")
    allowed_databases = tuple(settings["allowed_databases"])  # type: ignore[arg-type]
    if database not in allowed_databases:
        raise SyncConfigError(
            "Base de datos no autorizada para el destino: "
            + "/".join(allowed_databases)
        )
    try:
        port = int(read("port"))
    except (TypeError, ValueError) as exc:
        raise SyncConfigError("DB_PORT debe ser un número entero") from exc
    allowed_ports = tuple(settings["allowed_ports"])  # type: ignore[arg-type]
    if port not in allowed_ports:
        raise SyncConfigError(
            "Puerto no autorizado para el destino: "
            + ", ".join(str(item) for item in allowed_ports)
        )
    allowed_sslmode = {
        "disable", "allow", "prefer", "require", "verify-ca", "verify-full",
    }
    if sslmode not in allowed_sslmode:
        raise SyncConfigError("DB_SSLMODE no reconocido")
    if name == TARGET_SUPABASE and sslmode in {"disable", "allow"}:
        raise SyncConfigError("El destino supabase exige conexión cifrada")
    if require_password and not password:
        raise SyncConfigError(
            "Falta la contraseña del destino en las variables de entorno"
        )

    writes_allowed = _env(environment, WRITES_ENABLED_ENV) == "1"
    return DatabaseTarget(
        name=name,
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        sslmode=sslmode,
        writes_allowed=writes_allowed,
    )


def create_target_engine(target: DatabaseTarget, *, read_only: bool = True):
    """Crea un motor SQLAlchemy apuntando al destino ya validado.

    ``read_only=True`` (predeterminado) fija
    ``default_transaction_read_only=on``: cualquier escritura accidental falla
    en PostgreSQL, además del bloqueo lógico ``SET TRANSACTION READ ONLY``.
    """
    if not isinstance(target, DatabaseTarget):
        raise SyncConfigError("Se requiere un DatabaseTarget validado")
    if target.writes_allowed is False and read_only is False:
        raise SyncConfigError(
            "El destino no está habilitado para escritura "
            f"({WRITES_ENABLED_ENV}=1 requerido)"
        )
    flag = "on" if read_only else "off"
    return create_engine(
        target.url(),
        pool_pre_ping=True,
        pool_timeout=10,
        connect_args={
            "connect_timeout": CONNECT_TIMEOUT_SECONDS,
            "options": f"-c default_transaction_read_only={flag}",
        },
    )


def load_approved_repositories(path: str | Path | None = None) -> tuple[str, ...]:
    """Lee la lista aprobada y delega su validación en el extractor.

    Reutiliza ``extract_github._approved_endpoints`` para no duplicar las
    reglas de formato, ASCII y duplicados de la lista blanca.
    """
    from extract_github import _approved_endpoints

    resolved = Path(path) if path is not None else DEFAULT_APPROVED_PATH
    if not resolved.is_file():
        raise SyncConfigError(f"No existe la lista aprobada: {resolved.name}")

    names: list[str] = []
    for raw_line in resolved.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(line)
    if not names:
        raise SyncConfigError("La lista aprobada está vacía")
    try:
        _approved_endpoints(names, approved_repositories=names)
    except ValueError as exc:
        raise SyncConfigError(f"Lista aprobada inválida: {exc}") from exc
    return tuple(names)


def redact(value: object, *secrets: str | None) -> str:
    """Sustituye secretos conocidos por ``***`` antes de imprimir o guardar."""
    text = str(value)
    for secret in secrets:
        if secret and len(secret) >= 4:
            text = text.replace(secret, "***")
    return text
