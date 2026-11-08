"""Contrato OpenBridge SHA-256 v1 (offline; sin HTTP, SQL ni E/S al importar).

Genera huellas para consumo de IA sobre repositorios YA transformados.
Los hashes heredados de PostgreSQL NO se leen, comparan ni reescriben.
No es una herramienta de persistencia y no habilita escrituras en load.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping
import unicodedata

from transform import TransformationResult

HASH_VERSION = "openbridge-ai-v1"
REPOSITORY_FIELDS = (
    "github_id", "full_name", "name", "description", "homepage",
    "language", "topics", "stargazers_count", "forks_count",
    "pushed_at", "archived", "license_spdx_id",
)
_NULLABLE_TEXT = {"description", "homepage", "language", "license_spdx_id"}
_REQUIRED_TEXT = {"full_name", "name"}
_NONNEGATIVE_INTS = {"stargazers_count", "forks_count"}


class ContentHashError(ValueError):
    """Entrada incompleta o ambigua para calcular un hash verificable."""


@dataclass(frozen=True)
class HashPreview:
    github_id: int
    full_name: str
    content_hash: str
    content_hash_version: str
    readme_state: str


def _text(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str):
        raise ContentHashError(f"{label}: se esperaba texto{' o None' if nullable else ''}")
    if not nullable and not value.strip():
        raise ContentHashError(f"{label}: se requiere texto no vacío")
    return unicodedata.normalize("NFC", value)


def _timestamp(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ContentHashError("pushed_at: se esperaba ISO 8601 con zona horaria o None")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContentHashError("pushed_at: ISO 8601 inválido") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContentHashError("pushed_at: zona horaria obligatoria")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _repository_payload(repo: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(repo, Mapping):
        raise ContentHashError("repositorio: se esperaba un diccionario")
    actual = set(repo)
    expected = set(REPOSITORY_FIELDS)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ContentHashError(f"campos del repositorio incompatibles: faltan={missing}, sobran={unexpected}")
    identifier = repo["github_id"]
    if type(identifier) is not int or identifier <= 0:
        raise ContentHashError("github_id: entero positivo obligatorio")
    payload: dict[str, Any] = {"github_id": identifier}

    for field in _REQUIRED_TEXT:
        payload[field] = _text(repo[field], field)
    if payload["full_name"].count("/") != 1 or payload["full_name"].split("/")[1].casefold() != payload["name"].casefold():
        raise ContentHashError("full_name y name no coinciden")
    for field in _NULLABLE_TEXT:
        payload[field] = _text(repo[field], field, nullable=True)
    for field in _NONNEGATIVE_INTS:
        value = repo[field]
        if type(value) is not int or value < 0:
            raise ContentHashError(f"{field}: entero no negativo obligatorio")
        payload[field] = value
    if type(repo["archived"]) is not bool:
        raise ContentHashError("archived: se esperaba booleano")
    payload["archived"] = repo["archived"]
    payload["pushed_at"] = _timestamp(repo["pushed_at"])

    topics = repo["topics"]
    if not isinstance(topics, list):
        raise ContentHashError("topics: se esperaba lista")
    clean_topics: list[str] = []
    for topic in topics:
        item = _text(topic, "topics[]")
        if item != item.strip() or item != item.lower():
            raise ContentHashError("topics: deben estar previamente normalizados en minúsculas y sin espacios externos")
        clean_topics.append(item)
    if len(set(clean_topics)) != len(clean_topics):
        raise ContentHashError("topics: etiquetas duplicadas; ejecutar transform_records antes")
    payload["topics"] = sorted(clean_topics)
    return payload


def canonical_json(repo: Mapping[str, Any], readme_text: str | None) -> str:
    """JSON v1 exacto: claves ordenadas, sin espacios, UTF-8, texto en NFC.

    README: diferencia estrictamente ``None`` (404 confirmado) de "".
    No se recortan espacios ni se normalizan saltos de línea del README.
    """
    if readme_text is not None and not isinstance(readme_text, str):
        raise ContentHashError("readme_text: se esperaba texto o None")
    document = {
        "contract_version": HASH_VERSION,
        "repository": _repository_payload(repo),
        "readme_text": None if readme_text is None else unicodedata.normalize("NFC", readme_text),
    }
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash_v1(repo: Mapping[str, Any], readme_text: str | None) -> str:
    """Devuelve hex SHA-256 (64 caracteres) del JSON canónico codificado en UTF-8."""
    return hashlib.sha256(canonical_json(repo, readme_text).encode("utf-8")).hexdigest()


def preview_transformation_hashes(result: TransformationResult) -> list[HashPreview]:
    """Previsualiza hashes sin alterar objetos ni ejecutar solicitudes HTTP/SQL.

    Sólo permite README presente o 404 verificado (NO_ENCONTRADO).
    Si no se consultó o falló la descarga del README, falla cerrado.
    """
    if not isinstance(result, TransformationResult):
        raise ContentHashError("se requiere TransformationResult")
    repo_by_id: dict[int, Mapping[str, Any]] = {}
    name_to_id: dict[str, int] = {}
    for repo in result.repositories:
        payload = _repository_payload(repo)
        identifier, fullname = payload["github_id"], payload["full_name"].casefold()
        if identifier in repo_by_id or fullname in name_to_id:
            raise ContentHashError("repositorios duplicados")
        repo_by_id[identifier] = repo
        name_to_id[fullname] = identifier

    readmes: dict[int, str] = {}
    for item in result.readmes:
        if not isinstance(item, Mapping):
            raise ContentHashError("README: se esperaba diccionario")
        identifier = item.get("github_id")
        content = item.get("readme_text")
        if type(identifier) is not int or identifier not in repo_by_id or identifier in readmes:
            raise ContentHashError("README duplicado o huérfano")
        if not isinstance(content, str):
            raise ContentHashError("README disponible sin texto")
        readmes[identifier] = content

    absent: set[int] = set()
    for obs in result.observations:
        if not isinstance(obs, Mapping):
            raise ContentHashError("observación: se esperaba diccionario")
        name = obs.get("full_name")
        if not isinstance(name, str) or name.casefold() not in name_to_id:
            raise ContentHashError("observación sin repositorio asociado")
        identifier = name_to_id[name.casefold()]
        if obs.get("readme_status") != "NO_ENCONTRADO":
            raise ContentHashError(f"README no verificable: {name}; estado={obs.get('readme_status')}")
        if identifier in absent or identifier in readmes:
            raise ContentHashError("estado README incompatible o duplicado")
        absent.add(identifier)

    if (set(repo_by_id) - set(readmes) - absent):
        raise ContentHashError("faltan resultados de README: no se permite inferir 404")

    output: list[HashPreview] = []
    for repo in result.repositories:
        identifier = repo["github_id"]
        content = readmes.get(identifier)
        output.append(HashPreview(
            github_id=identifier,
            full_name=repo["full_name"],
            content_hash=content_hash_v1(repo, content),
            content_hash_version=HASH_VERSION,
            readme_state="DISPONIBLE" if identifier in readmes else "NO_ENCONTRADO",
        ))
    return output


def main() -> int:
    print("MODO SEGURO: módulo de hashing v1 disponible; 0 HTTP, 0 conexiones SQL, 0 escrituras.")
    print("Importa content_hash_v1 o preview_transformation_hashes desde Python para calcular hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
