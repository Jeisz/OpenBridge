"""OpenBridge — extracción controlada de repositorios públicos de GitHub.

Etapa de exploración operacional: no accede a PostgreSQL, no guarda archivos y
no calcula content_hash. Las solicitudes HTTP están desactivadas por defecto.

Contrato de salida: (records, audit), compatible con el patrón de la notebook 03.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from time import monotonic, sleep as _sleep, time as _time
from typing import Any, Callable, Sequence

import requests

# Las primeras cinco entradas conservan la muestra de la notebook 03.
APPROVED_REPOSITORIES: tuple[str, ...] = (
    "apache/airflow",
    "react/react",
    "torvalds/linux",
    "prometheus/prometheus",
    "BurntSushi/ripgrep",
    "fastapi/fastapi",
    "django/django",
    "pallets/flask",
    "golang/go",
    "kubernetes/kubernetes",
)
DEFAULT_REPOSITORIES = APPROVED_REPOSITORIES[:5]
API_ROOT = "https://api.github.com/repos/"
TIMEOUT_SECONDS = 10
MAX_README_BYTES = 2_000_000
TRANSIENT_HTTP_CODES = {500, 502, 503, 504}


def _header(headers: Any, key: str) -> str | None:
    """Devuelve un encabezado sin asumir mayúsculas/minúsculas."""
    for candidate, value in headers.items():
        if str(candidate).lower() == key.lower() and value is not None:
            return str(value)
    return None


def _github_headers(token: str | None, *, readme: bool) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.raw+json" if readme else "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "OpenBridge-DataEngineering/0.1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _error_kind(response: Any) -> str:
    code = response.status_code
    if 300 <= code < 400:
        return "Redireccion_bloqueada"
    if code == 404:
        return "HTTP_404_no_encontrado"
    if code == 403:
        return "HTTP_403_limite_solicitudes" if _is_rate_limit(response) else "HTTP_403_acceso_denegado"
    if code == 429:
        return "HTTP_429_limite_solicitudes"
    return f"HTTP_{code}"


def _is_rate_limit(response: Any) -> bool:
    if response.status_code == 429:
        return True
    if response.status_code != 403:
        return False
    if _header(response.headers, "x-ratelimit-remaining") == "0":
        return True
    if _header(response.headers, "retry-after") is not None:
        return True
    try:
        payload = response.json()
        message = str(payload.get("message", "")).lower() if isinstance(payload, dict) else ""
    except (TypeError, ValueError):
        message = ""
    return "rate limit" in message or "rate-limit" in message


def _rate_limit_wait_seconds(response: Any, now_epoch: float) -> float:
    """Sigue las cabeceras de GitHub; sin pistas adopta 60 s por seguridad."""
    retry_after = _header(response.headers, "retry-after")
    if retry_after is not None:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            return 60.0
    if _header(response.headers, "x-ratelimit-remaining") == "0":
        reset = _header(response.headers, "x-ratelimit-reset")
        if reset is not None:
            try:
                return max(0.0, float(reset) - now_epoch + 1.0)
            except ValueError:
                pass
    return 60.0


def _approved_endpoints(
    slugs: Sequence[str],
    *,
    approved_repositories: Sequence[str] | None = None,
) -> list[tuple[str, str, str]]:
    """Construye URLs únicamente desde la lista blanca, nunca desde URLs externas."""
    if isinstance(slugs, (str, bytes)) or not slugs:
        raise ValueError("Se requiere una secuencia no vacía de repositorios aprobados")
    allowlist = (
        APPROVED_REPOSITORIES
        if approved_repositories is None
        else approved_repositories
    )
    if isinstance(allowlist, (str, bytes)) or not allowlist:
        raise ValueError("Lista blanca explícita no válida")

    allowed: dict[str, str] = {}
    for name in allowlist:
        if not isinstance(name, str) or not name.isascii():
            raise ValueError("Entrada inválida en la lista blanca")
        parts = name.split("/")
        if len(parts) != 2 or any(
            not part or any(
                not (ch.isalnum() or ch in "._-")
                for ch in part
            )
            for part in parts
        ):
            raise ValueError("Identificador inválido en la lista blanca")
        key = name.casefold()
        if key in allowed:
            raise ValueError("Repositorio duplicado en la lista blanca")
        allowed[key] = name
    seen: set[str] = set()
    endpoints: list[tuple[str, str, str]] = []
    for slug in slugs:
        if not isinstance(slug, str) or slug.casefold() not in allowed:
            raise ValueError("Repositorio fuera de la lista blanca")
        normalized = allowed[slug.casefold()]
        key = normalized.casefold()
        if key in seen:
            raise ValueError("Repositorio duplicado en la selección")
        seen.add(key)
        endpoint = f"{API_ROOT}{normalized}"
        endpoints.append((normalized, endpoint, endpoint + "/readme"))
    return endpoints


def fetch_repositories(
    slugs: Sequence[str] = DEFAULT_REPOSITORIES,
    *,
    enabled: bool = False,
    include_readme: bool = True,
    http_get: Callable[..., Any] | None = None,
    sleeper: Callable[[float], None] | None = None,
    clock: Callable[[], float] | None = None,
    max_attempts: int = 3,
    max_wait_seconds: float = 30,
    token: str | None = None,
    approved_repositories: Sequence[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extrae metadatos y README con trazabilidad, sin persistencia.

    * enabled=False: no se realiza ninguna petición (ni una autenticada).
    * 403/429: aplica Retry-After/reset si la espera cabe en max_wait_seconds;
      de lo contrario detiene TODA la ejecución para proteger la cuota.
    * 5xx y errores transitorios de red: máximo max_attempts con backoff.
    * README 404: metadatos válidos; README ausente (None).
    * Ninguna respuesta simulada se presenta como evidencia real.

    El token opcional se obtiene desde GITHUB_TOKEN únicamente si enabled=True
    y no se devuelve ni se imprime. No se ejecuta escritura en PostgreSQL.
    """
    if approved_repositories is None:
        endpoints = _approved_endpoints(slugs)
    else:
        endpoints = _approved_endpoints(
            slugs,
            approved_repositories=approved_repositories,
        )
    if not isinstance(enabled, bool):
        raise TypeError("enabled debe ser booleano")
    if not isinstance(include_readme, bool):
        raise TypeError("include_readme debe ser booleano")
    if not 1 <= max_attempts <= 5:
        raise ValueError("max_attempts debe estar entre 1 y 5")
    if max_wait_seconds < 0:
        raise ValueError("max_wait_seconds no puede ser negativo")
    if not enabled:
        return [], []

    getter = requests.get if http_get is None else http_get
    pause = _sleep if sleeper is None else sleeper
    now = _time if clock is None else clock
    auth_token = (os.getenv("GITHUB_TOKEN") if token is None else token)
    simulated = http_get is not None
    records: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []

    def request_endpoint(slug: str, url: str, *, readme: bool) -> tuple[Any | None, bool]:
        """(respuesta HTTP si existe, límite de cuota que exige detener lote)."""
        for attempt in range(1, max_attempts + 1):
            started = monotonic()
            entry: dict[str, Any] = {
                "repository": slug,
                "stage": "readme" if readme else "metadata",
                "endpoint": url,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "attempt": attempt,
                "http_status": None,
                "success": False,
                "error_type": None,
                "rate_limit_remaining": None,
                "elapsed_seconds": None,
                "is_simulated": simulated,
            }
            response = None
            retry_delay: float | None = None
            stop_batch = False
            try:
                response = getter(
                    url,
                    headers=_github_headers(auth_token, readme=readme),
                    timeout=TIMEOUT_SECONDS,
                    allow_redirects=False,
                )
                entry["http_status"] = response.status_code
                entry["rate_limit_remaining"] = _header(response.headers, "x-ratelimit-remaining")
                if response.status_code == 200:
                    entry["success"] = True
                    return response, False
                entry["error_type"] = _error_kind(response)
                if _is_rate_limit(response):
                    retry_delay = _rate_limit_wait_seconds(response, now())
                    if retry_delay > max_wait_seconds or attempt >= max_attempts:
                        stop_batch = True
                elif response.status_code in TRANSIENT_HTTP_CODES and attempt < max_attempts:
                    retry_delay = min(float(2 ** (attempt - 1)), max_wait_seconds)
                else:
                    return response, False
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                entry["error_type"] = type(exc).__name__
                if attempt < max_attempts:
                    retry_delay = min(float(2 ** (attempt - 1)), max_wait_seconds)
                else:
                    return None, False
            except requests.exceptions.RequestException:
                entry["error_type"] = "RequestException"
                return None, False
            finally:
                entry["elapsed_seconds"] = round(monotonic() - started, 3)
                audit.append(entry)
            if stop_batch:
                # Reintentarlo antes de lo indicado por GitHub sería incorrecto.
                return response, True
            if retry_delay is not None:
                pause(retry_delay)
        return response, bool(response is not None and _is_rate_limit(response))

    for slug, metadata_url, readme_url in endpoints:
        response, halt = request_endpoint(slug, metadata_url, readme=False)
        if halt:
            break
        if response is None or response.status_code != 200:
            continue
        try:
            payload = response.json()
        except (TypeError, ValueError):
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "JSON_invalido"
            continue
        if not isinstance(payload, dict):
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "JSON_no_objeto"
            continue
        github_id = payload.get("id")
        full_name = payload.get("full_name")
        fork = payload.get("fork")
        if type(github_id) is not int or github_id <= 0 or not isinstance(full_name, str):
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "Identificadores_invalidos"
            continue
        if full_name.casefold() != slug.casefold():
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "Identidad_no_coincide"
            continue
        if type(fork) is not bool:
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "Fork_no_booleano"
            continue
        if fork:
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "Fork_excluido_T05"
            continue

        record = dict(payload)
        record["_metadata_extracted_at_utc"] = audit[-1]["timestamp_utc"]
        record["_metadata_endpoint_url"] = metadata_url
        record["_metadata_source"] = "GitHub REST API"
        record["_metadata_is_simulated"] = simulated
        record["_readme_text"] = None
        record["_readme_status"] = "NO_CONSULTADO" if not include_readme else "PENDIENTE"
        records.append(record)
        if not include_readme:
            continue

        readme_response, halt = request_endpoint(slug, readme_url, readme=True)
        if halt:
            record["_readme_status"] = "LIMITE_API"
            break
        if readme_response is None:
            record["_readme_status"] = "ERROR_HTTP"
            continue
        if readme_response.status_code == 404:
            record["_readme_status"] = "NO_ENCONTRADO"
            continue
        if readme_response.status_code != 200:
            record["_readme_status"] = "ERROR_HTTP"
            continue
        content = readme_response.content
        if not isinstance(content, bytes) or len(content) > MAX_README_BYTES:
            record["_readme_status"] = "CONTENIDO_INVALIDO_O_GRANDE"
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "README_contenido_invalido_o_grande"
            continue
        try:
            record["_readme_text"] = content.decode("utf-8")
        except UnicodeDecodeError:
            record["_readme_status"] = "UTF8_INVALIDO"
            audit[-1]["success"] = False
            audit[-1]["error_type"] = "README_UTF8_invalido"
        else:
            record["_readme_status"] = "DISPONIBLE"
    return records, audit


def main() -> None:
    parser = argparse.ArgumentParser(description="Extracción GitHub OpenBridge — sin escritura SQL")
    parser.add_argument("--live", action="store_true", help="autoriza peticiones reales a GitHub")
    parser.add_argument("--count", type=int, choices=(5, 10), default=5)
    parser.add_argument("--no-readme", action="store_true", help="consulta solo metadatos")
    args = parser.parse_args()
    selected = APPROVED_REPOSITORIES[:args.count]
    records, audit = fetch_repositories(
        selected, enabled=args.live, include_readme=not args.no_readme
    )
    if not args.live:
        print("MODO SEGURO: 0 solicitudes HTTP. Para autorizar: --live --count 5")
        return
    successes = sum(1 for item in audit if item["success"])
    errors = sum(1 for item in audit if not item["success"])
    print(f"GET intentados: {len(audit)}; GET correctos: {successes}; errores: {errors}")
    print(f"Repositorios válidos: {len(records)}; READMEs disponibles: "
          f"{sum(record['_readme_status'] == 'DISPONIBLE' for record in records)}")
    print("No se guardaron registros ni se modificó PostgreSQL.")


if __name__ == "__main__":
    main()
