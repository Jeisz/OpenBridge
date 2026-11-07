"""Búsqueda semántica sobre el catálogo de repos."""

import hashlib
from collections.abc import Collection
from typing import Literal

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

# Partes del texto que vienen de la IA. Sin ninguna: nombre, descripción y topics.
TextField = Literal["categories", "summary", "use_cases"]
# Las que usa la búsqueda. Sin categorías (medido en ai/eval/SEARCH_DECISION.md).
TEXT_FIELDS: tuple[TextField, ...] = ("summary", "use_cases")

# Variantes para medir (python -m ai.eval.run_search_eval --texto). Las cuatro primeras
# forman una cadena: cada una suma un dato de la IA a la anterior.
TEXT_VARIANTS: dict[str, tuple[TextField, ...]] = {
    "base": (),
    "categorias": ("categories",),
    "resumen": ("categories", "summary"),
    "casos": ("categories", "summary", "use_cases"),
    # Sin la descripción genérica de la categoría, que acerca consultas sin respuesta.
    "sin-categorias": ("summary", "use_cases"),
}


def clean_topics(topics: list[str]) -> list[str]:
    """Topics sin los de `NOISE_TOPICS`, en su orden original."""
    return [t for t in topics if t not in NOISE_TOPICS]


def build_embedding_text(repo: Repo, categories: dict[str, Category],
                         fields: tuple[TextField, ...] = TEXT_FIELDS) -> str:
    """Texto que representa el repo en la búsqueda.

    Orden: nombre -> categorías -> resumen -> descripción -> topics -> casos de uso.
    `fields` elige qué partes de la IA entran; las que faltan en el repo se omiten.
    """
    parts = [repo.full_name.split("/")[1] + "."]

    if "categories" in fields:
        for assignment in repo.categories:
            category = categories[assignment.category_id]
            parts.append(f"{category.name}: {category.description}")

    if "summary" in fields and repo.summary_es:
        parts.append(_sentence(repo.summary_es))

    description = (repo.description or "").strip()
    if description:
        parts.append(_sentence(description))

    topics = clean_topics(repo.topics)
    if topics:
        parts.append("Topics: " + ", ".join(topics) + ".")

    if "use_cases" in fields and repo.use_cases:
        parts.append("Usos: " + "; ".join(repo.use_cases) + ".")

    return " ".join(parts)


def embedding_hash(text: str, model: str, document_prompt: str = "") -> str:
    """Huella de un vector: el texto del repo, el modelo y el prompt con que se calcula.

    Si cambia cualquiera de los tres (por ejemplo, un resumen nuevo publicado), el vector
    guardado deja de servir.
    """
    content = "\n".join((model, document_prompt, text))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def plan_vectors(repos: list[Repo], stored: dict[int, dict],
                 fields: tuple[TextField, ...] = TEXT_FIELDS
                 ) -> tuple[dict[int, np.ndarray], list[tuple[Repo, str, str]]]:
    """Qué vectores guardados sirven y cuáles hay que calcular. No carga el modelo.

    stored: vectores guardados por github_id, con model, ai_input_hash y embedding (lista).
    Devuelve (vectores que sirven por github_id, [(repo, texto, huella)] por calcular).
    """
    from ai import embeddings   # solo model_spec(): no carga el modelo

    spec = embeddings.model_spec()
    categories = load_categories()
    reuse: dict[int, np.ndarray] = {}
    missing: list[tuple[Repo, str, str]] = []
    for repo in repos:
        text = build_embedding_text(repo, categories, fields)
        fingerprint = embedding_hash(text, spec.name, spec.document_prompt)
        saved = stored.get(repo.github_id)
        if (saved and saved["model"] == spec.name and saved["ai_input_hash"] == fingerprint
                and len(saved["embedding"]) == spec.dims):
            reuse[repo.github_id] = np.asarray(saved["embedding"], dtype=np.float32)
        else:
            missing.append((repo, text, fingerprint))
    return reuse, missing


def _sentence(text: str) -> str:
    """El texto sin espacios en los extremos y terminado en punto."""
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else text + "."


class SearchResult(BaseModel):
    """Un repo encontrado, con su similitud y sus advertencias."""

    repo: Repo
    score: float                # similitud coseno con la consulta
    license_unconfirmed: bool   # licencia NOASSERTION o ausente
    health_unknown: bool        # sin health_score


class SearchIndex:
    """Repos del catálogo y sus vectores, alineados: la fila i es el repo i."""

    def __init__(self, repos: list[Repo], vectors: np.ndarray, reused: int = 0):
        if len(repos) != len(vectors):
            raise ValueError(f"{len(repos)} repos y {len(vectors)} vectores")
        self.repos = repos
        self.vectors = vectors
        self.reused = reused                    # vectores guardados que sirvieron
        self.computed = len(repos) - reused     # vectores calculados al construir el índice

    @classmethod
    def build(cls, source: Source = DEFAULT_SOURCE,
              fields: tuple[TextField, ...] = TEXT_FIELDS) -> "SearchIndex":
        """Carga el catálogo del origen elegido y calcula sus vectores con el modelo.

        `fields`: partes de la IA que entran al texto (para medir variantes).
        """
        return cls.from_repos(load_repos(source), fields)

    @classmethod
    def from_repos(cls, repos: list[Repo], fields: tuple[TextField, ...] = TEXT_FIELDS,
                   stored: dict[int, dict] | None = None) -> "SearchIndex":
        """Índice de repos ya cargados (de los archivos o de la base).

        stored: vectores guardados (ver `plan_vectors`); los que siguen al día se reutilizan y
        solo se calculan los demás. Sin stored, se calculan todos.
        """
        reuse, missing = plan_vectors(repos, stored or {}, fields)
        computed: dict[int, np.ndarray] = {}
        if missing:
            from ai import embeddings   # carga el modelo (torch) solo si hay algo que calcular
            vectors = embeddings.embed_documents([text for _, text, _ in missing])
            computed = {repo.github_id: v for (repo, _, _), v in zip(missing, vectors)}
        rows = [reuse.get(r.github_id, computed.get(r.github_id)) for r in repos]
        return cls(repos, np.vstack(rows) if rows else np.empty((0, 0)), reused=len(reuse))

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
    if repo.archived or repo.disabled:
        return False    # archivado o deshabilitado por GitHub: no se recomienda nunca.
                        # disabled = None (sin dato) no excluye.
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


