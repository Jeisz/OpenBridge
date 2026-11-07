"""Carga los repos del catálogo, validados segun el contrato `Repo`
(shared/contracts/repo.py)

Punto de acceso único a los datos. Aqui se puede cambiar el origen de
los datos. Dos orígenes:
    snapshot  ai/data/catalog/  copia del catálogo real (por defecto)
    sample    ai/data/          20 repos de ejemplo con categorías asignadas a mano
"""

import json
from pathlib import Path
from typing import Literal

from shared.contracts.repo import Repo, Category, CategoryList

Source = Literal["snapshot", "sample"]
DEFAULT_SOURCE: Source = "snapshot"

DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE_DIRS: dict[str, Path] = {
    "snapshot": DATA_DIR / "catalog",
    "sample": DATA_DIR,
}
CATEGORIES_FILE = Path(__file__).resolve().parents[1] / "shared" / "contracts" / "categories.json"
ENRICHMENT_FILE = SOURCE_DIRS["snapshot"] / "enrichment.json"  # lo escribe ai.scripts.enrich_catalog


def source_dir(source: Source = DEFAULT_SOURCE) -> Path:
    """Carpeta de un origen. Lanza `ValueError` si el origen no existe."""
    if source not in SOURCE_DIRS:
        raise ValueError(f"El origen {source!r} no existe; opciones: {', '.join(SOURCE_DIRS)}")
    return SOURCE_DIRS[source]


def repos_file(source: Source = DEFAULT_SOURCE) -> Path:
    """Ruta de repos.json de un origen."""
    return source_dir(source) / "repos.json"


def readme_dir(source: Source = DEFAULT_SOURCE) -> Path:
    """Carpeta de los README de un origen."""
    return source_dir(source) / "readmes"


def readme_file(full_name: str, source: Source = DEFAULT_SOURCE) -> Path:
    """Ruta del README de un repo."""
    return readme_dir(source) / f"{full_name.replace('/', '__')}.md"


def load_raw(source: Source = DEFAULT_SOURCE) -> list[dict]:
    """Contenido de repos.json tal cual, sin validar y sin README."""
    return json.loads(repos_file(source).read_text(encoding="utf-8"))


def load_repos(source: Source = DEFAULT_SOURCE) -> list[Repo]:
    """Devuelve los repos del catálogo con su README, validados contra `Repo`.

    Si un repo no cumple el contrato, lanza `pydantic.ValidationError`
    Si un repo no tiene archivo de README, queda con readme_text = None.
    """
    repos = []
    for raw in load_raw(source):
        path = readme_file(raw["full_name"], source)
        # read_text convierte saltos de línea de Windows para que el texto
        # quede igual en cualquier sistema operativo.
        readme = path.read_text(encoding="utf-8") if path.is_file() else None
        repos.append(Repo.model_validate({**raw, "readme_text": readme}))
    return repos


def load_categories() -> dict[str, Category]:
    """Devuelve las categorías por `id`

    Arroja `pydantic.ValidationError` si el archivo no cumple `CategoryList`.
    """
    data = CategoryList.model_validate_json(CATEGORIES_FILE.read_bytes())
    return {c.id: c for c in data.categories}
