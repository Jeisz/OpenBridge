"""Compatibilidad con el validador que ya usa el frontend de Fabián.

`frontend/src/data/catalogHttp.mjs` valida cada respuesta en tiempo de
ejecución y lanza `Respuesta del catálogo inválida` / `Ficha inválida` si algo
no encaja. Esas reglas están escritas en JavaScript, no en `shared/contracts`,
así que se replican aquí (sin tocar `frontend/`): si una regla cambia allí o una
respuesta deja de cumplirla, estas pruebas fallan antes que la interfaz.

Reglas replicadas:

- Listado (`adaptApiRepo`): `full_name` texto, `github_id` entero,
  `stargazers_count` número finito, `archived` booleano, `pushed_at`
  interpretable por `Date.parse`, `categories` array y `summary_es` nulo o de
  250 caracteres como mucho.
- Ficha (`detail`): `repo.full_name` **idéntico** al nombre pedido,
  `integration_ideas` array de 3 como máximo, ningún repositorio archivado con
  ideas y, en cada idea, `full_name` igual al de la ficha, `id`/`title`/`summary`
  de texto, `docs_url` con esquema `http(s)`, los enums de `integration_type` y
  `difficulty`, listas de texto en `compatible_stack`/`dependencies`/`triggers`
  y `snippet_language` cuando hay `snippet`.
"""
from datetime import datetime
import re

from conftest import FakeRepository, build_client, detail_row, idea_row, list_row

SUMMARY_MAX_LENGTH = 250
"""Mismo tope que `shared.contracts.repo.Repo` y que el frontend."""

INTEGRATION_TYPES = {"rest_api", "docker", "sdk", "webhook"}
DIFFICULTIES = {"low", "medium", "high"}

_DOCS_URL = re.compile(r"^https?://")

CONSUMED_KEYS = {
    "full_name",
    "github_id",
    "stargazers_count",
    "archived",
    "pushed_at",
    "categories",
    "summary_es",
    "health_score",
    "open_issues_count",
    "homepage",
    "description",
    "language",
    "license_spdx_id",
}
"""Claves que leen los módulos de `frontend/src/data/`; un `undefined` es un fallo."""


def _date_parse(value: str) -> datetime:
    """Equivalente estricto de `Date.parse`: lanza `ValueError` si no es ISO."""
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _assert_consumable_repo(item: dict) -> None:
    """Reglas de `adaptApiRepo` (catalogHttp.mjs, líneas 6-7)."""
    assert isinstance(item["full_name"], str)
    assert isinstance(item["github_id"], int) and item["github_id"] > 0
    assert isinstance(item["stargazers_count"], int) and item["stargazers_count"] >= 0
    assert isinstance(item["archived"], bool)
    _date_parse(item["pushed_at"])
    assert isinstance(item["categories"], list)
    summary = item["summary_es"]
    assert summary is None or (
        isinstance(summary, str) and len(summary) <= SUMMARY_MAX_LENGTH
    )


def _assert_consumable_idea(idea: dict, full_name: str) -> None:
    """Reglas del `detail` de catalogHttp.mjs (línea 44)."""
    assert idea["full_name"] == full_name
    assert isinstance(idea["id"], str)
    assert isinstance(idea["title"], str)
    assert isinstance(idea["summary"], str)
    assert idea["integration_type"] in INTEGRATION_TYPES
    assert idea["difficulty"] in DIFFICULTIES
    assert isinstance(idea["compatible_stack"], list) and idea["compatible_stack"]
    assert all(isinstance(value, str) for value in idea["compatible_stack"])
    for key in ("dependencies", "triggers"):
        values = idea.get(key) or []
        assert isinstance(values, list)
        assert all(isinstance(value, str) for value in values)
    assert isinstance(idea["docs_url"], str) and _DOCS_URL.match(idea["docs_url"])
    assert idea["snippet"] is None or isinstance(idea["snippet"], str)
    if idea["snippet"]:
        assert isinstance(idea["snippet_language"], str)


