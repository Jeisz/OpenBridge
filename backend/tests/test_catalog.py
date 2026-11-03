"""Catálogo publicado: mismas comprobaciones que el archivo original de
`front-back-test`, ahora sobre el repositorio inyectado en vez de `ai/data`.

El listado y la ficha salen del mismo repositorio, no hay rutas sueltas, las
categorías pertenecen a la lista compartida y el asistente no simula respuestas.
"""
import json
from pathlib import Path

from conftest import FakeRepository, build_client, detail_row, idea_row, list_row
from shared.contracts.repo import Repo
from shared.contracts.repo_detail import RepoDetail as SharedRepoDetail

CATEGORIES_JSON = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "categories.json"
)


def test_catalog_detail_and_ideas_use_same_repository():
    repository = FakeRepository([list_row()], detail=detail_row(ideas=[idea_row()]))
    with build_client(repository) as client:
        response = client.get("/repos")
        assert response.status_code == 200
        repos = response.json()
        assert len(repos) > 0
        repo = repos[0]

        payload = client.get("/repos/" + repo["full_name"]).json()
        assert payload["repo"]["full_name"] == repo["full_name"]
        assert SharedRepoDetail.model_validate(payload).repo.full_name == repo["full_name"]
        assert Repo.model_validate(repo).full_name == repo["full_name"]

        assert (
            client.get("/repos/" + repo["full_name"] + "/integration-ideas").status_code
            == 404
        )
        assert client.get("/categories").status_code == 404

        shared = json.loads(CATEGORIES_JSON.read_text(encoding="utf-8"))
        categories = {category["id"] for category in shared["categories"]}
        assert all(c["category_id"] in categories for r in repos for c in r["categories"])

    unknown = FakeRepository([list_row()], detail=None)
    with build_client(unknown) as client:
        assert client.get("/repos/unknown/missing").status_code == 404


def test_assistant_does_not_simulate_generation():
    with build_client(FakeRepository()) as client:
        response = client.post(
            "/assistant", json={"query": "Necesito una aplicación para gestionar usuarios"}
        )
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "provider_unavailable"

        invalid = client.post("/assistant", json={"query": "hola"})
        assert invalid.status_code == 422
        assert invalid.json()["error"]["code"] == "invalid_query"


def test_summary_limit_is_250_characters():
    import pytest
    from pydantic import ValidationError

    record = list_row()
    assert len(Repo.model_validate({**record, "summary_es": "á" * 250}).summary_es) == 250
    with pytest.raises(ValidationError):
        Repo.model_validate({**record, "summary_es": "á" * 251})
