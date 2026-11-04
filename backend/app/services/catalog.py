"""Reglas del catálogo: paginación, filtros y traducción de filas a modelos HTTP.

No hay reglas de negocio inventadas:

- `is_maintained` y `health_score` se devuelven siempre en NULL porque no hay
  campo ni fórmula acordados.
- Ningún NULL se convierte en 0/false. `archived` es obligatorio en el contrato,
  así que una fila sin ese dato se reporta como catálogo no disponible.
- El resumen de IA se recorta a los 250 caracteres del contrato y se registra un
  aviso para el equipo de IA; la alternativa era romper la respuesta entera.
- Las ideas de un repositorio archivado se omiten: el contrato lo prohíbe.
"""
from dataclasses import dataclass
from datetime import datetime
import logging
import re
from math import ceil
from typing import Any, Sequence

from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from backend.app.api.schemas import (
    FULL_NAME_PATTERN,
    MAX_INTEGRATION_IDEAS,
    SUMMARY_ES_MAX_LENGTH,
    CatalogRepo,
    RepoDetailResponse,
)
from backend.app.core.errors import (
    CatalogUnavailableError,
    InvalidRequestError,
    RepoNotFoundError,
)
from backend.app.repositories.repos import RepoFilters, RepoRepository
from shared.contracts.integration_idea import IntegrationIdea

logger = logging.getLogger("openbridge.catalog")

