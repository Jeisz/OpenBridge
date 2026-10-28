"""Dobles de prueba compartidos por las pruebas de sincronización.

Sin red, sin PostgreSQL y sin credenciales reales. Se importan desde los
archivos ``test_sync_*.py`` añadiendo explícitamente este directorio a
``sys.path``.
"""

from __future__ import annotations

import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hash_contract import HASH_VERSION, content_hash_v1  # noqa: E402
from sync_config import DatabaseTarget  # noqa: E402
from transform import TransformationResult  # noqa: E402

_MISSING = object()


class Result:
    def __init__(self, rows=None, scalar=None, rowcount=None):
        self.rows = list(rows or [])
        self.scalar = scalar
        self.rowcount = rowcount

    def mappings(self):
        return self

    def all(self):
        return list(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def scalar_one(self):
        return self.scalar

    def scalar_one_or_none(self):
        return self.scalar


class _Transaction:
    def __init__(self, engine):
        self.engine = engine
        self.repos = None
        self.readmes = None

    def __enter__(self):
        self.engine.begin_calls += 1
        self.repos = copy.deepcopy(self.engine.repos)
        self.readmes = copy.deepcopy(self.engine.readmes)
        return self.engine

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.engine.repos = self.repos
            self.engine.readmes = self.readmes
            self.engine.rollback_count += 1
        return False


class _Connection:
    def __init__(self, engine):
        self.engine = engine

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def begin(self):
        return _Transaction(self.engine)

    def execute(self, statement, params=None):
        return self.engine.execute(statement, params)


class FakeCatalogEngine:
    """Motor SQL simulado: registra SQL, aplica filas y revierte transacciones."""

    def __init__(
        self,
        repos=None,
        readmes=None,
        *,
        database="postgres",
        user="openbridge_ai_writer",
        has_version_column=True,
        fail_readme_for=None,
        readme_alias=None,
    ):
        self.repos = {key: dict(value) for key, value in (repos or {}).items()}
        self.readmes = dict(readmes or {})
        self.database = database
        self.user = user
        self.has_version_column = has_version_column
        self.fail_readme_for = fail_readme_for
        self.readme_alias = dict(readme_alias or {})
        self.calls = []
        self.begin_calls = 0
        self.connect_calls = 0
        self.rollback_count = 0
        self.disposed = False

    def dispose(self):
        self.disposed = True

    def connect(self):
        self.connect_calls += 1
        return _Connection(self)

    def begin(self):
        return _Transaction(self)

    def statements(self):
        return [statement for statement, _ in self.calls]

    def state_rows(self):
        rows = []
        for identifier in sorted(self.repos):
            row = dict(self.repos[identifier])
            row["github_id"] = identifier
            if identifier in self.readmes:
                row["readme_github_id"] = self.readme_alias.get(
                    identifier, identifier
                )
                row["readme_text"] = self.readmes[identifier]
            else:
                row["readme_github_id"] = None
                row["readme_text"] = None
            rows.append(row)
        return rows

    def execute(self, statement, params=None):
        statement = " ".join(str(statement).split())
        self.calls.append((statement, params))
        if statement == "SET TRANSACTION READ ONLY":
            return Result()
        if statement == "SELECT current_database()":
            return Result(scalar=self.database)
        if statement == "SELECT current_user":
            return Result(scalar=self.user)
        if "information_schema.columns" in statement:
            rows = [("content_hash_version",)] if self.has_version_column else []
            return Result(rows=rows)
        if statement.startswith(
            "SELECT github_id FROM public.catalog_repositories "
            "ORDER BY github_id FOR UPDATE"
        ):
            return Result(rows=[{"github_id": key} for key in sorted(self.repos)])
        if statement.startswith("SELECT r.github_id"):
            return Result(rows=self.state_rows())
        if statement.startswith("INSERT INTO public.catalog_repositories"):
            identifier = params["github_id"]
            if identifier in self.repos:
                return Result(scalar=None)
            row = dict(params)
            row.pop("previous_content_hash", None)
            row.pop("previous_content_hash_version", None)
            row["topics"] = "{" + ",".join(params["topics"]) + "}"
            self.repos[identifier] = row
            return Result(scalar=identifier)
        if statement.startswith("UPDATE public.catalog_repositories"):
            identifier = params["github_id"]
            current = self.repos.get(identifier)
            if current is None:
                return Result(rowcount=0)
            if (
                current.get("content_hash") != params["previous_content_hash"]
                or current.get("content_hash_version")
                != params["previous_content_hash_version"]
            ):
                return Result(rowcount=0)
            updated = dict(params)
            updated.pop("previous_content_hash", None)
            updated.pop("previous_content_hash_version", None)
            updated["topics"] = "{" + ",".join(params["topics"]) + "}"
            current.update(updated)
            return Result(rowcount=1)
        if statement.startswith("INSERT INTO public.catalog_readmes"):
            identifier = params["github_id"]
            if identifier == self.fail_readme_for:
                raise RuntimeError("Fallo simulado al escribir el README")
            existing = self.readmes.get(identifier, _MISSING)
            if existing is not _MISSING and existing == params["readme_text"]:
                return Result(rowcount=0)
            self.readmes[identifier] = params["readme_text"]
            return Result(rowcount=1)
        raise AssertionError(f"SQL no esperado: {statement}")


def pg_topics(topics):
    return "{" + ",".join(str(item) for item in topics) + "}"


def repo_row(identifier=42, name="proyecto", **overrides):
    """Fila ya transformada, con los 12 campos del contrato de hash."""
    data = {
        "github_id": identifier,
        "full_name": f"example/{name}",
        "name": name,
        "description": "demo",
        "homepage": None,
        "language": "Python",
        "topics": ["api", "backend"],
        "stargazers_count": 5,
        "forks_count": 1,
        "pushed_at": "2026-10-20T12:30:00Z",
        "archived": False,
        "license_spdx_id": "MIT",
    }
    data.update(overrides)
    return data


def record(identifier=42, name="proyecto", status="DISPONIBLE", readme="# README\n", **overrides):
    """Registro con la forma que devuelve ``extract_github.fetch_repositories``."""
    status = overrides.pop("_readme_status", status)
    readme = overrides.pop("_readme_text", readme)
    data = {
        "id": identifier,
        "full_name": f"example/{name}",
        "name": name,
        "fork": False,
        "archived": False,
        "description": "demo",
        "homepage": None,
        "language": "Python",
        "topics": ["api", "backend"],
        "stargazers_count": 5,
        "forks_count": 1,
        "pushed_at": "2026-10-20T12:30:00Z",
        "license": {"spdx_id": "MIT"},
    }
    data.update(overrides)
    data["_readme_status"] = status
    data["_readme_text"] = readme if status == "DISPONIBLE" else None
    return data


def make_result(repositories, readmes=None, observations=None):
    return TransformationResult(
        list(repositories), list(readmes or []), list(observations or [])
    )


def one_result(repo, readme_text="# README\n"):
    """Resultado de transformación para un solo repositorio."""
    if readme_text is None:
        return make_result(
            [repo],
            [],
            [{"full_name": repo["full_name"], "readme_status": "NO_ENCONTRADO"}],
        )
    return make_result([repo], [{"github_id": repo["github_id"], "readme_text": readme_text}])


def stored_row(
    repo,
    *,
    text="# README\n",
    hash_text=None,
    hash_repo=None,
    content_hash=None,
    version=HASH_VERSION,
    full_name=None,
    topics=None,
    metadata_overrides=None,
):
    """Fila tal como la devolvería la lectura del catálogo."""
    row = dict(repo)
    if full_name is not None:
        row["full_name"] = full_name
    source = repo if hash_repo is None else hash_repo
    text_for_hash = text if hash_text is None else hash_text
    if content_hash is None:
        row["content_hash"] = content_hash_v1(source, text_for_hash)
    else:
        row["content_hash"] = content_hash
    row["content_hash_version"] = version
    row["topics"] = pg_topics(row["topics"]) if topics is None else topics
    if metadata_overrides:
        row.update(metadata_overrides)
    return row


def supabase_target(**overrides):
    data = {
        "name": "supabase",
        "host": "aws-0-us-east-1.pooler.supabase.com",
        "port": 5432,
        "database": "postgres",
        "user": "openbridge_ai_writer",
        "password": "password-de-prueba",
        "sslmode": "require",
        "writes_allowed": True,
    }
    data.update(overrides)
    return DatabaseTarget(**data)


class FakeFetcher:
    """Sustituto de ``fetch_repositories`` sin red."""

    def __init__(self, records=None, audit=None, error=None):
        self.records = [dict(item) for item in (records or [])]
        if audit is None:
            self.audit = [
                {
                    "repository": item.get("full_name"),
                    "stage": "metadata",
                    "success": True,
                    "http_status": 200,
                    "error_type": None,
                    "is_simulated": True,
                }
                for item in self.records
            ]
        else:
            self.audit = [dict(item) for item in audit]
        self.error = error
        self.calls = []

    def __call__(
        self,
        slugs,
        *,
        enabled=False,
        include_readme=True,
        token=None,
        approved_repositories=None,
    ):
        self.calls.append(
            {
                "slugs": tuple(slugs),
                "enabled": enabled,
                "include_readme": include_readme,
                "token": token,
                "approved": tuple(approved_repositories or ()),
            }
        )
        if self.error is not None:
            raise self.error
        return [dict(item) for item in self.records], [
            dict(item) for item in self.audit
        ]
