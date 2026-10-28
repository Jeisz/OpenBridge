"""OpenBridge — persistencia incremental del catálogo (aplicación de planes).

Complementa ``load.py`` (carga inicial insert-only) con la aplicación de un
``SyncPlan`` ya validado:

* lectura del estado en transacción de solo lectura;
* aplicación transaccional de INSERT/UPDATE con control optimista de versión;
* verificación posterior de hashes y READMEs.

No ejecuta DDL y no contiene ninguna sentencia DELETE. La API de escritura
exige confirmación explícita y un destino habilitado para escritura.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import time
from typing import Any

from sqlalchemy import ARRAY, Text, bindparam, text

from hash_contract import HASH_VERSION
from load import LoadPlanError
from sync_config import (
    DatabaseTarget,
    SyncConfigError,
    is_admin_user,
)
from sync_plan import (
    README_INSERT,
    README_UPDATE,
    REPO_INSERT,
    REPO_UPDATE,
    CatalogState,
    StoredRepository,
    SyncPlan,
    validate_plan,
)

SYNC_WRITE_CONFIRMATION = "CONFIRMO_SINCRONIZACION_INCREMENTAL_OPENBRIDGE_V1"

CURRENT_DATABASE_SQL = "SELECT current_database()"
CURRENT_USER_SQL = "SELECT current_user"
HASH_VERSION_COLUMN_SQL = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'catalog_repositories'
      AND column_name = 'content_hash_version'
"""

READ_STATE_SQL = """
    SELECT
        r.github_id, r.full_name, r.name, r.description, r.homepage,
        r.language, r.topics, r.stargazers_count, r.forks_count, r.pushed_at,
        r.archived, r.license_spdx_id, r.content_hash, r.content_hash_version,
        m.github_id AS readme_github_id, m.readme_text
    FROM public.catalog_repositories AS r
    LEFT JOIN public.catalog_readmes AS m ON m.github_id = r.github_id
    ORDER BY r.github_id
"""

LOCK_STATE_SQL = (
    "SELECT github_id FROM public.catalog_repositories "
    "ORDER BY github_id FOR UPDATE"
)

INSERT_REPOSITORY_SQL = """
    INSERT INTO public.catalog_repositories (
        github_id, full_name, name, description, homepage, language,
        topics, stargazers_count, forks_count, pushed_at,
        archived, license_spdx_id, content_hash, content_hash_version
    ) VALUES (
        :github_id, :full_name, :name, :description, :homepage, :language,
        CAST(:topics AS TEXT[])::TEXT, :stargazers_count,
        :forks_count, :pushed_at, :archived, :license_spdx_id,
        :content_hash, :content_hash_version
    ) ON CONFLICT (github_id) DO NOTHING RETURNING github_id
"""

UPDATE_REPOSITORY_SQL = """
    UPDATE public.catalog_repositories
    SET full_name = :full_name, name = :name, description = :description,
        homepage = :homepage, language = :language,
        topics = CAST(:topics AS TEXT[])::TEXT,
        stargazers_count = :stargazers_count, forks_count = :forks_count,
        pushed_at = :pushed_at, archived = :archived,
        license_spdx_id = :license_spdx_id,
        content_hash = :content_hash,
        content_hash_version = :content_hash_version
    WHERE github_id = :github_id
      AND content_hash IS NOT DISTINCT FROM :previous_content_hash
      AND content_hash_version IS NOT DISTINCT FROM :previous_content_hash_version
"""

UPSERT_README_SQL = """
    INSERT INTO public.catalog_readmes AS objetivo
        (github_id, readme_text, updated_at)
    VALUES (:github_id, :readme_text, CURRENT_TIMESTAMP)
    ON CONFLICT (github_id) DO UPDATE
    SET readme_text = EXCLUDED.readme_text,
        updated_at = CURRENT_TIMESTAMP
    WHERE objetivo.readme_text IS DISTINCT FROM EXCLUDED.readme_text
"""


@dataclass(frozen=True)
class SyncSummary:
    """Resultado de una aplicación real del plan."""

    inserted_repositories: int
    updated_repositories: int
    inserted_readmes: int
    updated_readmes: int
    unchanged_repositories: int
    preserved_repositories: int
    elapsed_seconds: float

    def to_line(self) -> str:
        return (
            "INSERT repositorios={i} | UPDATE repositorios={u} | "
            "INSERT READMEs={ri} | UPDATE READMEs={ru} | "
            "sin cambios={n} | preservados={p} | {s:.3f}s"
        ).format(
            i=self.inserted_repositories,
            u=self.updated_repositories,
            ri=self.inserted_readmes,
            ru=self.updated_readmes,
            n=self.unchanged_repositories,
            p=self.preserved_repositories,
            s=self.elapsed_seconds,
        )


