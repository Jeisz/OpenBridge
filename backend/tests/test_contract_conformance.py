"""Conformidad entre lo que la API publica y los contratos compartidos.

Cada aserción se contrastó con una respuesta real de la aplicación (TestClient,
repositorio falso, sin base de datos ni red) y con `shared/contracts/repo.py`
v1.2 (29-oct-2026) y `shared/contracts/repo_detail.py`.

Si un campo cambia de nombre, de tipo o de sitio (cuerpo ↔ cabeceras), esta
prueba falla antes de que lo note el frontend.
"""
from fastapi.testclient import TestClient

from conftest import FakeRepository, build_client, detail_row, idea_row, list_row
from backend.app.core.config import Settings
from backend.app.main import create_app
from shared.contracts.repo import Repo

# Repo v1.2 completo: la ficha lo publica entero.
CONTRACT_FIELDS = set(Repo.model_fields)
# El listado no consulta estas columnas, así que no las emite vacías.
LIST_EXCLUDED = {"readme_text", "topics"}
# Columnas de la tabla base que la API añade sobre el contrato.
API_EXTRAS = {"name", "html_url", "forks_count"}
PAGINATION_HEADERS = ("X-Total-Count", "X-Total-Pages", "X-Page", "X-Page-Size")
ERROR_FIELDS = {"code", "message"}


def test_list_body_is_the_contract_array():
    with build_client(FakeRepository([list_row()])) as client:
        body = client.get("/repos").json()

    assert isinstance(body, list)
    assert Repo.model_validate(body[0]).full_name == "keycloak/keycloak"


def test_list_publishes_the_contract_without_the_detail_only_columns():
    with build_client(FakeRepository([list_row()])) as client:
        item = client.get("/repos").json()[0]

    assert set(item) == (CONTRACT_FIELDS - LIST_EXCLUDED) | API_EXTRAS


def test_detail_body_has_exactly_repo_and_ideas():
    with build_client(FakeRepository(detail=detail_row(ideas=[idea_row()]))) as client:
        body = client.get("/repos/keycloak/keycloak").json()

    assert set(body) == {"repo", "integration_ideas"}
    assert isinstance(body["integration_ideas"], list)


def test_detail_publishes_every_contract_field_plus_api_extras():
    with build_client(FakeRepository(detail=detail_row())) as client:
        repo = client.get("/repos/keycloak/keycloak").json()["repo"]

    assert set(repo) == CONTRACT_FIELDS | API_EXTRAS
    # Lo que el listado omite sí viaja en la ficha.
    assert repo["topics"] == ["iam", "oauth2", "saml"]
    assert repo["readme_text"].startswith("# Keycloak")


def test_v12_field_types_are_the_contract_types():
    with build_client(FakeRepository([list_row(disabled=True, open_issues_count=None)])) as client:
        item = client.get("/repos").json()[0]

    assert isinstance(item["github_id"], int) and item["github_id"] > 0
    assert isinstance(item["full_name"], str) and item["full_name"].count("/") == 1
    assert isinstance(item["archived"], bool)
    assert item["disabled"] is True
    assert item["open_issues_count"] is None
    # Según contrato Repo v1.2, `is_maintained` es bool (True para repo activo reciente).
    assert item["is_maintained"] is True
    assert isinstance(item["categories"], list)
    for assignment in item["categories"]:
        assert set(assignment) == {"category_id", "assigned_by"}


def test_pagination_travels_in_headers_with_the_agreed_names():
    with build_client(FakeRepository([list_row()], total=45)) as client:
        response = client.get("/repos", params={"page": 3, "page_size": 10})

    assert tuple(
        header for header in PAGINATION_HEADERS if header in response.headers
    ) == PAGINATION_HEADERS
    assert response.headers["X-Total-Count"] == "45"
    assert response.headers["X-Total-Pages"] == "5"
    assert response.headers["X-Page"] == "3"
    assert response.headers["X-Page-Size"] == "10"
    # El cuerpo sigue siendo el array: no hay envoltorio con la paginación.
    assert isinstance(response.json(), list)


def test_documented_errors_share_the_same_body_shape():
    repository = FakeRepository(detail=None)
    with build_client(repository) as client:
        not_found = client.get("/repos/nadie/inexistente")
        invalid = client.get("/repos", params={"page_size": 0})

    assert not_found.status_code == 404
    assert not_found.json()["error"]["code"] == "repo_not_found"
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_request"
    for response in (not_found, invalid):
        assert set(response.json()) == {"error"}
        assert set(response.json()["error"]) == ERROR_FIELDS
        assert isinstance(response.json()["error"]["message"], str)


def test_catalog_without_database_is_503_with_the_catalog_code():
    with TestClient(create_app(Settings())) as client:
        response = client.get("/repos")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"


def test_archived_is_never_invented_when_the_row_brings_null():
    """`archived` es obligatorio en el contrato: NULL es 503, no `false`."""
    with build_client(FakeRepository([list_row(archived=None)])) as client:
        response = client.get("/repos")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"


def test_six_categories_are_preserved_in_the_catalog():
    categories = [{"category_id": name, "assigned_by": "rule"} for name in
                  ["database", "auth", "backend", "cache", "search", "infrastructure"]]
    with build_client(FakeRepository([list_row(categories=categories)])) as client:
        response = client.get("/repos")
    assert response.status_code == 200
    assert response.json()[0]["categories"] == categories


def test_categories_over_the_contract_limit_break_the_response():
    """Más de seis categorías exceden el contrato; no se descartan asignaciones."""
    row = list_row(categories=[{"category_id": "database", "assigned_by": "rule"}] * 7)
    with build_client(FakeRepository([row])) as client:
        response = client.get("/repos")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"


def test_unknown_route_uses_the_framework_404_body_not_the_api_one():
    """Deuda conocida: un 404 de ruta no pasa por `ErrorResponse`."""
    with build_client(FakeRepository()) as client:
        response = client.get("/categories")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_assistant_keeps_its_own_error_codes():
    with build_client(FakeRepository()) as client:
        unavailable = client.post(
            "/assistant", json={"query": "Necesito una aplicación para gestionar usuarios"}
        )
        invalid = client.post("/assistant", json={"query": "hola"})

    assert unavailable.status_code == 503
    assert unavailable.json()["error"]["code"] == "provider_unavailable"
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_query"


def test_health_shape_does_not_claim_more_than_liveness():
    with build_client(FakeRepository()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pushed_at_null_is_503_because_the_contract_requires_it():
    """`Repo.pushed_at` es obligatorio y el frontend hace `Date.parse`.

    Una fila sin fecha no se sirve con una fecha inventada: se reporta el
    catálogo como no disponible y se arregla en la ingesta.
    """
    with build_client(FakeRepository([list_row(pushed_at=None)])) as client:
        response = client.get("/repos")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"


def test_homepage_outside_the_contract_url_is_503_not_a_silent_fix():
    """`Repo.homepage` es `HttpUrl`: un valor que no es URL rompe la página entera.

    No se añade `https://` a lo que llega de la base: eso sería inventar datos.
    """
    with build_client(FakeRepository([list_row(homepage="keycloak.org")])) as client:
        response = client.get("/repos")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"
