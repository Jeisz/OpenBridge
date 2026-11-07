"""Tests del catálogo publicado que lee el servicio: sin base (filas simuladas)."""

import pytest
from pydantic import ValidationError

from ai.catalog import load_enrichment, load_repos
from ai.published import compose_repos


@pytest.fixture(scope="module")
def rows():
    """Las filas que devolverían la vista y las tablas de la IA para el snapshot del repo."""
    repos = load_repos("snapshot")
    view = [r.model_dump(mode="json", exclude={"categories", "summary_es", "use_cases"})
            for r in repos]
    enrichment, categories = [], []
    for github_id, part in load_enrichment().items():
        enrichment.append({"github_id": github_id, "summary_es": part["summary_es"],
                           "use_cases": part["use_cases"]})
        categories += [{"github_id": github_id, **c} for c in part["categories"]]
    return repos, view, enrichment, categories


def test_la_base_y_los_archivos_dan_el_mismo_catalogo(rows):
    # Con los mismos datos publicados, el asistente ve lo mismo leyendo la base o los archivos.
    repos, view, enrichment, categories = rows
    assert compose_repos(view, enrichment, categories) == repos


def test_conserva_quien_asigno_cada_categoria_y_su_orden(rows):
    repos, view, enrichment, categories = rows
    github_id = categories[0]["github_id"]
    mine = [c for c in categories if c["github_id"] == github_id]
    edited = [dict(c, assigned_by="human") if c is mine[0] else c for c in categories]
    repo = next(r for r in compose_repos(view, enrichment, edited) if r.github_id == github_id)
    assert repo.categories[0].assigned_by == "human"
    assert [c.category_id for c in repo.categories] == [c["category_id"] for c in mine]


def test_repo_sin_datos_de_la_ia_queda_con_su_parte_de_la_ingesta(rows):
    _, view, enrichment, categories = rows
    github_id = view[0]["github_id"]
    repo = next(r for r in compose_repos(
        view, [e for e in enrichment if e["github_id"] != github_id],
        [c for c in categories if c["github_id"] != github_id]) if r.github_id == github_id)
    assert repo.summary_es is None and repo.categories == [] and repo.use_cases == []


def test_saltos_de_linea_de_windows_en_el_readme(rows):
    _, view, enrichment, categories = rows
    row = next(r for r in view if r["readme_text"] and "\n" in r["readme_text"])
    windows = [dict(row, readme_text=row["readme_text"].replace("\n", "\r\n"))]
    assert "\r" not in compose_repos(windows, enrichment, categories)[0].readme_text


def test_vista_vacia_o_fila_invalida_es_error(rows):
    _, view, enrichment, categories = rows
    with pytest.raises(ValueError, match="no devolvió"):
        compose_repos([], enrichment, categories)
    with pytest.raises(ValidationError):
        compose_repos([dict(view[0], stargazers_count=-1)], enrichment, categories)