_METADATA_KEYS = (
    "name",
    "description",
    "homepage",
    "language",
    "topics",
    "stargazers_count",
    "forks_count",
    "pushed_at",
    "archived",
    "license_spdx_id",
)
_WRITE_KEYS = (
    "github_id",
    "full_name",
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


def _state_from_rows(rows: Iterable[Mapping[str, Any]]) -> CatalogState:
    repositories: dict[int, StoredRepository] = {}
    for row in rows:
        identifier = row.get("github_id")
        if type(identifier) is not int or identifier <= 0:
            raise LoadPlanError("github_id inválido al leer el catálogo")
        if identifier in repositories:
            raise LoadPlanError("github_id duplicado al leer el catálogo")
        full_name = row.get("full_name")
        if not isinstance(full_name, str) or "/" not in full_name:
            raise LoadPlanError("full_name inválido al leer el catálogo")
        readme_identifier = row.get("readme_github_id")
        readme_text = row.get("readme_text")
        has_readme = readme_identifier is not None
        if has_readme and readme_identifier != identifier:
            raise LoadPlanError("README huérfano detectado en el catálogo")
        if has_readme and readme_text is not None and not isinstance(readme_text, str):
            raise LoadPlanError("readme_text inválido al leer el catálogo")
        if not has_readme and readme_text is not None:
            raise LoadPlanError("readme_text sin fila README asociada")
        repositories[identifier] = StoredRepository(
            github_id=identifier,
            full_name=full_name,
            content_hash=row.get("content_hash"),
            content_hash_version=row.get("content_hash_version"),
            has_readme_row=has_readme,
            readme_text=readme_text,
            metadata={key: row.get(key) for key in _METADATA_KEYS},
        )
    return CatalogState(repositories=repositories)


def read_catalog_state(engine) -> CatalogState:
    """Lee el catálogo en una transacción explícitamente de solo lectura."""
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            rows = connection.execute(text(READ_STATE_SQL)).mappings().all()
    return _state_from_rows(rows)


def _repository_values(action, *, include_previous: bool) -> dict[str, Any]:
    values: dict[str, Any] = {
        key: action.repository.get(key) for key in _WRITE_KEYS
    }
    values["topics"] = sorted(
        str(item) for item in (action.repository.get("topics") or ())
    )
    values["content_hash"] = action.content_hash
    values["content_hash_version"] = HASH_VERSION
    if include_previous:
        values["previous_content_hash"] = action.previous_content_hash
        values["previous_content_hash_version"] = (
            action.previous_content_hash_version
        )
    return values


def apply_sync_plan(
    engine,
    plan: SyncPlan,
    *,
    target: DatabaseTarget,
    authorization: str,
) -> SyncSummary:
    """Aplica el plan en una única transacción con control optimista.

    No se abre conexión si la autorización, el destino o el plan no son
    válidos. Cualquier discrepancia revierte toda la transacción.
    """
    if authorization != SYNC_WRITE_CONFIRMATION:
        raise PermissionError(
            "Escritura bloqueada: falta la confirmación explícita de sincronización"
        )
    if not isinstance(target, DatabaseTarget):
        raise SyncConfigError("Destino no validado; escritura bloqueada")
    if not target.writes_allowed:
        raise PermissionError(
            "Escritura bloqueada: el destino no está habilitado "
            "(OPENBRIDGE_SYNC_ALLOW_WRITES=1 requerido)"
        )
    if is_admin_user(target.user):
        raise PermissionError(
            "Escritura bloqueada: no se admite una cuenta administrativa"
        )
    if not isinstance(plan, SyncPlan):
        raise LoadPlanError("Plan no válido")
    validate_plan(plan)

    unchanged = plan.unchanged_repositories
    preserved = plan.preserved_repositories
    if not plan.has_writes:
        return SyncSummary(0, 0, 0, 0, unchanged, preserved, 0.0)

    started = time.monotonic()
    inserted_repositories = 0
    updated_repositories = 0
    inserted_readmes = 0
    updated_readmes = 0

    with engine.begin() as connection:
        database = connection.execute(text(CURRENT_DATABASE_SQL)).scalar_one()
        if database != target.database:
            raise LoadPlanError(
                "Base de datos inesperada: se bloquea la escritura y se revierte"
            )
        user = connection.execute(text(CURRENT_USER_SQL)).scalar_one()
        if user != target.user or is_admin_user(str(user)):
            raise LoadPlanError(
                "Usuario de conexión no autorizado: se bloquea la escritura"
            )
        columns = {
            str(row[0])
            for row in connection.execute(text(HASH_VERSION_COLUMN_SQL))
        }
        if "content_hash_version" not in columns:
            raise LoadPlanError(
                "Falta la columna content_hash_version; escritura revertida"
            )

        connection.execute(text(LOCK_STATE_SQL))
        current = _state_from_rows(
            connection.execute(text(READ_STATE_SQL)).mappings().all()
        )

        for action in plan.actions:
            if not action.writes_anything:
                continue
            stored = current.repositories.get(action.github_id)

            if action.repository_action == REPO_INSERT:
                if stored is not None:
                    raise LoadPlanError(
                        f"{action.full_name} apareció tras planificar; se revierte todo"
                    )
                values = _repository_values(action, include_previous=False)
                created = connection.execute(
                    text(INSERT_REPOSITORY_SQL).bindparams(
                        bindparam("topics", type_=ARRAY(Text()))
                    ),
                    values,
                ).scalar_one_or_none()
                if created is None:
                    raise LoadPlanError(
                        "Colisión concurrente al insertar; se revierte todo"
                    )
                inserted_repositories += 1

            elif action.repository_action == REPO_UPDATE:
                if stored is None:
                    raise LoadPlanError(
                        f"{action.full_name} desapareció del catálogo; se revierte"
                    )
                if (
                    stored.content_hash != action.previous_content_hash
                    or stored.content_hash_version
                    != action.previous_content_hash_version
                ):
                    raise LoadPlanError(
                        f"Plan obsoleto para {action.full_name}: "
                        "el catálogo cambió; se revierte todo"
                    )
                values = _repository_values(action, include_previous=True)
                result = connection.execute(
                    text(UPDATE_REPOSITORY_SQL).bindparams(
                        bindparam("topics", type_=ARRAY(Text()))
                    ),
                    values,
                )
                if getattr(result, "rowcount", None) != 1:
                    raise LoadPlanError(
                        f"Actualización sin efecto para {action.full_name}: "
                        "se revierte todo"
                    )
                updated_repositories += 1

            if action.readme_action in {README_INSERT, README_UPDATE}:
                result = connection.execute(
                    text(UPSERT_README_SQL),
                    {
                        "github_id": action.github_id,
                        "readme_text": action.readme_text,
                    },
                )
                if getattr(result, "rowcount", None) != 1:
                    raise LoadPlanError(
                        f"README sin cambio real para {action.full_name}: "
                        "se revierte para evitar un plan obsoleto"
                    )
                if action.readme_action == README_INSERT:
                    inserted_readmes += 1
                else:
                    updated_readmes += 1

    return SyncSummary(
        inserted_repositories=inserted_repositories,
        updated_repositories=updated_repositories,
        inserted_readmes=inserted_readmes,
        updated_readmes=updated_readmes,
        unchanged_repositories=unchanged,
        preserved_repositories=preserved,
        elapsed_seconds=time.monotonic() - started,
    )


def verify_sync_result(engine, plan: SyncPlan) -> tuple[str, ...]:
    """Relee el catálogo y devuelve las discrepancias respecto al plan."""
    state = read_catalog_state(engine)
    problems: list[str] = []
    for action in plan.actions:
        if not action.writes_anything:
            continue
        stored = state.repositories.get(action.github_id)
        if stored is None:
            problems.append(
                f"{action.full_name}: ausente tras la sincronización"
            )
            continue
        if action.writes_repository:
            if stored.content_hash != action.content_hash:
                problems.append(
                    f"{action.full_name}: content_hash no coincide con el plan"
                )
            if stored.content_hash_version != HASH_VERSION:
                problems.append(
                    f"{action.full_name}: versión de hash distinta de {HASH_VERSION}"
                )
        if action.readme_action in {README_INSERT, README_UPDATE}:
            if not stored.has_readme_row:
                problems.append(f"{action.full_name}: README no persistido")
            elif stored.readme_text != action.readme_text:
                problems.append(
                    f"{action.full_name}: README distinto al planificado"
                )
    return tuple(problems)
