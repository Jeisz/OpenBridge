"""Tests de la búsqueda semántica (ai/search.py)

Los de orden filtros usan vectores inventados y no cargan el modelo
Los del modelo real solo corren con AI_MODEL_TESTS=1.
"""

import os

import numpy as np
import pytest

from ai.search import SearchIndex, build_embedding_text, clean_topics
from shared.contracts.repo import Category, Repo

# Consulta y vectores de largo 1. Similitud con QUERY: A=1.0, B=0.8, C=0.6, D=0.0
QUERY = np.array([1.0, 0.0])
A, B, C, D = [1.0, 0.0], [0.8, 0.6], [0.6, 0.8], [0.0, 1.0]

AUTH = {"auth": Category(id="auth", name="Autenticación", description="Login y SSO.",
                         llm_notes="Ej.: Keycloak.")}


def make_repo(name, *, categories=("auth",), license="MIT", health=None,
              archived=False, disabled=None, description=None, topics=()):
    """Repo mínimo válido según el contrato."""
    return Repo.model_validate({
        "full_name": f"test/{name}",
        "github_id": 1,
        "stargazers_count": 0,
        "pushed_at": "2026-01-01T00:00:00Z",
        "archived": archived,
        "disabled": disabled,
        "license_spdx_id": license,
        "health_score": health,
        "description": description,
        "topics": list(topics),
        "categories": [{"category_id": c, "assigned_by": "human"} for c in categories],
    })


def make_index(*pairs):
    """Índice a partir de pares (repo, vector)."""
    repos = [repo for repo, _ in pairs]
    vectors = np.array([vector for _, vector in pairs], dtype=float)
    return SearchIndex(repos, vectors)


def names(results):
    return [r.repo.full_name.split("/")[1] for r in results]


# --- Orden y forma del resultado ---

def test_ordena_por_similitud_y_respeta_k():
    index = make_index((make_repo("c"), C), (make_repo("a"), A), (make_repo("b"), B))
    results = index.search_vector(QUERY, k=2)
    assert names(results) == ["a", "b"]
    assert [r.score for r in results] == pytest.approx([1.0, 0.8])


def test_k_mayor_que_el_catalogo_devuelve_todos():
    index = make_index((make_repo("a"), A), (make_repo("b"), B))
    assert len(index.search_vector(QUERY, k=10)) == 2


def test_k_menor_que_uno_es_error():
    index = make_index((make_repo("a"), A))
    with pytest.raises(ValueError):
        index.search_vector(QUERY, k=0)


def test_repos_y_vectores_desalineados_es_error():
    with pytest.raises(ValueError):
        SearchIndex([make_repo("a")], np.array([A, B]))


def test_lista_vacia_si_nada_pasa_los_filtros():
    index = make_index((make_repo("a", archived=True), A))
    assert index.search_vector(QUERY, k=3) == []


# --- Filtros ---

def test_archivado_nunca_aparece():
    index = make_index((make_repo("a", archived=True), A), (make_repo("b"), B))
    assert names(index.search_vector(QUERY, k=5)) == ["b"]


@pytest.mark.parametrize("disabled, shown", [
    (True, ["b"]),        # deshabilitado por GitHub: nunca aparece
    (False, ["a", "b"]),
    (None, ["a", "b"]),   # sin dato: no se excluye
])
def test_deshabilitado_nunca_aparece_y_sin_dato_si(disabled, shown):
    index = make_index((make_repo("a", disabled=disabled), A), (make_repo("b"), B))
    assert sorted(names(index.search_vector(QUERY, k=5))) == shown


def test_sin_filtro_de_licencia_entran_todas_y_se_marcan():
    index = make_index(
        (make_repo("a", license="NOASSERTION"), A),
        (make_repo("b", license=None), B),
        (make_repo("c", license="MIT"), C),
    )
    results = index.search_vector(QUERY, k=5)
    assert names(results) == ["a", "b", "c"]
    assert [r.license_unconfirmed for r in results] == [True, True, False]


def test_filtro_de_licencia_solo_deja_las_confirmadas():
    index = make_index(
        (make_repo("a", license="NOASSERTION"), A),
        (make_repo("b", license=None), B),
        (make_repo("c", license="MIT"), C),
        (make_repo("d", license="AGPL-3.0"), D),
    )
    assert names(index.search_vector(QUERY, k=5, licenses=["MIT", "Apache-2.0"])) == ["c"]


def test_health_minimo_excluye_bajos_y_deja_pasar_sin_dato():
    index = make_index(
        (make_repo("a", health=40), A),
        (make_repo("b", health=None), B),
        (make_repo("c", health=90), C),
    )
    results = index.search_vector(QUERY, k=5, min_health=60)
    assert names(results) == ["b", "c"]
    assert [r.health_unknown for r in results] == [True, False]


def test_filtro_de_categoria():
    # Los que no pasan van primero en el catálogo: si el código confundiera la
    # posición en la lista filtrada con la del catálogo, devolvería "a" o "b".
    index = make_index(
        (make_repo("a", categories=["auth"]), A),
        (make_repo("b", categories=["auth"]), B),
        (make_repo("c", categories=["payments"]), C),
        (make_repo("d", categories=["database", "payments"]), D),
    )
    results = index.search_vector(QUERY, k=5, categories=["payments"])
    assert names(results) == ["c", "d"]
    assert [r.score for r in results] == pytest.approx([0.6, 0.0])


# --- Texto a embeber ---

def test_clean_topics_quita_ruido_y_conserva_el_orden():
    assert clean_topics(["hacktoberfest", "login", "open-source", "oidc"]) == ["login", "oidc"]


def test_texto_a_embeber():
    repo = make_repo("keycloak", description="Identity management", topics=["hacktoberfest", "oidc"])
    assert build_embedding_text(repo, AUTH) == (
        "keycloak. Autenticación: Login y SSO. Identity management. Topics: oidc."
    )


def test_texto_a_embeber_sin_descripcion():
    assert build_embedding_text(make_repo("x"), AUTH) == "x. Autenticación: Login y SSO."


# --- Con el modelo real (AI_MODEL_TESTS=1) ---

model_tests = pytest.mark.skipif(
    os.environ.get("AI_MODEL_TESTS") != "1",
    reason="usa el modelo real (~1,2 GB); correr con AI_MODEL_TESTS=1",
)


@pytest.fixture(scope="module")
def real_index():
    # Datos de ejemplo. Los que tienen categorías (la prueba de humo busca "auth").
    return SearchIndex.build(source="sample")


@model_tests
def test_humo_consulta_de_login_trae_un_repo_de_auth_en_el_top_3(real_index):
    results = real_index.search("necesito que los clientes de mi app inicien sesión", k=3)
    assert any(a.category_id == "auth" for r in results for a in r.repo.categories)


@model_tests
def test_la_consulta_lleva_instruccion_y_el_documento_no():
    from ai import embeddings

    query = embeddings.embed_query("login")
    document = embeddings.embed_documents(["login"])[0]
    assert not np.allclose(query, document, atol=1e-4)
