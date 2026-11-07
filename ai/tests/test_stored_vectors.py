"""Tests de los vectores guardados: reutilizar los que siguen al día, calcular los demás. Sin modelo."""

import numpy as np
import pytest

from ai import embeddings
from ai.catalog import load_repos
from ai.search import SearchIndex, embedding_hash, plan_vectors

SPEC = embeddings.model_spec()


@pytest.fixture(scope="module")
def repos():
    return load_repos("snapshot")[:5]


@pytest.fixture
def fake_model(monkeypatch):
    """Reemplaza el modelo: cuenta cuántos textos se le piden y devuelve vectores de unos."""
    asked = []
    monkeypatch.setattr(embeddings, "embed_documents",
                        lambda texts: asked.append(list(texts)) or np.ones((len(texts), SPEC.dims),
                                                                         dtype=np.float32))
    return asked


def stored_for(repos, value=0.5):
    """Vectores guardados al día para estos repos (huella correcta)."""
    _, missing = plan_vectors(repos, {})
    return {repo.github_id: {"model": SPEC.name, "ai_input_hash": fingerprint,
                             "embedding": [value] * SPEC.dims}
            for repo, _, fingerprint in missing}


def test_la_huella_cambia_con_el_texto_el_modelo_o_el_prompt():
    base = embedding_hash("texto", "modelo", "prompt")
    assert base == embedding_hash("texto", "modelo", "prompt")
    assert len({base, embedding_hash("otro", "modelo", "prompt"),
                embedding_hash("texto", "otro", "prompt"),
                embedding_hash("texto", "modelo", "otro")}) == 4


def test_vectores_al_dia_se_reutilizan_sin_llamar_al_modelo(repos, fake_model):
    index = SearchIndex.from_repos(repos, stored=stored_for(repos))
    assert fake_model == [] and (index.reused, index.computed) == (len(repos), 0)
    assert np.allclose(index.vectors, 0.5)


def test_solo_se_calculan_los_que_faltan_o_quedaron_viejos(repos, fake_model):
    stored = stored_for(repos)
    del stored[repos[0].github_id]                                  # falta
    stored[repos[1].github_id]["ai_input_hash"] = "huella-vieja"    # el texto cambió
    index = SearchIndex.from_repos(repos, stored=stored)
    assert len(fake_model) == 1 and len(fake_model[0]) == 2
    assert (index.reused, index.computed) == (len(repos) - 2, 2)
    assert np.allclose(index.vectors[0], 1.0) and np.allclose(index.vectors[2], 0.5)


def test_vectores_de_otro_modelo_no_se_usan(repos, fake_model):
    stored = stored_for(repos)
    for saved in stored.values():
        saved["model"] = "otro/modelo"
    index = SearchIndex.from_repos(repos, stored=stored)
    assert index.computed == len(repos)


def test_un_resumen_nuevo_deja_viejo_el_vector(repos):
    # El texto de búsqueda incluye el resumen de la IA: publicar uno nuevo cambia la huella.
    stored = stored_for(repos)
    changed = [repos[0].model_copy(update={"summary_es": "Resumen nuevo publicado."})] + repos[1:]
    _, missing = plan_vectors(changed, stored)
    assert [repo.github_id for repo, _, _ in missing] == [repos[0].github_id]


def test_leer_la_configuracion_del_modelo_no_carga_el_modelo(repos):
    # plan_vectors solo usa model_spec(): el plan del comando de actualización no carga torch.
    embeddings._model.cache_clear()
    plan_vectors(repos, {})
    assert embeddings._model.cache_info().currsize == 0
