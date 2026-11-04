"""Valida el snapshot del catálogo real (ai/data/catalog/) y las funciones del
script que lo genera. No se conecta a la base.

Correr desde la raíz del repo, con el entorno activo:
    python -m pytest ai/tests/test_catalog_snapshot.py -v
"""

import json

import pytest

from ai.scripts.export_catalog_snapshot import (
    INGESTION_FIELDS,
    META_FILE,
    README_DIR,
    REPOS_FILE,
    compare_columns,
    readme_path,
    redact,
    validate,
)
from shared.contracts.repo import Repo

# Claves acordadas de meta.json. Nunca host, usuario ni contraseña.
META_KEYS = {"source", "taken_at", "count", "command", "ignored_columns", "missing_fields"}


@pytest.fixture(scope="module")
def raw_repos() -> list[dict]:
    """repos.json tal cual, sin validar."""
    return json.loads(REPOS_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def meta() -> dict:
    return json.loads(META_FILE.read_text(encoding="utf-8"))


def test_cantidad_coincide_con_meta(raw_repos, meta):
    assert len(raw_repos) > 0
    assert len(raw_repos) == meta["count"]


def test_cumplen_el_contrato(raw_repos):
    # Si alguno no cumple, Pydantic lanza ValidationError y el test falla.
    for raw in raw_repos:
        Repo.model_validate(raw)


def test_solo_campos_de_la_ingesta(raw_repos):
    # Sin la mitad de la IA (categories, use_cases, summary_es) ni readme_text,
    # que va en readmes/.
    permitidos = INGESTION_FIELDS - {"readme_text"}
    de_mas = {clave for r in raw_repos for clave in r} - permitidos
    assert not de_mas, f"Campos que no van en el snapshot: {sorted(de_mas)}"


def test_ids_unicos(raw_repos):
    for campo in ("full_name", "github_id"):
        valores = [r[campo] for r in raw_repos]
        assert len(valores) == len(set(valores)), f"{campo} repetido"


def test_readmes_sin_huerfanos(raw_repos):
    # Un README puede faltar (el contrato lo permite), pero no puede sobrar.
    esperados = {readme_path(r["full_name"]).name for r in raw_repos}
    huerfanos = {p.name for p in README_DIR.glob("*.md")} - esperados
    assert not huerfanos, f"README sin repo en repos.json: {sorted(huerfanos)}"


def test_ordenados_por_full_name(raw_repos):
    nombres = [r["full_name"] for r in raw_repos]
    assert nombres == sorted(nombres)


def test_meta_tiene_solo_las_claves_acordadas(meta):
    assert set(meta) == META_KEYS


def fila(full_name: str, github_id: int, **cambios) -> dict:
    """Una fila como la devuelve la vista, con lo mínimo que exige Repo."""
    base = {
        "full_name": full_name,
        "github_id": github_id,
        "stargazers_count": 10,
        "pushed_at": "2026-10-01T00:00:00Z",
        "archived": False,
        "name": "columna-extra",   # la vista trae columnas que el contrato ignora
    }
    return {**base, **cambios}


def test_validate_devuelve_los_repos():
    repos = validate([fila("a/uno", 1), fila("b/dos", 2)])
    assert [r.full_name for r in repos] == ["a/uno", "b/dos"]


@pytest.mark.parametrize(
    "filas",
    [
        [fila("a/uno", 1, stargazers_count=-5)],   # no cumple el contrato
        [fila("a/uno", 1), fila("a/uno", 2)],      # full_name repetido
        [fila("a/uno", 1), fila("b/dos", 1)],      # github_id repetido
        [],                                         # la vista no devolvió filas
    ],
)
def test_validate_termina_si_algo_falla(filas):
    with pytest.raises(SystemExit):
        validate(filas)


def test_compare_columns():
    columnas = sorted(INGESTION_FIELDS - {"open_issues_count"}) + ["name"]
    assert compare_columns(columnas) == {
        "ignored_columns": ["name"],
        "missing_fields": ["open_issues_count"],
    }


def test_redact_quita_el_host():
    url = "postgresql://usuario:clave@db.ejemplo.test:5432/postgres"
    mensaje = 'connection to server at "db.ejemplo.test" failed'
    assert redact(mensaje, url) == 'connection to server at "<host>" failed'
