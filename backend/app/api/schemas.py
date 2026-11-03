"""Modelos HTTP del catálogo, con las formas que ya consume el frontend.

- `GET /repos` devuelve un array de repositorios, sin envoltorio.
- `GET /repos/{owner}/{name}` devuelve `{repo, integration_ideas}`, que es el
  contrato `shared.contracts.repo_detail.RepoDetail`.

`CatalogRepo` es un superconjunto de `shared.contracts.repo.Repo`: añade las
columnas que sólo existen en la ficha (`html_url`, `forks_count`, `disabled`).
Un repositorio que cumple `Repo` cumple `CatalogRepo`; el frontend ignora los
campos extra.

`is_maintained` y `health_score` viajan siempre en NULL: no hay campo, criterio
ni fórmula acordados, y no se inventan valores.

La paginación no viaja en el cuerpo: va en las cabeceras `X-Total-Count`,
`X-Total-Pages`, `X-Page` y `X-Page-Size`, porque el cuerpo es el array.
"""
from typing import Literal

from pydantic import BaseModel, Field

from shared.contracts.repo import Repo
from shared.contracts.repo_detail import RepoDetail as SharedRepoDetail

# Mismo patrón que shared/contracts/repo.py; hay un test que impide que se separe.
FULL_NAME_PATTERN = r"^[^/\s]+/[^/\s]+$"

SUMMARY_ES_MAX_LENGTH = 250
"""Tope acordado para el resumen de IA; `Repo` lo valida."""

MAX_INTEGRATION_IDEAS = 3
"""Tope de ideas por ficha que fija `shared.contracts.repo_detail`."""

PAGINATION_HEADERS = ("X-Total-Count", "X-Total-Pages", "X-Page", "X-Page-Size")
"""Cabeceras con la paginación del listado."""


class CatalogRepo(Repo):
    """Contrato `Repo` más las columnas propias de la ficha."""

    name: str | None = Field(default=None, description="Nombre del repositorio sin owner.")
    html_url: str | None = Field(default=None, description="URL pública del repositorio.")
    forks_count: int | None = Field(default=None, ge=0)
    disabled: bool | None = Field(
        default=None,
        description="catalog_repositories.disabled. NULL = sin dato; no se convierte a false.",
    )
    is_maintained: bool | None = Field(
        default=None,
        description="Pendiente: ni el campo ni el criterio están acordados (siempre NULL).",
    )
    health_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Pendiente: no hay fórmula acordada (siempre NULL).",
    )


class CatalogListItem(CatalogRepo):
    """Elemento del listado: el contrato sin las columnas que sólo lee la ficha.

    `readme_text` y `topics` se excluyen al serializar porque el listado no las
    consulta; emitirlas vacías sugeriría que el repositorio no tiene README ni
    temas. La ficha sí las devuelve.
    """

    readme_text: str | None = Field(
        default=None,
        exclude=True,
        description="No se consulta en el listado; la ficha lo trae completo.",
    )
    topics: list[str] = Field(
        default_factory=list,
        exclude=True,
        description="No se consultan en el listado; la ficha los trae.",
    )


class RepoDetailResponse(SharedRepoDetail):
    """Ficha HTTP: el envoltorio compartido con la ficha enriquecida.

    Hereda de `shared.contracts.repo_detail.RepoDetail`, así que mantiene sus
    reglas: como mucho tres ideas, todas del mismo repositorio y ninguna en un
    repositorio archivado.
    """

    repo: CatalogRepo


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Cuerpo de error del catálogo (misma forma que `shared.contracts.assistant.ErrorResponse`).

    Códigos: `invalid_request` (422), `repo_not_found` (404),
    `catalog_unavailable` (503).
    """

    error: ErrorDetail
