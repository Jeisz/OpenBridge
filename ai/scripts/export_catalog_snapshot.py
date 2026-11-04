"""Exporta el catálogo de la vista public.v_repos_for_ai a ai/data/catalog/.

Uso desde la raíz del repo con entorno activo:
    python -m ai.scripts.export_catalog_snapshot

AI_READER_DATABASE_URL tiene que estar configurado en .env. Escribe:
    ai/data/catalog/repos.json                  campos de la ingesta, sin el README
    ai/data/catalog/readmes/<owner>__<name>.md  README de cada repo
    ai/data/catalog/meta.json                   cuándo, de dónde y que columnas trajo
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from pydantic import ValidationError

from shared.contracts.repo import Repo

ENV_VAR = "AI_READER_DATABASE_URL"
SOURCE = "public.v_repos_for_ai"
QUERY = f"SELECT * FROM {SOURCE}"
COMMAND = "python -m ai.scripts.export_catalog_snapshot"

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "catalog"
REPOS_FILE = OUT_DIR / "repos.json"
README_DIR = OUT_DIR / "readmes"
META_FILE = OUT_DIR / "meta.json"

# Campos que escribe la IA
AI_FIELDS = {"categories", "use_cases", "summary_es"}
INGESTION_FIELDS = set(Repo.model_fields) - AI_FIELDS


def fetch_rows(url: str) -> tuple[list[dict], list[str]]:
    """Filas de la vista y nombres de sus columnas. En una transacción"""
    with psycopg.connect(url, row_factory=dict_row) as conn:
        conn.read_only = True
        cur = conn.execute(QUERY)
        columns = [col.name for col in cur.description]
        rows = cur.fetchall()
    return rows, columns


def redact(message: str, url: str) -> str:
    """Remueve el host del mensaje de error."""
    host = urlsplit(url).hostname
    return message.replace(host, "<host>") if host else message


def validate(rows: list[dict]) -> list[Repo]:
    """Valida cada fila contra Repo. Si alguna falla, muestra todas y termina."""
    repos, errors = [], []
    for row in rows:
        try:
            repos.append(Repo.model_validate(row))
        except ValidationError as e:
            errors.append(f"- {row.get('full_name', '?')}: {e}")
    if errors:
        sys.exit("Filas que no cumplen el contrato Repo:\n" + "\n".join(errors))
    if not repos:
        sys.exit(f"{SOURCE} no devolvió filas")
    for field in ("full_name", "github_id"):
        values = [getattr(r, field) for r in repos]
        if len(values) != len(set(values)):
            sys.exit(f"Hay valores repetidos de {field} en {SOURCE}")
    return repos


def compare_columns(columns: list[str]) -> dict[str, list[str]]:
    """Columnas de la vista que el contrato ignora y campos de la ingesta que faltan."""
    found = set(columns)
    return {
        "ignored_columns": sorted(found - INGESTION_FIELDS),
        "missing_fields": sorted(INGESTION_FIELDS - found),
    }


def readme_path(full_name: str) -> Path:
    return README_DIR / f"{full_name.replace('/', '__')}.md"


def write_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_snapshot(repos: list[Repo], columns_report: dict[str, list[str]]) -> None:
    repos = sorted(repos, key=lambda r: r.full_name)
    README_DIR.mkdir(parents=True, exist_ok=True)
    for old in README_DIR.glob("*.md"):
        old.unlink()
    for repo in repos:
        if repo.readme_text:
            readme_path(repo.full_name).write_text(repo.readme_text,
                                                   encoding="utf-8",
                                                   newline="\n")

    rows = [r.model_dump(mode="json",
                         exclude=AI_FIELDS | {"readme_text"}) for r in repos]
    write_json(REPOS_FILE, rows)
    write_json(META_FILE, {
        "source": SOURCE,
        "taken_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(repos),
        "command": COMMAND,
        **columns_report,
    })


def main() -> None:
    load_dotenv()
    url = os.environ.get(ENV_VAR)
    if not url:
        sys.exit(f"Falta {ENV_VAR} en .env (ver .env.example)")
    try:
        rows, columns = fetch_rows(url)
    except psycopg.Error as e:
        sys.exit(f"No se pudo leer {SOURCE}: {redact(str(e), url)}")

    repos = validate(rows)
    report = compare_columns(columns)
    write_snapshot(repos, report)

    print(f"{len(repos)} repos -> {OUT_DIR}")
    print("Columnas de la vista que el contrato ignora:",
            ", ".join(report["ignored_columns"]) or "ninguna")
    print("Campos del contrato que la vista no trae:",
            ", ".join(report["missing_fields"]) or "ninguno")


if __name__ == "__main__":
    main()

