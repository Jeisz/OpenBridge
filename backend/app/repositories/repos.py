"""Consultas de solo lectura al catálogo y a los resultados de IA.

Fuentes (acuerdo del 29-oct-2026):
- `public.catalog_repositories`: catálogo original (lectura).
- `public.v_repos_for_ai`: vista de lectura que publica el equipo de datos.
- `ai.*`: resultados de IA, opcionales por repositorio.

La vista todavía no expone `disabled` ni `open_issues_count`, por eso el
listado lee esas dos columnas de la tabla base. Cuando la vista las incluya,
basta con cambiar el SELECT. No se escribe nada y no hay migraciones.
"""
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

MAINTENANCE_ACTIVE = "active"
MAINTENANCE_INACTIVE = "inactive"

_BASE_JOINS = """
    FROM public.catalog_repositories r
    LEFT JOIN ai.ai_repo_enrichment e ON e.github_id = r.github_id
    LEFT JOIN LATERAL (
        SELECT json_agg(
                   json_build_object(
                       'category_id', c.category_id,
                       'assigned_by', c.assigned_by
                   ) ORDER BY c.rank
               ) AS categories
        FROM ai.ai_repo_categories c
        WHERE c.github_id = r.github_id
    ) categories ON TRUE
"""

_LIST_COLUMNS = """
    r.github_id,
    r.full_name,
    r.name,
    r.description,
    r.language,
    r.homepage,
    r.license_spdx_id,
    r.stargazers_count,
    r.forks_count,
    r.pushed_at,
    r.archived,
    r.disabled,
    r.open_issues_count,
    e.summary_es,
    COALESCE(e.use_cases, ARRAY[]::text[]) AS use_cases,
    categories.categories,
    COUNT(*) OVER () AS total_count
"""

_DETAIL_QUERY = """
SELECT
    r.github_id,
    v.full_name,
    v.name,
    v.description,
    v.homepage,
    v.language,
    v.topics,
    v.stargazers_count,
    v.forks_count,
    v.pushed_at,
    v.archived,
    v.license_spdx_id,
    r.open_issues_count,
    r.disabled,
    r.html_url,
    v.readme_text,
    e.summary_es,
    COALESCE(e.use_cases, ARRAY[]::text[]) AS use_cases,
    categories.categories,
    ideas.ideas
FROM public.v_repos_for_ai v
JOIN public.catalog_repositories r ON r.github_id = v.github_id
LEFT JOIN ai.ai_repo_enrichment e ON e.github_id = v.github_id
LEFT JOIN LATERAL (
    SELECT json_agg(
               json_build_object(
                   'category_id', c.category_id,
                   'assigned_by', c.assigned_by
               ) ORDER BY c.rank
           ) AS categories
    FROM ai.ai_repo_categories c
    WHERE c.github_id = v.github_id
) categories ON TRUE
LEFT JOIN LATERAL (
    SELECT json_agg(
               json_build_object(
                   'id', i.id,
                   'title', i.title,
                   'integration_type', i.integration_type,
                   'summary', i.summary,
                   'compatible_stack', i.compatible_stack,
                   'dependencies', i.dependencies,
                   'difficulty', i.difficulty,
                   'triggers', i.triggers,
                   'snippet', i.snippet,
                   'snippet_language', i.snippet_language,
                   'docs_url', i.docs_url,
                   'generated_by', i.generated_by,
                   'reviewed_at', i.reviewed_at,
                   'based_on_hash', i.based_on_hash
               ) ORDER BY i.id
           ) AS ideas
    FROM ai.ai_integration_ideas i
    WHERE i.github_id = v.github_id
) ideas ON TRUE
WHERE lower(v.full_name) = lower(:full_name)
"""


@dataclass(frozen=True)
class RepoFilters:
    """Filtros ya normalizados por el servicio."""

    search: str | None = None
    categories: tuple[str, ...] = ()
    language: str | None = None
    license_spdx_id: str | None = None
    maintenance: str | None = None
    min_stars: int | None = None


@dataclass(frozen=True)
class RepoPage:
    rows: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0


def _like_pattern(value: str) -> str:
    """Patrón ILIKE literal: lo que escribe el usuario se busca como texto."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _where_clause(filters: RepoFilters) -> tuple[list[str], dict[str, Any]]:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if filters.search:
        clauses.append(
            "("
            "r.full_name ILIKE :search ESCAPE '\\' "
            "OR r.name ILIKE :search ESCAPE '\\' "
            "OR COALESCE(r.description, '') ILIKE :search ESCAPE '\\' "
            "OR COALESCE(e.summary_es, '') ILIKE :search ESCAPE '\\'"
            ")"
        )
        params["search"] = _like_pattern(filters.search)

    if filters.categories:
        clauses.append(
            "EXISTS ("
            "SELECT 1 FROM ai.ai_repo_categories fc "
            "WHERE fc.github_id = r.github_id AND fc.category_id = ANY(:categories)"
            ")"
        )
        params["categories"] = list(filters.categories)

    if filters.language:
        clauses.append("lower(r.language) = lower(:language)")
        params["language"] = filters.language

    if filters.license_spdx_id:
        clauses.append("r.license_spdx_id = :license_spdx_id")
        params["license_spdx_id"] = filters.license_spdx_id

    if filters.maintenance == MAINTENANCE_ACTIVE:
        # Aproximación local acordada con Frontend: activo = ni archivado ni deshabilitado.
        clauses.append(
            "(COALESCE(r.archived, FALSE) = FALSE AND COALESCE(r.disabled, FALSE) = FALSE)"
        )
    elif filters.maintenance == MAINTENANCE_INACTIVE:
        clauses.append(
            "(COALESCE(r.archived, FALSE) = TRUE OR COALESCE(r.disabled, FALSE) = TRUE)"
        )

    if filters.min_stars is not None:
        clauses.append("r.stargazers_count >= :min_stars")
        params["min_stars"] = filters.min_stars

    return clauses, params


def build_list_statement(
    filters: RepoFilters, *, limit: int, offset: int
) -> tuple[str, dict[str, Any]]:
    """SQL y parámetros del listado. El orden por full_name es técnico (paginación estable)."""
    clauses, params = _where_clause(filters)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        f"SELECT {_LIST_COLUMNS}{_BASE_JOINS}{where} "
        "ORDER BY r.full_name ASC LIMIT :limit OFFSET :offset"
    )
    params.update({"limit": limit, "offset": offset})
    return sql, params


def build_detail_statement() -> str:
    return _DETAIL_QUERY


class RepoRepository:
    """Acceso a datos del catálogo. No conoce HTTP ni modelos de respuesta."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def list_repos(self, filters: RepoFilters, *, limit: int, offset: int) -> RepoPage:
        sql, params = build_list_statement(filters, limit=limit, offset=offset)
        with self._engine.connect() as connection:
            rows = [
                dict(row) for row in connection.execute(text(sql), params).mappings()
            ]
        total = int(rows[0]["total_count"]) if rows else 0
        for row in rows:
            row.pop("total_count", None)
        return RepoPage(rows=rows, total=total)

    def get_repo(self, full_name: str) -> dict[str, Any] | None:
        with self._engine.connect() as connection:
            row = (
                connection.execute(text(_DETAIL_QUERY), {"full_name": full_name})
                .mappings()
                .first()
            )
        return dict(row) if row is not None else None

