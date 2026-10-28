"""OpenBridge — planificación pura de la sincronización incremental.

Este módulo no hace I/O: recibe la transformación (``TransformationResult``) y
el estado leído del catálogo, y devuelve un plan explícito de inserciones,
actualizaciones, registros sin cambios y registros preservados.

Reglas de seguridad:

* Solo se planifican escrituras para hashes ``openbridge-ai-v1`` verificables.
* Los hashes históricos sin versión (o de otra versión) se preservan y se
  informan para una migración separada; nunca se recalculan aquí.
* Un README ausente confirmado por HTTP 404 se distingue de un fallo
  transitorio (red, cuota, contenido inválido): los fallos transitorios no
  producen escrituras y nunca se interpretan como 404.
* No existe acción de borrado.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Any
import unicodedata

from hash_contract import (
    HASH_VERSION,
    ContentHashError,
    content_hash_v1,
)
from transform import TransformationResult

REPO_INSERT = "INSERT"
REPO_UPDATE = "UPDATE"
REPO_UNCHANGED = "UNCHANGED"
REPO_PRESERVE = "PRESERVE"

README_INSERT = "INSERT"
README_UPDATE = "UPDATE"
README_UNCHANGED = "UNCHANGED"
README_PRESERVE = "PRESERVE"
README_NONE = "NONE"

REPOSITORY_ACTIONS = frozenset(
    {REPO_INSERT, REPO_UPDATE, REPO_UNCHANGED, REPO_PRESERVE}
)
README_ACTIONS = frozenset(
    {README_INSERT, README_UPDATE, README_UNCHANGED, README_PRESERVE, README_NONE}
)

README_AVAILABLE = "DISPONIBLE"
README_CONFIRMED_404 = "NO_ENCONTRADO"
README_UNRESOLVED = "NO_VERIFICABLE"

_COMPARED_SCALARS = (
    "name",
    "description",
    "homepage",
    "language",
    "stargazers_count",
    "forks_count",
    "pushed_at",
    "archived",
    "license_spdx_id",
)
_COUNT_FIELDS = frozenset({"stargazers_count", "forks_count"})


class SyncPlanError(ValueError):
    """Datos, catálogo o plan incompatibles con una sincronización segura."""


@dataclass(frozen=True)
class StoredRepository:
    """Fila actual del catálogo (solo lectura) usada para comparar."""

    github_id: int
    full_name: str
    content_hash: str | None = None
    content_hash_version: str | None = None
    has_readme_row: bool = False
    readme_text: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CatalogState:
    """Estado completo del catálogo consultado en modo solo lectura."""

    repositories: Mapping[int, StoredRepository]

    @classmethod
    def empty(cls) -> "CatalogState":
        return cls({})


@dataclass(frozen=True)
class SyncAction:
    """Decisión por repositorio, sin SQL y sin efectos secundarios."""

    github_id: int
    full_name: str
    repository_action: str
    readme_action: str
    reasons: tuple[str, ...]
    repository: Mapping[str, Any]
    readme_text: str | None
    content_hash: str | None
    content_hash_version: str | None
    previous_content_hash: str | None = None
    previous_content_hash_version: str | None = None

    @property
    def writes_repository(self) -> bool:
        return self.repository_action in {REPO_INSERT, REPO_UPDATE}

    @property
    def writes_readme(self) -> bool:
        return self.readme_action in {README_INSERT, README_UPDATE}

    @property
    def writes_anything(self) -> bool:
        return self.writes_repository or self.writes_readme


@dataclass(frozen=True)
class SyncPlan:
    """Plan validable e idempotente. No contiene sentencias SQL."""

    actions: tuple[SyncAction, ...]
    warnings: tuple[str, ...] = ()
    legacy_hash_ids: tuple[int, ...] = ()
    inconsistent_hash_ids: tuple[int, ...] = ()
    unresolved_readme: tuple[str, ...] = ()
    missing_repositories: tuple[str, ...] = ()
    approved_total: int = 0
    hash_version: str = HASH_VERSION

    def _count(self, attribute: str, value: str) -> int:
        return sum(1 for action in self.actions if getattr(action, attribute) == value)

    @property
    def inserted_repositories(self) -> int:
        return self._count("repository_action", REPO_INSERT)

    @property
    def updated_repositories(self) -> int:
        return self._count("repository_action", REPO_UPDATE)

    @property
    def unchanged_repositories(self) -> int:
        return self._count("repository_action", REPO_UNCHANGED)

    @property
    def preserved_repositories(self) -> int:
        return self._count("repository_action", REPO_PRESERVE)

    @property
    def inserted_readmes(self) -> int:
        return self._count("readme_action", README_INSERT)

    @property
    def updated_readmes(self) -> int:
        return self._count("readme_action", README_UPDATE)

    @property
    def unchanged_readmes(self) -> int:
        return self._count("readme_action", README_UNCHANGED)

    @property
    def preserved_readmes(self) -> int:
        return self._count("readme_action", README_PRESERVE)

    @property
    def writes(self) -> int:
        return sum(1 for action in self.actions if action.writes_anything)

    @property
    def incomplete(self) -> bool:
        return bool(self.missing_repositories) or bool(self.unresolved_readme)

    @property
    def has_writes(self) -> bool:
        return self.writes > 0


def _validate_approved(approved: Sequence[str]) -> frozenset[str]:
    if isinstance(approved, (str, bytes)) or not approved:
        raise SyncPlanError("Se requiere una lista aprobada no vacía")
    seen: set[str] = set()
    for name in approved:
        if not isinstance(name, str):
            raise SyncPlanError("La lista aprobada contiene entradas no textuales")
        parts = name.split("/")
        if len(parts) != 2 or any(not part for part in parts):
            raise SyncPlanError("Identificador aprobado inválido en la lista")
        key = name.casefold()
        if key in seen:
            raise SyncPlanError("Repositorio duplicado en la lista aprobada")
        seen.add(key)
    return frozenset(seen)


def _validate_state(state: CatalogState) -> None:
    if not isinstance(state, CatalogState):
        raise SyncPlanError("Estado del catálogo no válido")
    for key, row in state.repositories.items():
        if type(key) is not int or key <= 0:
            raise SyncPlanError("Clave de catálogo no válida")
        if not isinstance(row, StoredRepository):
            raise SyncPlanError("Fila de catálogo no válida")
        if row.github_id != key:
            raise SyncPlanError("Clave y github_id discrepan en el estado del catálogo")
        if not isinstance(row.full_name, str) or "/" not in row.full_name:
            raise SyncPlanError("full_name inválido en el estado del catálogo")
        if row.readme_text is not None and not isinstance(row.readme_text, str):
            raise SyncPlanError("readme_text inválido en el estado del catálogo")
        if row.has_readme_row is False and row.readme_text is not None:
            raise SyncPlanError("Fila README inconsistente en el estado del catálogo")
        if row.content_hash is not None and not isinstance(row.content_hash, str):
            raise SyncPlanError("content_hash inválido en el estado del catálogo")


def _text_nfc(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    normalized = unicodedata.normalize("NFC", value)
    return normalized if normalized.strip() else None


def _normalize_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def _as_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_pg_array(text: str) -> list[str]:
    """Interpreta el literal de arreglo de PostgreSQL usado en ``topics``."""
    if not (text.startswith("{") and text.endswith("}")):
        raise ValueError("formato de arreglo no reconocido")
    inner = text[1:-1]
    if not inner.strip():
        return []
    items: list[str] = []
    buffer: list[str] = []
    quoted = False
    in_quotes = False
    escaped = False

    def flush() -> None:
        raw = "".join(buffer)
        buffer.clear()
        if not quoted and raw.strip().upper() == "NULL":
            return
        if not quoted and not raw.strip():
            return
        items.append(raw)

    for char in inner:
        if escaped:
            buffer.append(char)
            escaped = False
            continue
        if in_quotes and char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            quoted = True
            continue
        if char == "," and not in_quotes:
            flush()
            quoted = False
            continue
        buffer.append(char)
    if in_quotes:
        raise ValueError("arreglo entrecomillado sin cierre")
    flush()
    return items


def parse_stored_topics(value: Any) -> list[str]:
    """Normaliza ``topics`` almacenados (arreglo PG o JSON) para comparar.

    Lanza ``ValueError`` si el formato es desconocido: el plan lo trata como
    dato no verificable y no sobrescribe la fila.
    """
    if value is None:
        return []
    if not isinstance(value, str):
        raise ValueError("topics almacenados no son texto")
    text = value.strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("topics JSON inválido") from exc
        if not isinstance(parsed, list):
            raise ValueError("topics JSON no es una lista")
        if any(not isinstance(item, str) for item in parsed):
            raise ValueError("topics JSON contiene valores no textuales")
        return [item.casefold() for item in parsed]
    if text.startswith("{"):
        return [item.casefold() for item in _parse_pg_array(text)]
    raise ValueError("formato de topics desconocido")


def _metadata_changes(
    stored: StoredRepository, repository: Mapping[str, Any]
) -> tuple[bool, bool]:
    """Devuelve (¿cambió algún campo?, ¿topics almacenados no verificables?)."""
    changed = False
    for name in _COMPARED_SCALARS:
        if name == "pushed_at":
            left = _normalize_timestamp(stored.metadata.get(name))
            right = _normalize_timestamp(repository.get(name))
        elif name in _COUNT_FIELDS:
            left = _as_int(stored.metadata.get(name))
            right = _as_int(repository.get(name))
        elif name == "name":
            left = (_text_nfc(stored.metadata.get(name)) or "").casefold()
            right = (_text_nfc(repository.get(name)) or "").casefold()
        else:
            left = _text_nfc(stored.metadata.get(name))
            right = _text_nfc(repository.get(name))
        if left != right:
            changed = True
    try:
        stored_topics = parse_stored_topics(stored.metadata.get("topics"))
    except ValueError:
        return changed, True
    new_topics = repository.get("topics") or ()
    normalized_new = sorted(str(item).casefold() for item in new_topics)
    if sorted(stored_topics) != normalized_new:
        changed = True
    return changed, False


def _compute_hash(repository: Mapping[str, Any], readme_text: str | None) -> str:
    try:
        return content_hash_v1(repository, readme_text)
    except ContentHashError as exc:
        raise SyncPlanError(
            f"Hash no calculable para {repository.get('full_name')}: {exc}"
        ) from exc


def _action(
    *,
    github_id: int,
    full_name: str,
    repository_action: str,
    readme_action: str,
    reasons: tuple[str, ...],
    repository: Mapping[str, Any],
    readme_text: str | None,
    content_hash: str | None = None,
    content_hash_version: str | None = None,
    previous_content_hash: str | None = None,
    previous_content_hash_version: str | None = None,
) -> SyncAction:
    if repository_action not in REPOSITORY_ACTIONS:
        raise SyncPlanError("Acción de repositorio no permitida")
    if readme_action not in README_ACTIONS:
        raise SyncPlanError("Acción de README no permitida")
    return SyncAction(
        github_id=github_id,
        full_name=full_name,
        repository_action=repository_action,
        readme_action=readme_action,
        reasons=tuple(reasons),
        repository=dict(repository),
        readme_text=readme_text,
        content_hash=content_hash,
        content_hash_version=content_hash_version,
        previous_content_hash=previous_content_hash,
        previous_content_hash_version=previous_content_hash_version,
    )


def _index_transformation(
    result: TransformationResult, approved_keys: frozenset[str]
) -> tuple[
    dict[int, Mapping[str, Any]],
    dict[int, str],
    dict[int, str],
]:
    repositories: dict[int, Mapping[str, Any]] = {}
    names: dict[str, int] = {}
    for repository in result.repositories:
        identifier = repository.get("github_id")
        full_name = repository.get("full_name")
        if type(identifier) is not int or identifier <= 0:
            raise SyncPlanError("github_id inválido en la transformación")
        if not isinstance(full_name, str) or "/" not in full_name:
            raise SyncPlanError("full_name inválido en la transformación")
        if identifier in repositories:
            raise SyncPlanError(f"github_id duplicado en la transformación: {identifier}")
        key = full_name.casefold()
        if key in names:
            raise SyncPlanError(f"full_name duplicado en la transformación: {full_name}")
        if key not in approved_keys:
            raise SyncPlanError(f"Repositorio fuera de la lista aprobada: {full_name}")
        repositories[identifier] = repository
        names[key] = identifier

    readmes: dict[int, str] = {}
    for item in result.readmes:
        identifier = item.get("github_id")
        text = item.get("readme_text")
        if type(identifier) is not int or identifier not in repositories:
            raise SyncPlanError("README sin repositorio correspondiente")
        if identifier in readmes:
            raise SyncPlanError("README duplicado en la transformación")
        if not isinstance(text, str):
            raise SyncPlanError("readme_text inválido en la transformación")
        readmes[identifier] = text

    statuses: dict[int, str] = {}
    for observation in result.observations:
        full_name = observation.get("full_name")
        if not isinstance(full_name, str):
            raise SyncPlanError("Observación sin full_name válido")
        identifier = names.get(full_name.casefold())
        if identifier is None:
            raise SyncPlanError(f"Observación sin repositorio: {full_name}")
        if identifier in statuses:
            raise SyncPlanError(f"Observación README duplicada: {full_name}")
        status = observation.get("readme_status")
        if not isinstance(status, str) or not status:
            raise SyncPlanError(f"readme_status inválido: {full_name}")
        statuses[identifier] = status

    for identifier in repositories:
        has_readme = identifier in readmes
        has_status = identifier in statuses
        if has_readme and has_status:
            raise SyncPlanError("Estado README ambiguo: contenido y observación")
        if not has_readme and not has_status:
            raise SyncPlanError("Falta el estado README de un repositorio")
    return repositories, readmes, statuses


def build_sync_plan(
    result: TransformationResult,
    state: CatalogState,
    *,
    approved: Sequence[str],
    expected_hash_version: str = HASH_VERSION,
) -> SyncPlan:
    """Compara la transformación con el catálogo y decide qué escribir.

    No abre conexiones ni escribe nada. Los fallos transitorios de README se
    preservan (nunca se escriben ni se interpretan como 404).
    """
    if not isinstance(result, TransformationResult):
        raise SyncPlanError("Se requiere un TransformationResult")
    if expected_hash_version != HASH_VERSION:
        raise SyncPlanError("Versión de hash no soportada en este coordinador")
    _validate_state(state)
    approved_keys = _validate_approved(approved)
    repositories, readmes, statuses = _index_transformation(result, approved_keys)

    actions: list[SyncAction] = []
    warnings: list[str] = []
    legacy_ids: list[int] = []
    inconsistent_ids: list[int] = []
    unresolved: list[str] = []

    for identifier in sorted(repositories):
        repository = repositories[identifier]
        full_name = str(repository["full_name"])
        text = readmes.get(identifier)
        status = statuses.get(identifier, README_AVAILABLE)
        if text is not None:
            readme_state = README_AVAILABLE
        elif status == README_CONFIRMED_404:
            readme_state = README_CONFIRMED_404
        else:
            readme_state = README_UNRESOLVED

        stored = state.repositories.get(identifier)
        if stored is None:
            if readme_state == README_UNRESOLVED:
                unresolved.append(full_name)
                warnings.append(
                    f"{full_name}: README no verificable ({status}); "
                    "no se inserta un registro parcial"
                )
                actions.append(_action(
                    github_id=identifier,
                    full_name=full_name,
                    repository_action=REPO_PRESERVE,
                    readme_action=README_PRESERVE,
                    reasons=("readme_unresolved", status),
                    repository=repository,
                    readme_text=None,
                ))
                continue
            content_hash = _compute_hash(repository, text)
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_INSERT,
                readme_action=(
                    README_INSERT if readme_state == README_AVAILABLE else README_NONE
                ),
                reasons=("new_repository",),
                repository=repository,
                readme_text=text,
                content_hash=content_hash,
                content_hash_version=HASH_VERSION,
            ))
            continue

        if full_name.casefold() != stored.full_name.casefold():
            warnings.append(
                f"{full_name}: conflicto de identidad con {stored.full_name}; "
                "se preserva la fila existente"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=("identity_conflict",),
                repository=repository,
                readme_text=None,
            ))
            continue

        if stored.content_hash_version != HASH_VERSION:
            legacy_ids.append(identifier)
            reason = (
                "hash_version_missing"
                if stored.content_hash_version is None
                else f"hash_version_unsupported:{stored.content_hash_version}"
            )
            warnings.append(
                f"{full_name}: hash sin versión {HASH_VERSION}; "
                "se preserva para una migración separada"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=(reason,),
                repository=repository,
                readme_text=None,
            ))
            continue

        if readme_state == README_UNRESOLVED:
            unresolved.append(full_name)
            warnings.append(
                f"{full_name}: README no verificable ({status}); "
                "se preservan los datos existentes"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=("readme_unresolved", status),
                repository=repository,
                readme_text=None,
            ))
            continue

        if stored.has_readme_row and readme_state == README_CONFIRMED_404:
            warnings.append(
                f"{full_name}: 404 confirmado pero existe README almacenado; "
                "no se elimina (política de borrado pendiente)"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=("stored_readme_missing_upstream",),
                repository=repository,
                readme_text=None,
            ))
            continue

        content_hash = _compute_hash(repository, text)
        metadata_changed, topics_unverifiable = _metadata_changes(stored, repository)
        readme_changed = readme_state == README_AVAILABLE and stored.readme_text != text
        readme_row_missing = readme_state == README_AVAILABLE and not stored.has_readme_row

        if content_hash == stored.content_hash:
            if readme_changed:
                warnings.append(
                    f"{full_name}: el hash coincide pero el README almacenado difiere; "
                    "se repara solo el README"
                )
                actions.append(_action(
                    github_id=identifier,
                    full_name=full_name,
                    repository_action=REPO_UNCHANGED,
                    readme_action=README_UPDATE,
                    reasons=("readme_desync",),
                    repository=repository,
                    readme_text=text,
                    content_hash=content_hash,
                    content_hash_version=HASH_VERSION,
                    previous_content_hash=stored.content_hash,
                    previous_content_hash_version=stored.content_hash_version,
                ))
            else:
                actions.append(_action(
                    github_id=identifier,
                    full_name=full_name,
                    repository_action=REPO_UNCHANGED,
                    readme_action=(
                        README_UNCHANGED if stored.has_readme_row else README_NONE
                    ),
                    reasons=("unchanged",),
                    repository=repository,
                    readme_text=text,
                    content_hash=content_hash,
                    content_hash_version=HASH_VERSION,
                    previous_content_hash=stored.content_hash,
                    previous_content_hash_version=stored.content_hash_version,
                ))
            continue

        if stored.content_hash is None:
            inconsistent_ids.append(identifier)
            warnings.append(
                f"{full_name}: versión v1 sin content_hash almacenado; se preserva"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=("hash_inconsistent",),
                repository=repository,
                readme_text=None,
            ))
            continue

        if (
            not metadata_changed
            and not readme_changed
            and not readme_row_missing
            and not topics_unverifiable
        ):
            inconsistent_ids.append(identifier)
            warnings.append(
                f"{full_name}: el hash almacenado no corresponde a sus propios datos; "
                "se preserva y requiere revisión"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=("hash_inconsistent",),
                repository=repository,
                readme_text=None,
            ))
            continue

        if (
            topics_unverifiable
            and not metadata_changed
            and not readme_changed
            and not readme_row_missing
        ):
            warnings.append(
                f"{full_name}: topics almacenados no verificables; se preserva"
            )
            actions.append(_action(
                github_id=identifier,
                full_name=full_name,
                repository_action=REPO_PRESERVE,
                readme_action=README_PRESERVE,
                reasons=("stored_topics_unverifiable",),
                repository=repository,
                readme_text=None,
            ))
            continue

        reasons: list[str] = []
        if metadata_changed or topics_unverifiable:
            reasons.append("metadata_changed")
        if readme_changed or readme_row_missing:
            reasons.append("readme_changed")
        if readme_row_missing:
            readme_action = README_INSERT
        elif readme_changed:
            readme_action = README_UPDATE
        elif stored.has_readme_row:
            readme_action = README_UNCHANGED
        else:
            readme_action = README_NONE
        actions.append(_action(
            github_id=identifier,
            full_name=full_name,
            repository_action=REPO_UPDATE,
            readme_action=readme_action,
            reasons=tuple(reasons),
            repository=repository,
            readme_text=text,
            content_hash=content_hash,
            content_hash_version=HASH_VERSION,
            previous_content_hash=stored.content_hash,
            previous_content_hash_version=stored.content_hash_version,
        ))

    approved_names = tuple(approved)
    extracted_keys = {
        str(repository["full_name"]).casefold()
        for repository in repositories.values()
    }
    missing = tuple(
        name for name in approved_names if name.casefold() not in extracted_keys
    )
    if missing:
        warnings.append(
            "Extracción incompleta: faltan repositorios aprobados y la "
            "sincronización no se considera completa"
        )
    return SyncPlan(
        actions=tuple(actions),
        warnings=tuple(warnings),
        legacy_hash_ids=tuple(legacy_ids),
        inconsistent_hash_ids=tuple(inconsistent_ids),
        unresolved_readme=tuple(unresolved),
        missing_repositories=missing,
        approved_total=len(approved_names),
        hash_version=HASH_VERSION,
    )


_HEX = frozenset("0123456789abcdef")


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX


def validate_plan(plan: SyncPlan) -> None:
    """Verifica el plan completo antes de abrir cualquier conexión de escritura.

    Recalcula cada hash ``openbridge-ai-v1`` a partir de los datos que se van a
    escribir: un plan manipulado o construido con datos distintos se rechaza.
    """
    if not isinstance(plan, SyncPlan):
        raise SyncPlanError("Plan no válido")
    if plan.hash_version != HASH_VERSION:
        raise SyncPlanError("El plan no usa la versión de hash soportada")
    if type(plan.approved_total) is not int or plan.approved_total < 0:
        raise SyncPlanError("approved_total inválido en el plan")

    seen_ids: set[int] = set()
    seen_names: set[str] = set()
    for action in plan.actions:
        if not isinstance(action, SyncAction):
            raise SyncPlanError("El plan contiene una acción no válida")
        if type(action.github_id) is not int or action.github_id <= 0:
            raise SyncPlanError("github_id inválido en el plan")
        if action.github_id in seen_ids:
            raise SyncPlanError(f"github_id duplicado en el plan: {action.github_id}")
        if not isinstance(action.full_name, str) or "/" not in action.full_name:
            raise SyncPlanError("full_name inválido en el plan")
        if action.repository_action not in REPOSITORY_ACTIONS:
            raise SyncPlanError("Acción de repositorio desconocida")
        if action.readme_action not in README_ACTIONS:
            raise SyncPlanError("Acción de README desconocida")
        if not isinstance(action.repository, Mapping):
            raise SyncPlanError("Datos de repositorio no válidos en el plan")
        if action.repository.get("github_id") != action.github_id:
            raise SyncPlanError("La acción no corresponde a su github_id")
        expected_name = action.repository.get("full_name")
        if not isinstance(expected_name, str) or expected_name.casefold() != action.full_name.casefold():
            raise SyncPlanError("La acción no corresponde a su full_name")
        key = action.full_name.casefold()
        if key in seen_names:
            raise SyncPlanError(f"full_name duplicado en el plan: {action.full_name}")
        seen_ids.add(action.github_id)
        seen_names.add(key)

        if action.readme_action in {README_INSERT, README_UPDATE}:
            if not isinstance(action.readme_text, str) or not action.readme_text:
                raise SyncPlanError("Se intenta escribir un README vacío")
        if action.repository_action == REPO_INSERT:
            if action.readme_action in {README_UNCHANGED, README_UPDATE}:
                raise SyncPlanError("Inserción con README preexistente: plan inválido")
            if action.previous_content_hash is not None:
                raise SyncPlanError("Una inserción no puede declarar hash previo")
            if action.previous_content_hash_version is not None:
                raise SyncPlanError("Una inserción no puede declarar versión previa")
        if action.repository_action == REPO_PRESERVE:
            if action.content_hash is not None:
                raise SyncPlanError("Una acción preservada no puede declarar hash nuevo")
            if action.writes_anything:
                raise SyncPlanError("Una acción preservada no puede escribir")

        if action.content_hash is not None:
            if action.content_hash_version != HASH_VERSION:
                raise SyncPlanError("Hash sin versión compatible en el plan")
            if not _is_sha256(action.content_hash):
                raise SyncPlanError("content_hash no es un SHA-256 hexadecimal")
            expected = _compute_hash(action.repository, action.readme_text)
            if expected != action.content_hash:
                raise SyncPlanError(
                    f"Hash inconsistente en el plan para {action.full_name}"
                )
        elif action.writes_repository:
            raise SyncPlanError(
                f"Escritura sin hash verificable para {action.full_name}"
            )
