"""GET /repos/{owner}/{name}: `{repo, integration_ideas}`, datos de IA opcionales y errores."""
import logging

from sqlalchemy.exc import OperationalError

from conftest import FakeRepository, build_client, detail_row, idea_row
from shared.contracts.repo import Repo
from shared.contracts.repo_detail import RepoDetail as SharedRepoDetail


def test_detail_wraps_the_repo_and_its_ideas():
    repository = FakeRepository(detail=detail_row(ideas=[idea_row()]))
    with build_client(repository) as client:
        response = client.get("/repos/keycloak/keycloak")

    assert response.status_code == 200
    assert repository.detail_calls == ["keycloak/keycloak"]
    body = response.json()
    assert set(body) == {"repo", "integration_ideas"}
    # El cuerpo entero cumple el envoltorio compartido que consume el frontend.
    assert SharedRepoDetail.model_validate(body).repo.full_name == "keycloak/keycloak"
    repo = body["repo"]
    assert Repo.model_validate(repo).github_id == 2218615
    assert repo["topics"] == ["iam", "oauth2", "saml"]
    assert repo["html_url"] == "https://github.com/keycloak/keycloak"
    assert repo["open_issues_count"] == 1234
    assert repo["readme_text"].startswith("# Keycloak")
    assert repo["pushed_at"].startswith("2026-10-22T22:19:40")
    assert body["integration_ideas"][0]["full_name"] == "keycloak/keycloak"


def test_detail_without_ai_results_is_200_with_empty_values():
    repository = FakeRepository(
        detail=detail_row(
            summary_es=None, use_cases=None, categories=None, ideas=None, readme_text=None
        )
    )
    with build_client(repository) as client:
        body = client.get("/repos/keycloak/keycloak").json()

    assert body["repo"]["summary_es"] is None
    assert body["repo"]["use_cases"] == []
    assert body["repo"]["categories"] == []
    assert body["integration_ideas"] == []
    assert body["repo"]["readme_text"] is None
    assert body["repo"]["is_maintained"] is None
    assert body["repo"]["health_score"] is None


def test_detail_maps_integration_ideas_with_full_name():
    repository = FakeRepository(detail=detail_row(ideas=[idea_row()]))
    with build_client(repository) as client:
        idea = client.get("/repos/keycloak/keycloak").json()["integration_ideas"][0]

    assert idea["full_name"] == "keycloak/keycloak"
    assert idea["integration_type"] == "rest_api"
    assert idea["difficulty"] == "medium"
    assert idea["reviewed_at"] is None


def test_invalid_idea_is_skipped_and_logged(caplog):
    repository = FakeRepository(
        detail=detail_row(
            ideas=[idea_row(id="mal", compatible_stack=[]), idea_row(id="bien")]
        )
    )
    with caplog.at_level(logging.WARNING, logger="openbridge.catalog"):
        with build_client(repository) as client:
            ideas = client.get("/repos/keycloak/keycloak").json()["integration_ideas"]

    assert [idea["id"] for idea in ideas] == ["bien"]
    assert "inválida" in caplog.text


def test_archived_repo_drops_ideas_because_the_contract_forbids_them(caplog):
    repository = FakeRepository(detail=detail_row(archived=True, ideas=[idea_row()]))
    with caplog.at_level(logging.WARNING, logger="openbridge.catalog"):
        with build_client(repository) as client:
            body = client.get("/repos/keycloak/keycloak").json()

    assert body["repo"]["archived"] is True
    assert body["integration_ideas"] == []
    assert "archivado" in caplog.text


def test_owner_lookup_is_case_insensitive_at_the_repository_boundary():
    repository = FakeRepository(detail=detail_row(full_name="keycloak/keycloak"))
    with build_client(repository) as client:
        assert client.get("/repos/KeyCloak/KeyCloak").status_code == 200

    assert repository.detail_calls == ["KeyCloak/KeyCloak"]


def test_unknown_repo_is_404_with_repo_not_found():
    repository = FakeRepository(detail=None)
    with build_client(repository) as client:
        response = client.get("/repos/nadie/inexistente")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "repo_not_found"
    assert "nadie/inexistente" in response.json()["error"]["message"]


def test_path_characters_outside_owner_name_are_rejected():
    repository = FakeRepository(detail=detail_row())
    with build_client(repository) as client:
        response = client.get("/repos/key%20cloak/keycloak")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert repository.detail_calls == []


def test_long_summary_is_trimmed_to_the_contract_and_logged(caplog):
    largo = "b" * 450
    repository = FakeRepository(detail=detail_row(summary_es=largo))
    with caplog.at_level(logging.WARNING, logger="openbridge.catalog"):
        with build_client(repository) as client:
            body = client.get("/repos/keycloak/keycloak").json()

    assert len(body["repo"]["summary_es"]) == 250
    assert "250" in caplog.text


def test_database_failure_is_503():
    repository = FakeRepository(error=OperationalError("SELECT", {}, Exception("boom")))
    with build_client(repository) as client:
        response = client.get("/repos/keycloak/keycloak")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "catalog_unavailable"