def test_list_ships_every_key_the_frontend_reads():
    with build_client(FakeRepository([list_row()])) as client:
        item = client.get("/repos").json()[0]

    assert CONSUMED_KEYS <= set(item)


def test_list_item_is_consumable_by_the_frontend():
    with build_client(FakeRepository([list_row()])) as client:
        item = client.get("/repos").json()[0]

    _assert_consumable_repo(item)


def test_list_item_without_ai_or_optional_data_is_still_consumable():
    """Un repositorio sin enriquecimiento no puede romper el listado del frontend."""
    row = list_row(
        summary_es=None,
        use_cases=[],
        categories=[],
        open_issues_count=None,
        disabled=None,
        homepage=None,
        description=None,
        language=None,
        license_spdx_id=None,
        forks_count=None,
    )
    with build_client(FakeRepository([row])) as client:
        item = client.get("/repos").json()[0]

    _assert_consumable_repo(item)
    assert item["summary_es"] is None
    assert item["categories"] == []


def test_pushed_at_is_interpretable_by_the_frontend_date_parse():
    with build_client(
        FakeRepository([list_row(pushed_at="2026-10-22T22:19:40Z")])
    ) as client:
        item = client.get("/repos").json()[0]

    parsed = _date_parse(item["pushed_at"])
    assert parsed.tzinfo is not None
    assert (parsed.year, parsed.month, parsed.day) == (2026, 10, 22)


def test_trimmed_summary_keeps_the_frontend_length_rule():
    """El frontend cuenta puntos de código (`Array.from`), igual que `len`."""
    with build_client(
        FakeRepository([list_row(summary_es="a" * 240 + "😀" * 20)])
    ) as client:
        item = client.get("/repos").json()[0]

    assert len(item["summary_es"]) == SUMMARY_MAX_LENGTH
    _assert_consumable_repo(item)


def test_detail_payload_is_consumable_by_the_frontend():
    with build_client(FakeRepository(detail=detail_row(ideas=[idea_row()]))) as client:
        body = client.get("/repos/keycloak/keycloak").json()

    repo = body["repo"]
    _assert_consumable_repo(repo)
    # catalogHttp.mjs compara con igualdad exacta contra el nombre de la ruta.
    assert repo["full_name"] == "keycloak/keycloak"
    assert 0 <= len(body["integration_ideas"]) <= 3
    _assert_consumable_idea(body["integration_ideas"][0], repo["full_name"])


def test_detail_without_ai_results_is_consumable_with_empty_ideas():
    with build_client(FakeRepository(detail=detail_row(ideas=[]))) as client:
        body = client.get("/repos/keycloak/keycloak").json()

    _assert_consumable_repo(body["repo"])
    assert body["integration_ideas"] == []


def test_archived_detail_never_ships_ideas_to_the_frontend():
    """`catalogHttp.mjs` lanza `Ficha inválida` si un archivado trae ideas."""
    with build_client(
        FakeRepository(detail=detail_row(archived=True, ideas=[idea_row()]))
    ) as client:
        body = client.get("/repos/keycloak/keycloak").json()

    assert body["repo"]["archived"] is True
    assert body["integration_ideas"] == []


def test_detail_answers_with_the_canonical_full_name_of_the_row():
    """La ficha devuelve el `full_name` almacenado, no el escrito en la ruta.

    El frontend exige `payload.repo.full_name === name`, así que debe pedir el
    nombre exacto que le entregó el listado; la búsqueda en SQL sí ignora
    mayúsculas.
    """
    with build_client(
        FakeRepository(detail=detail_row(full_name="Keycloak/Keycloak"))
    ) as client:
        body = client.get("/repos/keycloak/keycloak").json()

    assert body["repo"]["full_name"] == "Keycloak/Keycloak"
