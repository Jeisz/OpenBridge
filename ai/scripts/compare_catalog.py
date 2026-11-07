"""Compara el catálogo de la vista con lo que tiene la IA. Solo lee: no escribe nada.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.compare_catalog

Lee public.v_repos_for_ai y lo publicado por la IA (ai.ai_processing) con el usuario lector
(AI_READER_DATABASE_URL en .env). Compara la vista con lo publicado (¿sigue al día?) y con el
snapshot (ai/data/catalog/, la copia de los archivos). Qué compara: ver ai/catalog_diff.py.

Código de salida: 0 sin diferencias, 1 con diferencias, 2 si no pudo comparar.
"""

import os
import sys

import psycopg
from dotenv import load_dotenv

from ai.catalog import load_repos
from ai.catalog_diff import CatalogDiff, diff_catalog, with_unix_newlines
from ai.published import fetch_published
from ai.scripts.export_catalog_snapshot import (ENV_VAR, SOURCE, compare_columns, fetch_rows,
                                                redact, validate)
from shared.contracts.repo import Repo

NO_CHANGES, CHANGES, FAILED = 0, 1, 2


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(FAILED)


def read_view() -> tuple[list[Repo], list[str]]:
    """Repos de la vista, validados contra Repo, y los nombres de sus columnas."""
    load_dotenv()
    url = os.environ.get(ENV_VAR)
    if not url:
        fail(f"Falta {ENV_VAR} en .env (ver .env.example)")
    try:
        rows, columns = fetch_rows(url)
    except psycopg.Error as e:
        fail(f"No se pudo leer {SOURCE}: {redact(str(e), url)}")
    try:
        repos = validate(rows)          # termina el programa si una fila no cumple Repo
    except SystemExit as e:
        fail(str(e.code))
    return [with_unix_newlines(r) for r in repos], columns


def read_published() -> dict[str, dict[int, dict]]:
    """Lo publicado por la IA en la base, por tipo de dato (ver ai/published.py)."""
    load_dotenv()
    url = os.environ.get(ENV_VAR)
    if not url:
        fail(f"Falta {ENV_VAR} en .env (ver .env.example)")
    try:
        return fetch_published(url)
    except psycopg.Error as e:
        fail(f"No se pudo leer lo publicado por la IA: {redact(str(e), url)}")


SHOWN = 10   # nombres por línea: más que esto no se lee, y el conteo ya dice cuántos son


def _some(items: list[str], sep: str = ", ") -> str:
    """Los primeros SHOWN elementos y, si hay más, cuántos faltan."""
    rest = len(items) - SHOWN
    return sep.join(items[:SHOWN]) + (f"{sep}y {rest} más" if rest > 0 else "")


def _names(repos: list[Repo]) -> str:
    return _some([r.full_name for r in repos])


def report(diff: CatalogDiff, live: int, known: int) -> str:
    """Texto para leer: un conteo por clase y, si hay, los repos."""
    lines = [f"Vista: {live} repos · copia en archivos (snapshot): {known} repos",
             "Datos de la IA comparados con lo publicado en la base"]

    def add(label: str, count: int, detail: str = "") -> None:
        lines.append(f"{label}: {count}" + (f" → {detail}" if count else ""))

    add("Nuevos", len(diff.new), _names(diff.new))
    add("Ya no están en la vista", len(diff.removed), _names(diff.removed))
    add("Mismo repo con otro nombre", len(diff.renamed),
        _some([f"{a.full_name} → {b.full_name}" for a, b in diff.renamed]))
    add("Cambió archived", len(diff.archived_changed), _names(diff.archived_changed))
    for label, stale in (("Enriquecimiento por actualizar", diff.enrichment_stale),
                         ("Ideas por actualizar", diff.ideas_stale)):
        add(label, len(stale), _some([f"{r.full_name} ({why})" for r, why in stale], "; "))
    for table, ids in diff.orphans.items():
        add(f"Datos de la IA sin repo en la vista ({table})", len(ids), _some(list(map(str, ids))))
    lines.append("Campos que cambiaron (repos por campo): "
                 + (", ".join(f"{k} {v}" for k, v in diff.field_changes.items()) or "ninguno"))
    lines.append("Resultado: " + ("hay diferencias" if diff.has_changes else "sin diferencias"))
    return "\n".join(lines)


def main() -> None:
    live, columns = read_view()
    published = read_published()
    try:
        known = load_repos("snapshot")
    except (OSError, ValueError) as e:      # ValueError incluye JSON inválido y ValidationError
        fail(f"No se pudo leer la copia del catálogo: {e}")
    diff = diff_catalog(live, known, published["enrichment"], published["ideas"])
    print(report(diff, len(live), len(known)))
    missing = compare_columns(columns)["missing_fields"]
    print("Campos del contrato que la vista no trae:", ", ".join(missing) or "ninguno")
    sys.exit(CHANGES if diff.has_changes else NO_CHANGES)


if __name__ == "__main__":
    main()
