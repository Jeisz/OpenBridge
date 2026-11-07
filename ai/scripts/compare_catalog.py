"""Compara el catálogo de la vista con lo que tiene la IA. Solo lee: no escribe nada.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.compare_catalog

Lee public.v_repos_for_ai con el usuario lector (AI_READER_DATABASE_URL en .env) y la
compara con el snapshot (ai/data/catalog/) y con los datos de la IA (enrichment.json,
ideas.json). Qué compara: ver ai/catalog_diff.py.

Código de salida: 0 sin diferencias, 1 con diferencias, 2 si no pudo comparar.
"""

import os
import sys

import psycopg
from dotenv import load_dotenv

from ai.catalog import ENRICHMENT_FILE, load_repos
from ai.catalog_diff import CatalogDiff, diff_catalog, with_unix_newlines
from ai.scripts.batch import load_records
from ai.scripts.export_catalog_snapshot import (ENV_VAR, SOURCE, compare_columns, fetch_rows,
                                                redact, validate)
from ai.scripts.generate_ideas import OUT_FILE as IDEAS_FILE
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


def _names(repos: list[Repo]) -> str:
    return ", ".join(r.full_name for r in repos)


def report(diff: CatalogDiff, live: int, known: int) -> str:
    """Texto para leer: un conteo por clase y, si hay, los repos."""
    lines = [f"Vista: {live} repos · catálogo de la IA (snapshot): {known} repos"]

    def add(label: str, count: int, detail: str = "") -> None:
        lines.append(f"{label}: {count}" + (f" → {detail}" if count else ""))

    add("Nuevos", len(diff.new), _names(diff.new))
    add("Ya no están en la vista", len(diff.removed), _names(diff.removed))
    add("Mismo repo con otro nombre", len(diff.renamed),
        ", ".join(f"{a.full_name} → {b.full_name}" for a, b in diff.renamed))
    add("Cambió archived", len(diff.archived_changed), _names(diff.archived_changed))
    for label, stale in (("Enriquecimiento por actualizar", diff.enrichment_stale),
                         ("Ideas por actualizar", diff.ideas_stale)):
        add(label, len(stale), "; ".join(f"{r.full_name} ({why})" for r, why in stale))
    for table, ids in diff.orphans.items():
        add(f"Datos de la IA sin repo en la vista ({table})", len(ids), ", ".join(map(str, ids)))
    lines.append("Campos que cambiaron (repos por campo): "
                 + (", ".join(f"{k} {v}" for k, v in diff.field_changes.items()) or "ninguno"))
    lines.append("Resultado: " + ("hay diferencias" if diff.has_changes else "sin diferencias"))
    return "\n".join(lines)


def main() -> None:
    live, columns = read_view()
    try:
        known = load_repos("snapshot")
        enrichment, ideas = load_records(ENRICHMENT_FILE), load_records(IDEAS_FILE)
    except (OSError, ValueError) as e:      # ValueError incluye JSON inválido y ValidationError
        fail(f"No se pudo leer lo que tiene la IA: {e}")
    diff = diff_catalog(live, known, enrichment, ideas)
    print(report(diff, len(live), len(known)))
    missing = compare_columns(columns)["missing_fields"]
    print("Campos del contrato que la vista no trae:", ", ".join(missing) or "ninguno")
    sys.exit(CHANGES if diff.has_changes else NO_CHANGES)


if __name__ == "__main__":
    main()
