"""OpenBridge: normalización local de datos extraídos de GitHub (sin SQL ni HTTP).

Entrada: ``records`` devuelto por ``extract_github.fetch_repositories``.
Salida: filas preparadas para revisión y pruebas, *no* para carga automática.

NOTA T05: ``content_hash`` se deja deliberadamente sin calcular hasta que
Ingesta + IA aprueben la serialización y el tratamiento de hashes históricos.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence


class TransformationError(ValueError):
    """Los registros no satisfacen las reglas de validación de ingesta."""


@dataclass(frozen=True)
class TransformationResult:
    repositories: list[dict[str, Any]]
    readmes: list[dict[str, Any]]
    observations: list[dict[str, str]]


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TransformationError(f"{field}: se requiere texto no vacío")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TransformationError(f"{field}: se esperaba texto o None")
    return value.strip() or None


def _nonnegative_int(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise TransformationError(f"{field}: se requiere entero no negativo")
    return value


def _parse_github_date(value: Any) -> str | None:
    """Conserva texto ISO original; PostgreSQL actual registra pushed_at como TEXT."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise TransformationError("pushed_at: se esperaba texto ISO 8601 o None")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TransformationError("pushed_at: formato ISO 8601 inválido") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TransformationError("pushed_at: se requiere zona horaria")
    return value


def _topics(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise TransformationError("topics: se esperaba una lista")
    seen: set[str] = set()
    normalized: list[str] = []
    for topic in value:
        text = _required_text(topic, "topics[]").lower()
        if text not in seen:
            normalized.append(text)
            seen.add(text)
    return normalized


def _license_id(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TransformationError("license: se esperaba objeto o None")
    return _optional_text(value.get("spdx_id"), "license.spdx_id")


def transform_records(records: Sequence[Mapping[str, Any]]) -> TransformationResult:
    """Valida y normaliza registros; ante un error aborta sin salida parcial.

    Los README ausentes o no consultados no generan filas ``catalog_readmes``.
    Los errores transitorios de README se señalan en ``observations``: esta
    fase nunca convierte fallos de descarga en README vacío o en texto ``None``.

    No genera ``content_hash`` ni escritura SQL. No edita los diccionarios de
    entrada. Idempotencia de UPSERT todavía NO evaluada.
    """
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise TransformationError("records: se requiere una secuencia de registros")

    repositories: list[dict[str, Any]] = []
    readmes: list[dict[str, Any]] = []
    observations: list[dict[str, str]] = []
    seen_ids: set[int] = set()
    seen_names: set[str] = set()

    for position, record in enumerate(records, start=1):
        if not isinstance(record, Mapping):
            raise TransformationError(f"registro {position}: se esperaba objeto")

        github_id = record.get("id")
        if type(github_id) is not int or github_id <= 0:
            raise TransformationError(f"registro {position}: id GitHub positivo requerido")
        full_name = _required_text(record.get("full_name"), "full_name")
        name = _required_text(record.get("name"), "name")
        if full_name.count("/") != 1 or full_name.split("/")[1].casefold() != name.casefold():
            raise TransformationError(f"registro {position}: full_name y name inconsistentes")
        if github_id in seen_ids or full_name.casefold() in seen_names:
            raise TransformationError(f"registro {position}: repositorio duplicado")
        seen_ids.add(github_id)
        seen_names.add(full_name.casefold())

        fork = record.get("fork")
        if type(fork) is not bool:
            raise TransformationError(f"registro {position}: fork debe ser booleano")
        if fork:
            raise TransformationError(f"registro {position}: no se admiten forks (T05)")
        archived = record.get("archived")
        if type(archived) is not bool:
            raise TransformationError(f"registro {position}: archived debe ser booleano")

        repo = {
            "github_id": github_id,
            "full_name": full_name,
            "name": name,
            "description": _optional_text(record.get("description"), "description"),
            "homepage": _optional_text(record.get("homepage"), "homepage"),
            "language": _optional_text(record.get("language"), "language"),
            "topics": _topics(record.get("topics")),
            "stargazers_count": _nonnegative_int(record.get("stargazers_count"), "stargazers_count"),
            "forks_count": _nonnegative_int(record.get("forks_count"), "forks_count"),
            "pushed_at": _parse_github_date(record.get("pushed_at")),
            "archived": archived,
            "license_spdx_id": _license_id(record.get("license")),
        }

        status = record.get("_readme_status")
        if status == "DISPONIBLE":
            readme_text = record.get("_readme_text")
            if not isinstance(readme_text, str):
                raise TransformationError(f"registro {position}: README disponible sin texto válido")
            readmes.append({"github_id": github_id, "readme_text": readme_text})
        elif status in {"NO_CONSULTADO", "NO_ENCONTRADO"}:
            observations.append({"full_name": full_name, "readme_status": status})
        elif status in {"ERROR_HTTP", "LIMITE_API", "CONTENIDO_INVALIDO_O_GRANDE", "UTF8_INVALIDO"}:
            observations.append({"full_name": full_name, "readme_status": status})
        else:
            raise TransformationError(f"registro {position}: estado README desconocido o pendiente")

        repositories.append(repo)

    return TransformationResult(repositories, readmes, observations)
