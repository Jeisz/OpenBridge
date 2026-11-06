"""Valida elección de origen de datos de catalog.py."""

from typing import get_args

import pytest

from ai import catalog
from ai.scripts.export_catalog_snapshot import README_DIR as SNAPSHOT_README_DIR
from ai.scripts.export_catalog_snapshot import REPOS_FILE as SNAPSHOT_REPOS_FILE


def test_por_defecto_lee_donde_escribe_el_export():
    # La carpeta del snapshot está definida en dos archivos. Si se separan,
    # la búsqueda leería un catálogo viejo o vacío sin avisar.
    assert catalog.repos_file() == SNAPSHOT_REPOS_FILE
    assert catalog.readme_dir() == SNAPSHOT_README_DIR


def test_cada_origen_declarado_tiene_carpeta():
    assert set(get_args(catalog.Source)) == set(catalog.SOURCE_DIRS)


def test_origen_desconocido_es_error():
    with pytest.raises(ValueError, match="no existe"):
        catalog.load_raw(source="snapshop")


def test_el_catalogo_real_carga_validado():
    # Valida los repos junto con su README, por el mismo camino que usa la búsqueda.
    assert len(catalog.load_repos()) == len(catalog.load_raw())


def test_el_snapshot_suma_los_datos_de_la_ia():
    enrichment = catalog.load_enrichment()
    assert enrichment, "falta ai/data/catalog/enrichment.json"
    for repo in catalog.load_repos():
        ai_part = enrichment.get(repo.github_id)
        if ai_part is None:
            continue
        assert [c.category_id for c in repo.categories] == [
            c["category_id"] for c in ai_part["categories"]]
        assert all(c.assigned_by == "llm" for c in repo.categories)
        assert repo.summary_es == ai_part["summary_es"]
        assert repo.use_cases == ai_part["use_cases"]


def test_los_repos_de_ejemplo_conservan_sus_categorias_propias():
    sample = catalog.load_repos(source="sample")
    assert all(c.assigned_by == "human" for r in sample for c in r.categories)


def test_sin_archivo_de_la_ia_no_hay_datos_de_la_ia(tmp_path, monkeypatch):
    monkeypatch.setattr(catalog, "ENRICHMENT_FILE", tmp_path / "no-existe.json")
    assert catalog.load_enrichment() == {}
