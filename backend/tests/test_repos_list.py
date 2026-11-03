"""GET /repos: array del contrato, paginación en cabeceras y filtros acordados."""
import logging

from conftest import FakeRepository, build_client, list_row
from shared.contracts.repo import Repo


def _pagination(response) -> dict[str, int]:
    return {
        "total": int(response.headers["X-Total-Count"]),
        "total_pages": int(response.headers["X-Total-Pages"]),
        "page": int(response.headers["X-Page"]),
        "page_size": int(response.headers["X-Page-Size"]),
    }


def test_body_is_the_contract_array_not_an_envelope():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        response = client.get("/repos")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["full_name"] == "keycloak/keycloak"
    # Lo que el frontend valida es el contrato compartido, no una copia local.
    assert Repo.model_validate(body[0]).github_id == 2218615


def test_uses_default_pagination_from_settings():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        response = client.get("/repos")

    assert response.status_code == 200
    assert repository.list_calls == [
        {"filters": repository.list_calls[0]["filters"], "limit": 20, "offset": 0}
    ]
    assert _pagination(response) == {
        "total": 1,
        "total_pages": 1,
        "page": 1,
        "page_size": 20,
    }


def test_page_and_page_size_become_limit_and_offset():
    repository = FakeRepository([list_row()], total=45)
    with build_client(repository) as client:
        response = client.get("/repos", params={"page": 3, "page_size": 10})

    assert repository.list_calls[0]["limit"] == 10
    assert repository.list_calls[0]["offset"] == 20
    assert _pagination(response) == {
        "total": 45,
        "total_pages": 5,
        "page": 3,
        "page_size": 10,
    }


def test_empty_result_is_an_empty_array_with_zero_totals():
    repository = FakeRepository([])
    with build_client(repository) as client:
        response = client.get("/repos")

    assert response.json() == []
    assert _pagination(response) == {
        "total": 0,
        "total_pages": 0,
        "page": 1,
        "page_size": 20,
    }


def test_list_does_not_expose_columns_it_does_not_query():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        item = client.get("/repos").json()[0]

    # El listado no lee README ni temas: no se emiten como si fueran datos.
    assert "readme_text" not in item
    assert "topics" not in item


def test_agreed_filters_are_forwarded():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        client.get(
            "/repos",
            params=[
                ("q", "  keycloak  "),
                ("category", "auth"),
                ("category", "database"),
                ("language", "Java"),
                ("license", "Apache-2.0"),
                ("maintenance", "active"),
                ("min_stars", 1000),
            ],
        )

    filters = repository.list_calls[0]["filters"]
    assert filters.search == "keycloak"
    assert filters.categories == ("auth", "database")
    assert filters.language == "Java"
    assert filters.license_spdx_id == "Apache-2.0"
    assert filters.maintenance == "active"
    assert filters.min_stars == 1000


def test_without_filters_the_repository_gets_empty_filters():
    repository = FakeRepository([])
    with build_client(repository) as client:
        client.get("/repos")

    filters = repository.list_calls[0]["filters"]
    assert (filters.search, filters.categories, filters.language) == (None, (), None)
    assert (filters.license_spdx_id, filters.maintenance, filters.min_stars) == (
        None,
        None,
        None,
    )

def test_missing_ai_data_is_null_not_zero_or_false():
    repository = FakeRepository(
        [list_row(summary_es=None, disabled=None, description=None, categories=None)]
    )
    with build_client(repository) as client:
        item = client.get("/repos").json()[0]

    assert item["summary_es"] is None
    assert item["disabled"] is None
    assert item["description"] is None
    assert item["categories"] == []
    assert item["is_maintained"] is None
    assert item["health_score"] is None


def test_archived_null_is_not_served_as_false():
    """`archived` es obligatorio en el contrato: sin dato se responde 503."""
    repository = FakeRepository([list_row(archived=None)])
    with build_client(repository) as client:
        response = client.get("/repos")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"


def test_categories_keep_all_assignments_and_order():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        item = client.get("/repos").json()[0]

    assert item["categories"] == [
        {"category_id": "auth", "assigned_by": "llm"},
        {"category_id": "database", "assigned_by": "human"},
    ]


def test_summary_over_250_chars_is_trimmed_to_the_contract_and_logged(caplog):
    largo = "a" * 300
    repository = FakeRepository([list_row(summary_es=largo)])
    with caplog.at_level(logging.WARNING, logger="openbridge.catalog"):
        with build_client(repository) as client:
            item = client.get("/repos").json()[0]

    assert len(item["summary_es"]) == 250
    assert "250" in caplog.text


def test_page_size_over_max_is_422():
    repository = FakeRepository([])
    with build_client(repository) as client:
        response = client.get("/repos", params={"page_size": 101})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert repository.list_calls == []


def test_invalid_query_parameters_use_the_error_body():
    repository = FakeRepository([])
    with build_client(repository) as client:
        for params in (
            {"page": 0},
            {"page_size": 0},
            {"maintenance": "quizas"},
            {"min_stars": -1},
        ):
            response = client.get("/repos", params=params)
            assert response.status_code == 422, params
            assert response.json()["error"]["code"] == "invalid_request"
    assert repository.list_calls == []


def test_validation_messages_are_spanish_and_name_the_parameter():
    with build_client(FakeRepository()) as client:
        message = client.get("/repos", params={"page_size": 0}).json()["error"]["message"]
        assert message == "El parámetro 'page_size' debe ser mayor o igual a 1."

        message = client.get("/repos", params={"maintenance": "quizas"}).json()["error"][
            "message"
        ]
        assert message.startswith("El parámetro 'maintenance' debe ser uno de")

        message = client.get("/repos", params={"q": "x" * 121}).json()["error"]["message"]
        assert message == "El parámetro 'q' no puede superar 120 caracteres."


def test_database_failure_is_503():
    from sqlalchemy.exc import OperationalError

    repository = FakeRepository(
        [], error=OperationalError("SELECT", {}, Exception("boom"))
    )
    with build_client(repository) as client:
        response = client.get("/repos")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"


def test_missing_grants_are_503_with_a_permission_message(caplog):
    from psycopg.errors import InsufficientPrivilege
    from sqlalchemy.exc import DBAPIError

    error = DBAPIError(
        "SELECT",
        {},
        InsufficientPrivilege("permission denied for table catalog_repositories"),
    )
    repository = FakeRepository([], error=error)
    with caplog.at_level(logging.ERROR, logger="openbridge.catalog"):
        with build_client(repository) as client:
            response = client.get("/repos")

    assert response.status_code == 503
    assert "permisos" in response.json()["error"]["message"]
    assert "42501" in caplog.text
