"""Pruebas del coordinador con extractor y motores simulados (sin red ni SQL)."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent / "src"))
sys.path.insert(0, str(TESTS_DIR.parent / "scripts"))

from hash_contract import HASH_VERSION  # noqa: E402
from sync_config import (  # noqa: E402
    WRITES_ENABLED_ENV,
    WRITE_CONFIRMATION_ENV,
)
from sync_doubles import (  # noqa: E402
    FakeCatalogEngine,
    FakeFetcher,
    record,
    repo_row,
    stored_row,
)
from sync_load import SYNC_WRITE_CONFIRMATION  # noqa: E402
import update_catalog  # noqa: E402

TARGET_ENV = "OPENBRIDGE_SYNC_TARGET"
BASE_ENV = {
    "OPENBRIDGE_SUPABASE_DB_HOST": "aws-0-us-east-1.pooler.supabase.com",
    "OPENBRIDGE_SUPABASE_DB_PORT": "5432",
    "OPENBRIDGE_SUPABASE_DB_NAME": "postgres",
    "OPENBRIDGE_SUPABASE_DB_USER": "openbridge_ai_writer",
    "OPENBRIDGE_SUPABASE_DB_PASSWORD": "password-de-prueba",
}
WRITE_ENV = {
    **BASE_ENV,
    WRITES_ENABLED_ENV: "1",
    WRITE_CONFIRMATION_ENV: SYNC_WRITE_CONFIRMATION,
}


class EngineFactory:
    def __init__(self, engine):
        self.engine = engine
        self.calls = []

    def __call__(self, target, *, read_only=True):
        self.calls.append({"target": target, "read_only": read_only})
        return self.engine


def write_approved(tmp_path, *names):
    path = tmp_path / "approved.txt"
    path.write_text("\n".join(names) + "\n", encoding="utf-8")
    return str(path)


def run(argv, *, environ, fetcher=None, engine=None, tmp_path=None):
    factory = EngineFactory(engine if engine is not None else FakeCatalogEngine())
    code = update_catalog.run(
        argv,
        environ=environ,
        fetcher=fetcher if fetcher is not None else FakeFetcher([]),
        engine_factory=factory,
    )
    return code, factory


def test_offline_mode_makes_no_http_or_sql(capsys):
    fetcher = FakeFetcher([record()])
    code, factory = run([], environ={}, fetcher=fetcher)
    assert code == update_catalog.EXIT_OK
    assert fetcher.calls == []
    assert factory.calls == []
    assert "0 solicitudes HTTP" in capsys.readouterr().out


def test_dry_run_prints_plan_and_never_writes(tmp_path, capsys):
    engine = FakeCatalogEngine()
    summary = tmp_path / "resumen.md"
    fetcher = FakeFetcher([record()])
    code, factory = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
            "--summary-file",
            str(summary),
        ],
        environ=BASE_ENV,
        fetcher=fetcher,
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_OK
    assert [call["read_only"] for call in factory.calls] == [True]
    assert engine.repos == {}
    assert engine.readmes == {}
    assert not any(
        sql.startswith(("INSERT", "UPDATE", "DELETE"))
        for sql in engine.statements()
    )
    assert "0 escrituras ejecutadas (dry-run)" in output
    assert "INSERT repositorios" not in output
    saved = summary.read_text(encoding="utf-8")
    assert "Resumen" not in saved or "INSERT=1" in saved
    assert "0 escrituras ejecutadas" in saved


def test_dry_run_without_database_comparison_exits_warnings(tmp_path, capsys):
    fetcher = FakeFetcher([record()])
    code, factory = run(
        [
            "--live",
            "--skip-db",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ={},
        fetcher=fetcher,
        engine=None,
    )
    assert code == update_catalog.EXIT_WARNINGS
    assert factory.calls == []
    assert "OMITIDA" in capsys.readouterr().out


def test_dry_run_without_credentials_skips_database(tmp_path, capsys):
    code, factory = run(
        [
            "--live",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ={},
        fetcher=FakeFetcher([record()]),
    )
    assert code == update_catalog.EXIT_WARNINGS
    assert factory.calls == []
    assert "OMITIDA" in capsys.readouterr().out


def test_apply_without_authorization_is_blocked(tmp_path, capsys):
    fetcher = FakeFetcher([record()])
    code, factory = run(
        [
            "--live",
            "--apply",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=BASE_ENV,
        fetcher=fetcher,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WRITE_BLOCKED
    assert fetcher.calls == []
    assert factory.calls == []
    assert "ESCRITURA BLOQUEADA" in output


def test_apply_with_authorization_applies_and_verifies(tmp_path, capsys):
    engine = FakeCatalogEngine()
    code, factory = run(
        [
            "--live",
            "--apply",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_OK
    assert [call["read_only"] for call in factory.calls] == [True, False, True]
    assert engine.repos[42]["content_hash_version"] == HASH_VERSION
    assert engine.readmes[42] == "# README\n"
    assert "INSERT repositorios=1" in output
    assert "Verificación posterior: hashes y READMEs coinciden" in output


def test_dry_run_plans_legacy_backfill_without_writing(tmp_path, capsys):
    repo = repo_row()
    legacy = stored_row(repo, version=None, content_hash="0" * 64)
    engine = FakeCatalogEngine({42: legacy}, {42: "# README\n"})
    code, factory = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_OK
    assert [call["read_only"] for call in factory.calls] == [True]
    assert engine.repos[42]["content_hash_version"] is None
    assert engine.repos[42]["content_hash"] == "0" * 64
    assert "Hashes históricos sin versión a recalcular con openbridge-ai-v1: 1" in output
    assert "0 escrituras ejecutadas (dry-run)" in output


def test_apply_backfills_legacy_hash_and_version(tmp_path, capsys):
    repo = repo_row()
    legacy = stored_row(repo, version=None, content_hash="0" * 64)
    engine = FakeCatalogEngine({42: legacy}, {42: "# README\n"})
    code, factory = run(
        [
            "--live",
            "--apply",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_OK
    assert [call["read_only"] for call in factory.calls] == [True, False, True]
    assert engine.repos[42]["content_hash_version"] == HASH_VERSION
    assert engine.repos[42]["content_hash"] != "0" * 64
    assert len(engine.repos[42]["content_hash"]) == 64
    assert "backfill de hash=1" in output
    assert "Verificación posterior: hashes y READMEs coinciden" in output


def test_dry_run_preserves_legacy_hash_when_readme_is_unresolved(tmp_path, capsys):
    repo = repo_row()
    legacy = stored_row(repo, version=None, content_hash="0" * 64)
    engine = FakeCatalogEngine({42: legacy}, {42: "# README\n"})
    code, _ = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record(status="ERROR_HTTP")]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WARNINGS
    assert "a recalcular con openbridge-ai-v1" not in output
    assert "README no verificable" in output
    assert engine.repos[42]["content_hash_version"] is None


def test_incomplete_extraction_exits_warnings(tmp_path, capsys):
    engine = FakeCatalogEngine()
    code, _ = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto", "example/pendiente"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WARNINGS
    assert "Faltan repositorios aprobados: example/pendiente" in output
    assert "Completitud: INCOMPLETA" in output


def test_approved_list_rejects_duplicates(tmp_path, capsys):
    path = tmp_path / "approved.txt"
    path.write_text("example/proyecto\nExample/Proyecto\n", encoding="utf-8")
    fetcher = FakeFetcher([record()])
    code, factory = run(
        ["--live", "--repositories", str(path)],
        environ={},
        fetcher=fetcher,
    )
    assert code == update_catalog.EXIT_USAGE
    assert fetcher.calls == []
    assert factory.calls == []
    assert "duplicado" in capsys.readouterr().out


def test_secrets_never_appear_in_output_or_summary(tmp_path, capsys):
    token = "ghp_super_secreto_token"
    summary = tmp_path / "resumen.md"
    env = {**BASE_ENV, "GITHUB_TOKEN": token}
    code, _ = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
            "--summary-file",
            str(summary),
        ],
        environ=env,
        fetcher=FakeFetcher([record()]),
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_OK
    assert token not in output
    assert BASE_ENV["OPENBRIDGE_SUPABASE_DB_PASSWORD"] not in output
    saved = summary.read_text(encoding="utf-8")
    assert token not in saved
    assert BASE_ENV["OPENBRIDGE_SUPABASE_DB_PASSWORD"] not in saved


def test_transform_failure_aborts_before_database(tmp_path, capsys):
    code, factory = run(
        [
            "--live",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record(status="PENDIENTE")]),
    )
    assert code == update_catalog.EXIT_ERROR
    assert factory.calls == []
    assert "ERROR de transformación" in capsys.readouterr().out


def test_extraction_error_returns_error_without_database(tmp_path, capsys):
    code, factory = run(
        [
            "--live",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record()], error=RuntimeError("fallo de red simulado")),
    )
    assert code == update_catalog.EXIT_ERROR
    assert factory.calls == []
    assert "ERROR de extracción" in capsys.readouterr().out


def test_limit_processes_only_the_approved_prefix(tmp_path):
    fetcher = FakeFetcher([record()])
    code, _ = run(
        [
            "--live",
            "--skip-db",
            "--limit",
            "1",
            "--repositories",
            write_approved(tmp_path, "example/proyecto", "example/segundo"),
        ],
        environ={},
        fetcher=fetcher,
    )
    assert code == update_catalog.EXIT_WARNINGS
    assert fetcher.calls[0]["slugs"] == ("example/proyecto",)


def test_apply_with_skip_db_is_rejected(capsys):
    code, factory = run(["--live", "--apply", "--skip-db"], environ={})
    assert code == update_catalog.EXIT_USAGE
    assert factory.calls == []
    assert "--skip-db" in capsys.readouterr().out


def test_apply_rejects_admin_database_user(tmp_path, capsys):
    env = {**WRITE_ENV, "OPENBRIDGE_SUPABASE_DB_USER": "postgres.proyecto"}
    code, factory = run(
        [
            "--live",
            "--apply",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto"),
        ],
        environ=env,
        fetcher=FakeFetcher([record()]),
    )
    assert code == update_catalog.EXIT_USAGE
    assert factory.calls == []
    assert "destino válido" in capsys.readouterr().out
