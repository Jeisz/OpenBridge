"""Búsqueda semántica sobre el catálogo de repos."""

from collections.abc import Collection

import numpy as np
from pydantic import BaseModel

from ai.catalog import DEFAULT_SOURCE, Source, load_categories, load_repos
from shared.contracts.repo import Category, Repo

# Topics de ruido que no describen qué hace un repo: campañas, etiquetas
# de GitHub o que se comparten con todos los repos del catálogo.
NOISE_TOPICS = frozenset({
    "hacktoberfest",
    "beginner-friendly",
    "featured",
    "works-with-react",
    "example",
    "open-source",
})

# Licencias que no se pueden confirmar
UNCONFIRMED_LICENSES = frozenset({None, "NOASSERTION"})


def clean_topics(topics: list[str]) -> list[str]:
    """Topics sin los de `NOISE_TOPICS`, en su orden original."""
    return [t for t in topics if t not in NOISE_TOPICS]


def build_embedding_text(repo: Repo, categories: dict[str, Category]) -> str:
    """Texto que representa el repo en la búsqueda.

    Orden: nombre -> categorías -> descripción -> topics.
    Si el repo no tiene descripción, se omite esa parte.
    """
    parts = [repo.full_name.split("/")[1] + "."]

    for assignment in repo.categories:
        category = categories[assignment.category_id]
        parts.append(f"{category.name}: {category.description}")

    description = (repo.description or "").strip()
    if description:
        if not description.endswith((".", "!", "?")):
            description += "."
        parts.append(description)

    topics = clean_topics(repo.topics)
    if topics:
        parts.append("Topics: " + ", ".join(topics) + ".")

    return " ".join(parts)


class SearchResult(BaseModel):
    """Un repo encontrado, con su similitud y sus advertencias."""

    repo: Repo
    score: float                # similitud coseno con la consulta
    license_unconfirmed: bool   # licencia NOASSERTION o ausente
    health_unknown: bool        # sin health_score


class SearchIndex:
    """Repos del catálogo y sus vectores, alineados: la fila i es el repo i."""

    def __init__(self, repos: list[Repo], vectors: np.ndarray):
        if len(repos) != len(vectors):
            raise ValueError(f"{len(repos)} repos y {len(vectors)} vectores")
        self.repos = repos
        self.vectors = vectors

    @classmethod
    def build(cls, source: Source = DEFAULT_SOURCE) -> "SearchIndex":
        """Carga el catálogo del origen elegido y calcula sus vectores con el modelo."""
        from ai import embeddings   # Se importa aquí por torch

        repos = load_repos(source)
        categories = load_categories()
        texts = [build_embedding_text(r, categories) for r in repos]
        return cls(repos, embeddings.embed_documents(texts))

    def search(self,
               query: str,
               k: int = 5,
               *,
               licenses: Collection[str] | None = None,
               min_health: float | None = None,
               categories: Collection[str] | None = None,) -> list[SearchResult]:
        """Los k repos más parecidos a la consulta que pasan los filtros"""
        from ai import embeddings

        return self.search_vector(embeddings.embed_query(query),
                                  k,
                                  licenses=licenses,
                                  min_health=min_health,
                                  categories=categories,)

    def search_vector(self,
                      query_vector: np.ndarray,
                      k: int = 5,
                      *,
                      licenses: Collection[str] | None = None,
                      min_health: float | None = None,
                      categories: Collection[str] | None = None,) -> list[SearchResult]:
        """Como `search`, pero con la consulta ya convertida en vector."""
        if k < 1:
            raise ValueError("k debe ser al menos 1")

        keep = [
            i for i, repo in enumerate(self.repos)
            if _passes(repo, licenses, min_health, categories)
        ]
        if not keep:
            return []

        scores = self.vectors[keep] @ query_vector
        order = np.argsort(-scores, kind="stable")[:k]
        return [_to_result(self.repos[keep[j]], float(scores[j])) for j in order]


def _passes(repo: Repo,
            licenses: Collection[str] | None,
            min_health: float | None,
            categories: Collection[str] | None,) -> bool:
    """True si el repo pasa todos los filtros"""
    if repo.archived:
        return False    # repo archivado no se recomienda
    if licenses is not None and repo.license_spdx_id not in licenses:
        return False    # NOASSERTION o None no confirman ninguna licencia.
    if min_health is not None and repo.health_score is not None and repo.health_score < min_health:
        return False    # Sin health_score pasa
    if categories is not None and not any(a.category_id in categories for a in repo.categories):
        return False
    return True


def _to_result(repo: Repo, score: float) -> SearchResult:
    return SearchResult(repo=repo,
                        score=score,
                        license_unconfirmed=repo.license_spdx_id in UNCONFIRMED_LICENSES,
                        health_unknown=repo.health_score is None,)