_FULL_NAME_RE = re.compile(FULL_NAME_PATTERN)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _to_datetime(value: Any) -> datetime | None:
    """`pushed_at` viaja como texto ISO; nunca se sustituye por otra fecha."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        logger.warning("pushed_at no interpretable como ISO 8601: %r", value)
        return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    logger.warning("Se esperaba una lista y llegó %s", type(value).__name__)
    return []


def _fit_summary(summary: str | None, full_name: str) -> str | None:
    """Ajusta el resumen al tope del contrato y avisa al equipo de IA.

    `shared.contracts.repo.Repo` rechaza más de 250 caracteres: recortar es
    preferible a tumbar la respuesta entera por una fila de IA.
    """
    if not summary or len(summary) <= SUMMARY_ES_MAX_LENGTH:
        return summary
    logger.warning(
        "summary_es de %s supera los %s caracteres del contrato (%s); se recorta.",
        full_name,
        SUMMARY_ES_MAX_LENGTH,
        len(summary),
    )
    return summary[:SUMMARY_ES_MAX_LENGTH]


def _unavailable(exc: SQLAlchemyError, action: str) -> CatalogUnavailableError:
    """Traduce fallos de base de datos sin filtrar detalles internos al cliente."""
    if isinstance(exc, DBAPIError) and getattr(exc.orig, "sqlstate", None) == "42501":
        # 42501 = insufficient_privilege: el rol de lectura no tiene los GRANT.
        logger.error(
            "Permisos insuficientes (sqlstate 42501) en la base al %s: %s",
            action,
            exc.orig,
        )
        return CatalogUnavailableError(
            "El catálogo no es accesible con los permisos actuales del servicio."
        )
    logger.warning("Error de base de datos al %s: %s", action, exc)
    return CatalogUnavailableError(
        "No se pudo consultar el catálogo en este momento."
    )


@dataclass(frozen=True)
class CatalogPage:
    """Una página del listado. El cuerpo es el array; la paginación va aparte."""

    items: list[CatalogRepo]
    page: int
    page_size: int
    total: int
    total_pages: int

    def headers(self) -> dict[str, str]:
        return {
            "X-Total-Count": str(self.total),
            "X-Total-Pages": str(self.total_pages),
            "X-Page": str(self.page),
            "X-Page-Size": str(self.page_size),
        }


class CatalogService:
    """Orquesta el repositorio y construye los modelos de respuesta."""

    def __init__(
        self,
        repository: RepoRepository,
        *,
        default_page_size: int,
        max_page_size: int,
    ) -> None:
        self._repository = repository
        self._default_page_size = default_page_size
        self._max_page_size = max_page_size

    def list_repos(
        self,
        *,
        page: int = 1,
        page_size: int | None = None,
        q: str | None = None,
        categories: Sequence[str] | None = None,
        language: str | None = None,
        license_spdx_id: str | None = None,
        maintenance: str | None = None,
        min_stars: int | None = None,
    ) -> CatalogPage:
        size = self._resolve_page_size(page_size)
        filters = RepoFilters(
            search=_clean(q),
            categories=tuple(
                c.strip() for c in (categories or ()) if c and c.strip()
            ),
            language=_clean(language),
            license_spdx_id=_clean(license_spdx_id),
            maintenance=maintenance,
            min_stars=min_stars,
        )
        try:
            result = self._repository.list_repos(
                filters, limit=size, offset=(page - 1) * size
            )
        except SQLAlchemyError as exc:
            raise _unavailable(exc, "listar repositorios") from exc

        try:
            items = [self._to_catalog_repo(row) for row in result.rows]
        except ValidationError as exc:
            raise CatalogUnavailableError(
                "El catálogo devolvió filas incompatibles con el contrato Repo."
            ) from exc

        total_pages = ceil(result.total / size) if result.total else 0
        return CatalogPage(
            items=items,
            page=page,
            page_size=size,
            total=result.total,
            total_pages=total_pages,
        )

    def get_repo(self, owner: str, name: str) -> RepoDetailResponse:
        full_name = f"{owner}/{name}"
        if not _FULL_NAME_RE.fullmatch(full_name):
            raise InvalidRequestError(
                f"'{full_name}' no cumple el formato owner/name del contrato Repo."
            )
        try:
            row = self._repository.get_repo(full_name)
        except SQLAlchemyError as exc:
            raise _unavailable(exc, f"leer {full_name}") from exc

        if row is None:
            raise RepoNotFoundError(full_name)

        try:
            return self._to_detail(row, full_name)
        except ValidationError as exc:
            logger.warning("Fila incompatible con RepoDetail (%s): %s", full_name, exc)
            raise CatalogUnavailableError(
                f"El catálogo devolvió datos incompatibles con el contrato para '{full_name}'."
            ) from exc

    def _resolve_page_size(self, page_size: int | None) -> int:
        if page_size is None:
            return self._default_page_size
        if page_size < 1:
            raise InvalidRequestError("page_size debe ser mayor o igual a 1.")
        if page_size > self._max_page_size:
            raise InvalidRequestError(
                f"page_size no puede superar {self._max_page_size}."
            )
        return page_size

    def _repo_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Traduce una fila SQL al contrato; no rellena huecos con valores falsos."""
        return {
            "github_id": row["github_id"],
            "full_name": row["full_name"],
            "name": row.get("name"),
            "description": row.get("description"),
            "homepage": row.get("homepage"),
            "topics": _as_list(row.get("topics")),
            "language": row.get("language"),
            "license_spdx_id": row.get("license_spdx_id"),
            "stargazers_count": row.get("stargazers_count"),
            "forks_count": row.get("forks_count"),
            "pushed_at": _to_datetime(row.get("pushed_at")),
            "archived": row.get("archived"),
            "readme_text": row.get("readme_text"),
            "open_issues_count": row.get("open_issues_count"),
            "summary_es": _fit_summary(row.get("summary_es"), row["full_name"]),
            "use_cases": _as_list(row.get("use_cases")),
            "categories": _as_list(row.get("categories")),
            "html_url": row.get("html_url"),
            "disabled": row.get("disabled"),
            "is_maintained": None,
            "health_score": None,
        }

    def _to_catalog_repo(self, row: dict[str, Any]) -> CatalogRepo:
        return CatalogRepo.model_validate(self._repo_payload(row))

    def _to_detail(self, row: dict[str, Any], full_name: str) -> RepoDetailResponse:
        repo = self._to_catalog_repo(row)
        return RepoDetailResponse(
            repo=repo,
            integration_ideas=self._to_ideas(row.get("ideas"), repo),
        )

    def _to_ideas(self, rows: Any, repo: CatalogRepo) -> list[IntegrationIdea]:
        """Una idea inválida se omite y se registra; no rompe la ficha entera."""
        ideas: list[IntegrationIdea] = []
        for raw in _as_list(rows):
            if not isinstance(raw, dict):
                logger.warning(
                    "Idea de IA con forma inesperada en %s; se omite.", repo.full_name
                )
                continue
            try:
                ideas.append(
                    IntegrationIdea.model_validate({**raw, "full_name": repo.full_name})
                )
            except ValidationError as exc:
                logger.warning(
                    "Idea de IA inválida en %s; se omite: %s", repo.full_name, exc
                )

        if repo.archived and ideas:
            # Regla de shared.contracts.repo_detail: un archivado no lleva ideas.
            logger.warning(
                "El repositorio archivado %s trae %s ideas; se omiten por contrato.",
                repo.full_name,
                len(ideas),
            )
            return []

        if len(ideas) > MAX_INTEGRATION_IDEAS:
            logger.warning(
                "%s trae %s ideas y el contrato admite %s; se recortan.",
                repo.full_name,
                len(ideas),
                MAX_INTEGRATION_IDEAS,
            )
            return ideas[:MAX_INTEGRATION_IDEAS]
        return ideas

