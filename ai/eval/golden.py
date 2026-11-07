"""Golden set de la búsqueda: consultas con los repos que deberían aparecer.

Cada golden set declara el catálogo contra el que se escribió (`source`). La
evaluación construye el índice con ese mismo origen.
    catalog  search_queries_catalog.json  catálogo real (snapshot)
    sample   search_queries.json          20 repos de ejemplo
"""

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ai.catalog import Source

EVAL_DIR = Path(__file__).resolve().parent

GoldenName = Literal["catalog", "catalog-validation", "sample"]
DEFAULT_GOLDEN: GoldenName = "catalog"
GOLDEN_FILES: dict[str, Path] = {
    "catalog": EVAL_DIR / "search_queries_catalog.json",
    # Consultas nuevas para validar el texto de búsqueda elegido con "catalog"; no se usan para ajustarlo.
    "catalog-validation": EVAL_DIR / "search_queries_catalog_validation.json",
    "sample": EVAL_DIR / "search_queries.json",
}
# Nombre del reporte de cada golden set. El de los datos de ejemplo conserva su
# nombre original para regenerarse en el mismo archivo.
REPORT_PREFIX: dict[str, str] = {"catalog": "search-catalog",
                                 "catalog-validation": "search-catalog-validation",
                                 "sample": "search"}


class SearchQuery(BaseModel):
    """Una consulta y los repos aceptables".

    `expected` vacío significa que el catálogo no tiene respuesta.
    """
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    expected: list[str]
    pair: str | None = None
    note: str = Field(min_length=1)

    @property
    def answerable(self) -> bool:
        return bool(self.expected)


class SearchGoldenSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    source: Source                              # catálogo contra el que se escribió
    catalog_taken_at: datetime | None = None    # fecha del snapshot, si source es "snapshot"
    queries: list[SearchQuery]


def load_search_queries(name: GoldenName = DEFAULT_GOLDEN) -> SearchGoldenSet:
    """Carga y valida un golden set.

    Lanza `ValueError` si el nombre no existe y `ValidationError` si el archivo no cumple.
    """
    if name not in GOLDEN_FILES:
        raise ValueError(f"El golden set {name!r} no existe; opciones: {', '.join(GOLDEN_FILES)}")
    return SearchGoldenSet.model_validate_json(GOLDEN_FILES[name].read_bytes())
