"""Alineación con los contratos compartidos y superficie HTTP publicada."""
import json
from pathlib import Path

from conftest import FakeRepository, build_client, list_row
from backend.app.api.schemas import (
    FULL_NAME_PATTERN,
    CatalogListItem,
    CatalogRepo,
    RepoDetailResponse,
)
from backend.app.repositories.repos import build_detail_statement
from shared.contracts.integration_idea import IntegrationIdea
from shared.contracts.repo import CategoryAssignment, Repo
from shared.contracts.repo_detail import RepoDetail as SharedRepoDetail

CATEGORIES_JSON = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "categories.json"
)


def test_full_name_pattern_matches_the_shared_contract():
    contract_patterns = [
        getattr(metadata, "pattern", None)
        for metadata in Repo.model_fields["full_name"].metadata
    ]
    assert FULL_NAME_PATTERN in contract_patterns
    assert CatalogRepo.model_fields["full_name"].metadata[0].pattern == FULL_NAME_PATTERN


def test_published_paths_are_the_catalog_and_the_assistant():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        paths = set(client.get("/openapi.json").json()["paths"])

    assert paths == {"/health", "/repos", "/repos/{owner}/{name}", "/assistant"}
    assert not any(path.startswith("/api") for path in paths)


def test_out_of_scope_routes_are_not_exposed():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        for path in ("/categories", "/integrations", "/repos/keycloak/keycloak/ideas"):
            assert client.get(path).status_code == 404, path


def test_catalog_repo_is_a_superset_of_the_shared_contract():
    assert issubclass(CatalogRepo, Repo)
    assert issubclass(CatalogListItem, CatalogRepo)
    for extra in ("html_url", "forks_count"):
        assert extra in CatalogRepo.model_fields
        assert extra not in Repo.model_fields
    for shared in ("disabled", "is_maintained"):
        assert shared in Repo.model_fields
        assert CatalogRepo.model_fields[shared].annotation == Repo.model_fields[shared].annotation


def test_detail_response_reuses_the_shared_wrapper():
    assert issubclass(RepoDetailResponse, SharedRepoDetail)
    assert issubclass(RepoDetailResponse.model_fields["repo"].annotation, Repo)


def test_list_item_categories_use_the_contract_model():
    repository = FakeRepository([list_row()])
    with build_client(repository) as client:
        item = client.get("/repos").json()[0]

    for category in item["categories"]:
        assert CategoryAssignment.model_validate(category).assigned_by in {
            "rule",
            "llm",
            "human",
        }


def test_categories_come_from_the_shared_file_not_from_a_local_copy():
    shared = json.loads(CATEGORIES_JSON.read_text(encoding="utf-8"))
    ids = [category["id"] for category in shared["categories"]]
    # La API no mantiene su propia lista: los ids llegan desde ai.ai_repo_categories.
    assert len(ids) == len(set(ids)) == 18
    assert "auth" in ids


def test_pending_fields_are_optional_and_documented():
    for field_name in ("is_maintained", "health_score"):
        field = CatalogRepo.model_fields[field_name]
        assert field.default is None
        assert "Pendiente" in (field.description or "")


def test_detail_sql_builds_every_contract_idea_field():
    sql = build_detail_statement()
    missing = [
        name
        for name in IntegrationIdea.model_fields
        if name != "full_name" and f"'{name}', i.{name}" not in sql
    ]
    # full_name lo pone el servicio desde la ruta: la tabla ai no lo guarda.
    assert missing == []


def test_detail_sql_builds_every_category_assignment_field():
    sql = build_detail_statement()
    missing = [
        name
        for name in CategoryAssignment.model_fields
        if f"'{name}', c.{name}" not in sql
    ]
    assert missing == []
