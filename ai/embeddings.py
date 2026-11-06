"""Embeddings de texto con un modelo local, en CPU.

El modelo se elige con la variable de entorno AI_EMBEDDING_MODEL
(por defecto, qwen3). Solo este archivo sabe qué modelo se usa.
Cambiar el modelo obliga a recalcular los vectores de todo el catálogo.
"""

import os
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import torch
from huggingface_hub.errors import GatedRepoError
from sentence_transformers import SentenceTransformer


@dataclass(frozen=True)
class ModelSpec:
    """Modelo de embeddings y como usarlo"""

    name: str                       # id en Hugging Face
    query_prompt: str               # se antepone a la consulta
    document_prompt: str = ""       # se antepone a cada documento
    left_padding: bool = False
    min_score: float | None = None  # umbral de no_evidence


QWEN3_INSTRUCTION  = (
    "Given a description of a software project or business need, "
    "retrieve open-source tools that fit it"
)

MODELS = {"qwen3": ModelSpec(name="Qwen/Qwen3-Embedding-0.6B",
                             # Instrucción en inglés en la consulta, como recomienda el modelo.
                             query_prompt=f"Instruct: {QWEN3_INSTRUCTION}\nQuery:",
                             left_padding=True,),
          "embeddinggemma": ModelSpec(name="google/embeddinggemma-300m",
                                      # Formatos de su ficha. Requiere aceptar licencia HF
                                      query_prompt="task: search result | query: ",
                                      document_prompt="title: none | text: ",
                                      # Calibrado con ai/eval (catálogo real, 100 repos, texto
                                      # con resumen y casos de uso de la IA, 100 consultas).
                                      # Cambiar el texto de los repos obliga a recalibrarlo.
                                      min_score=0.23),
}
DEFAULT_MODEL = "embeddinggemma"


def model_spec() -> ModelSpec:
    """El modelo elegido con AI_EMBEDDING_MODEL."""
    key = os.environ.get("AI_EMBEDDING_MODEL", DEFAULT_MODEL)
    if key not in MODELS:
        raise ValueError(f"AI_EMBEDDING_MODEL={key!r} no existe; opciones: {', '.join(MODELS)}")
    return MODELS[key]


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    """Carga el modelo la primera vez; luego reutiliza el mismo."""
    spec = model_spec()
    try:
        # float32: en CPU, bfloat16 (default) es lento e impreciso.
        return SentenceTransformer(
            spec.name,
            processor_kwargs={"padding_side": "left"} if spec.left_padding else {},
            model_kwargs={"dtype": torch.float32},
        )
    except GatedRepoError as err:
        raise RuntimeError(
            f"{spec.name} requiere aceptar su licencia en Hugging Face y un token de lectura "
            "(hf auth login). Pasos en ai/README.md, sección 'Modelo de embeddings'."
        ) from err


def embed_documents(texts: list[str]) -> np.ndarray:
    """Vectores de los documentos normalizados: (len(texts), 1024)."""
    return _model().encode(texts,
                           prompt=model_spec().document_prompt or None,
                           normalize_embeddings=True,
                           convert_to_numpy=True)


def embed_query(text: str) -> np.ndarray:
    """Vector de una consulta normalizado: (dimensión del modelo,)."""
    return _model().encode(text,
                           prompt=model_spec().query_prompt,
                           normalize_embeddings=True,
                           convert_to_numpy=True
    )
