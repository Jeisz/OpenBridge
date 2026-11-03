"""Rutas del catálogo: GET /repos y GET /repos/{owner}/{name}.

Sin prefijo /api: el acuerdo del 29-oct-2026 fija las rutas en la raíz.
Las formas de respuesta son las que ya consume el frontend: array en el listado
y `{repo, integration_ideas}` en la ficha. La paginación del listado viaja en
cabeceras para no cambiar el cuerpo.

`/categories` e `integrations` no se exponen. `POST /assistant` es el servicio
independiente del asistente (ver `routes/assistant.py`).
"""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, Response

from backend.app.api.deps import get_catalog_service
from backend.app.api.schemas import (
    CatalogListItem,
    ErrorResponse,
    RepoDetailResponse,
)
from backend.app.services.catalog import CatalogService

router = APIRouter(prefix="/repos", tags=["repos"])

Maintenance = Literal["active", "inactive"]

_NAME_PATTERN = r"^[A-Za-z0-9_.-]{1,100}$"

_RESPONSES = {
    422: {"model": ErrorResponse, "description": "Parámetro fuera de las reglas del catálogo."},
    503: {"model": ErrorResponse, "description": "Base de datos no configurada o no disponible."},
}


@router.get(
    "",
    response_model=list[CatalogListItem],
    summary="Listado paginado de repositorios",
    description=(
        "Devuelve un array con la página actual del catálogo. Sin resultados "
        "responde 200 con `[]`.\n\n"
        "La paginación viaja en las cabeceras `X-Total-Count`, `X-Total-Pages`, "
        "`X-Page` y `X-Page-Size`, porque el cuerpo del contrato es el array.\n\n"
        "El listado no consulta `readme_text` ni `topics`: esas claves sólo las "
        "trae la ficha. Ningún NULL se sustituye por 0 ni por `false`.\n\n"
        "Los filtros replican los de la interfaz: búsqueda por texto, categoría "
        "(cualquiera de las asignadas), lenguaje, licencia SPDX, mantenimiento y "
        "estrellas mínimas.\n\n"
        "`maintenance` es la aproximación local acordada con Frontend "
        "(active = ni archivado ni deshabilitado); el criterio definitivo de "
        "mantenedor sigue pendiente.\n\n"
        "El orden es `full_name ASC`, elegido para que la paginación sea estable; "
        "no es una regla de negocio acordada."
    ),
    responses={**_RESPONSES, 200: {"description": "Página de repositorios."}},
)
def list_repos(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    response: Response,
    q: Annotated[
        str | None,
        Query(
            max_length=120,
            description="Texto a buscar en full_name, nombre, descripción y resumen de IA.",
            examples=["keycloak"],
        ),
    ] = None,
    category: Annotated[
        list[str] | None,
        Query(
            description=(
                "Categoría principal o secundaria asignada por IA. "
                "Se puede repetir para pedir varias (se combinan con OR)."
            ),
            examples=[["autenticacion"]],
        ),
    ] = None,
    language: Annotated[
        str | None,
        Query(max_length=50, description="Lenguaje principal; sin distinguir mayúsculas.", examples=["Go"]),
    ] = None,
    license: Annotated[
        str | None,
        Query(max_length=50, description="Identificador SPDX de la licencia.", examples=["MIT"]),
    ] = None,
    maintenance: Annotated[
        Maintenance | None,
        Query(description="Aproximación local: active = ni archivado ni deshabilitado."),
    ] = None,
    min_stars: Annotated[
        int | None,
        Query(ge=0, description="Estrellas mínimas (>=).", examples=[1000]),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Página, empezando en 1.")] = 1,
    page_size: Annotated[
        int | None,
        Query(ge=1, description="Tamaño de página; por defecto 20 y máximo 100."),
    ] = None,
) -> list[CatalogListItem]:
    result = service.list_repos(
        page=page,
        page_size=page_size,
        q=q,
        categories=category,
        language=language,
        license_spdx_id=license,
        maintenance=maintenance,
        min_stars=min_stars,
    )
    response.headers.update(result.headers())
    return result.items


@router.get(
    "/{owner}/{name}",
    response_model=RepoDetailResponse,
    summary="Ficha de un repositorio",
    description=(
        "Devuelve `repo` (contrato Repo completo más `html_url`, `forks_count` y "
        "`disabled`) e `integration_ideas`.\n\n"
        "Un repositorio sin resultados de IA responde 200 con `summary_es: null`, "
        "`categories: []`, `use_cases: []` e `integration_ideas: []`.\n\n"
        "La ficha cumple `shared.contracts.repo_detail`: como mucho tres ideas, "
        "todas del mismo repositorio, y ninguna si el repositorio está archivado.\n\n"
        "`is_maintained` y `health_score` viajan en `null`: no hay campo, "
        "criterio ni fórmula acordados."
    ),
    responses={
        200: {"description": "Ficha del repositorio."},
        404: {"model": ErrorResponse, "description": "El repositorio no está en el catálogo."},
        422: _RESPONSES[422],
        503: _RESPONSES[503],
    },
)
def get_repo(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    owner: Annotated[str, Path(pattern=_NAME_PATTERN, description="Owner de GitHub.", examples=["keycloak"])],
    name: Annotated[str, Path(pattern=_NAME_PATTERN, description="Nombre del repositorio.", examples=["keycloak"])],
) -> RepoDetailResponse:
    return service.get_repo(owner, name)
