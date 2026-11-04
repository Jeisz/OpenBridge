"""Valida los datos de ejemplo de la IA (ai/data/seed/ejemplo_ia.json) y cómo se
convierten en filas. No se conecta a la base.

Correr desde la raíz del repo, con el entorno activo:
    python -m pytest ai/tests/test_seed_example.py -v
"""

import copy
import json

import pytest

from ai.catalog import load_categories
from ai.scripts.export_catalog_snapshot import REPOS_FILE
from ai.scripts.load_seed_example import (
    IDEA_COLUMNS,
    MARKER,
    load_seed,
    to_rows,
    validate_seed,
)
from shared.contracts.integration_idea import IntegrationIdea


@pytest.fixture(scope="module")
def seed() -> dict:
    return load_seed()


@pytest.fixture(scope="module")
def snapshot() -> list[dict]:
    return json.loads(REPOS_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def category_ids() -> set[str]:
    return set(load_categories())


def test_la_semilla_es_valida(seed, snapshot, category_ids):
    # Si algo falla, el ValueError lista todos los errores.
    validate_seed(seed, snapshot, category_ids)


# Cada caso rompe UNA regla en una copia de la semilla. Como la semilla real es
# válida (test de arriba), el error solo puede venir de ese cambio.
def _con_ideas(seed: dict) -> dict:
    return next(repo for repo in seed["repos"] if repo["ideas"])


def marca_equivocada(s): s["marker"] = "otra-marca"
def repo_fuera_del_catalogo(s): s["repos"][0]["github_id"] = 1
def full_name_que_no_coincide(s): s["repos"][0]["full_name"] = "otro/repo"
def categoria_que_no_existe(s): s["repos"][0]["categories"][0]["category_id"] = "no-existe"
def resumen_de_251(s): s["repos"][0]["summary_es"] = "x" * 251
def mas_de_3_ideas(s):
    repo = _con_ideas(s)
    repo["ideas"] = repo["ideas"] * 4
def stack_de_41(s): _con_ideas(s)["ideas"][0]["compatible_stack"] = ["x" * 41]
def idea_sin_marca(s): _con_ideas(s)["ideas"][0]["based_on_hash"] = "abc123"
def idea_revisada(s): _con_ideas(s)["ideas"][0]["reviewed_at"] = "2026-10-31T00:00:00Z"


@pytest.mark.parametrize("romper, mensaje", [
    (marca_equivocada, "marker debe ser"),
    (repo_fuera_del_catalogo, "no está en el snapshot"),
    (full_name_que_no_coincide, "no está en el snapshot"),
    (categoria_que_no_existe, "categoría que no existe"),
    (resumen_de_251, "no cumple Repo"),
    (mas_de_3_ideas, "máximo 3"),
    (stack_de_41, "no cumple IntegrationIdea"),
    (idea_sin_marca, "based_on_hash debe ser"),
    (idea_revisada, "reviewed_at debe ser null"),
], ids=lambda x: x.__name__ if callable(x) else None)
def test_cada_regla_rechaza_su_caso(seed, snapshot, category_ids, romper, mensaje):
    roto = copy.deepcopy(seed)
    romper(roto)
    with pytest.raises(ValueError, match=mensaje):
        validate_seed(roto, snapshot, category_ids)


def test_rank_sale_del_orden(seed):
    rows = to_rows(seed)["categories"]
    for repo in seed["repos"]:
        got = [(r["category_id"], r["rank"]) for r in rows if r["github_id"] == repo["github_id"]]
        expected = [(c["category_id"], i) for i, c in enumerate(repo["categories"], start=1)]
        assert got == expected, repo["full_name"]


def test_enrichment_lleva_la_marca(seed):
    rows = to_rows(seed)["enrichment"]
    assert len(rows) == len(seed["repos"])
    assert all(r["ai_input_hash"] == MARKER for r in rows)


def test_columnas_de_ideas_siguen_el_contrato():
    # Columnas de ai_integration_ideas = IntegrationIdea sin
    # full_name + github_id, sin renombrar. Si cambia el contrato, este test avisa.
    assert set(IDEA_COLUMNS) == set(IntegrationIdea.model_fields) - {"full_name"} | {"github_id"}
