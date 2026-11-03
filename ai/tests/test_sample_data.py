"""Valida los datos de ejemplo de la IA (ai/data/) contra el esquema `Repo`.

Correr desde la raíz del repo, con el entorno activo:
    python -m pytest ai/tests -v
"""

import json
from pathlib import Path

import pytest

from ai.catalog import load_raw, load_repos
from shared.contracts.repo import CategoryList, Repo

CATEGORIES_FILE = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "categories.json"
)


@pytest.fixture(scope="module")
def raw_repos() -> list[dict]:
    """Contenido de repos.json tal cual, sin validar."""
    return load_raw(source="sample")


@pytest.fixture(scope="module")
def repos() -> list[Repo]:
    """Los repos ya validados con su README."""
    return load_repos(source="sample")


@pytest.fixture(scope="module")
def category_ids() -> set[str]:
    data = json.loads(CATEGORIES_FILE.read_text(encoding="utf-8"))
    return {c.id for c in CategoryList.model_validate(data).categories}


def test_datos_cumplen_el_contrato():
    # Si algún repo no cumple, load_repos lanza ValidationError y el test falla
    # mostrando todos los errores.
    load_repos(source="sample")


def test_claves_son_campos_del_contrato(raw_repos):
    # Los campos desconocidos son ignorados por el contrato. En nuestros datos,
    # una clave desconocida es casi siempre un error de tipeo.
    campos = set(Repo.model_fields)
    desconocidas = {clave for r in raw_repos for clave in r} - campos
    assert not desconocidas, f"Claves que no están en el contrato: {sorted(desconocidas)}"


def test_cantidad_de_repos(repos):
    assert 15 <= len(repos) <= 20, f"Hay {len(repos)} repos; se esperan 15–20"


def test_ids_unicos(repos):
    # El asistente solo puede citar repos del catálogo, y para comprobarlo
    # cada full_name tiene que identificar un solo repo.
    full_names = [r.full_name for r in repos]
    github_ids = [r.github_id for r in repos]
    assert len(full_names) == len(set(full_names)), "full_name duplicado"
    assert len(github_ids) == len(set(github_ids)), "github_id duplicado"


def test_todos_tienen_categoria(repos):
    # El contrato permite repos sin categoría (aún no procesados). Los datos de
    # ejemplo no.
    sin_categoria = [r.full_name for r in repos if not r.categories]
    assert not sin_categoria, f"Repos sin categoría: {sin_categoria}"


def test_categorias_existen(repos, category_ids):
    usadas = {a.category_id for r in repos for a in r.categories}
    desconocidas = usadas - category_ids
    assert not desconocidas, f"Categorías que no están en categories.json: {sorted(desconocidas)}"


def test_todos_tienen_readme(repos):
    # En los datos de ejemplo todos los repos deben tener su README guardado.
    sin_readme = [r.full_name for r in repos if not r.readme_text]
    assert not sin_readme, f"Repos sin README en ai/data/readmes/: {sin_readme}"
