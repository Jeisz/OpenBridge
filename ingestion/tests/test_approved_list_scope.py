"""Cobertura de la lista aprobada por defecto frente al catálogo publicado.

Solo lectura: no accede a GitHub, a PostgreSQL ni al sistema de archivos fuera
del repositorio.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parents[1]
sys.path.insert(0, str(TESTS_DIR.parent / "src"))

from sync_config import load_approved_repositories  # noqa: E402

SNAPSHOT = REPO_ROOT / "ai" / "data" / "catalog" / "repos.json"
LEGACY_LIST = REPO_ROOT / "ingestion" / "approved_repositories_100_verified.txt"


def test_default_approved_list_covers_the_127_snapshot_repositories():
    approved = load_approved_repositories()
    assert len(approved) == 127
    assert len({name.casefold() for name in approved}) == 127

    rows = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert len(rows) == 127
    published = {row["full_name"].casefold() for row in rows}
    assert published <= {name.casefold() for name in approved}


def test_default_approved_list_keeps_the_100_verified_entries():
    approved = {name.casefold() for name in load_approved_repositories()}
    legacy = [
        line.strip()
        for line in LEGACY_LIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(legacy) == 100
    assert {name.casefold() for name in legacy} <= approved
