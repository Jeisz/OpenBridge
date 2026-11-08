"""Pruebas de las compuertas de escritura del coordinador (sin red ni SQL).

Cubren ``--require-complete``, ``--max-writes`` y ``--fail-on-incomplete``:
deben impedir la escritura o cambiar el código de salida sin abrir conexiones
de escritura ni modificar el catálogo.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent / "src"))
sys.path.insert(0, str(TESTS_DIR.parent / "scripts"))

from sync_config import (  # noqa: E402
    WRITES_ENABLED_ENV,
    WRITE_CONFIRMATION_ENV,
)
from sync_doubles import (  # noqa: E402
    FakeCatalogEngine,
    FakeFetcher,
    record,
)
from sync_load import SYNC_WRITE_CONFIRMATION  # noqa: E402
import update_catalog  # noqa: E402

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


def run(argv, *, environ, fetcher, engine=None):
    factory = EngineFactory(engine if engine is not None else FakeCatalogEngine())
    code = update_catalog.run(
        argv,
        environ=environ,
        fetcher=fetcher,
        engine_factory=factory,
    )
    return code, factory


def apply_argv(tmp_path, *extra):
    return [
        "--live",
        "--apply",
        "--target",
        "supabase",
        "--repositories",
        write_approved(tmp_path, "example/proyecto", "example/segundo"),
        *extra,
    ]


def test_require_complete_blocks_apply_on_partial_plan(tmp_path, capsys):
    engine = FakeCatalogEngine()
    code, factory = run(
        apply_argv(tmp_path, "--require-complete"),
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WRITE_BLOCKED
    assert [call["read_only"] for call in factory.calls] == [True]
    assert not any(
        sql.startswith(("INSERT", "UPDATE", "DELETE")) for sql in engine.statements()
    )
    assert engine.repos == {}
    assert "ESCRITURA BLOQUEADA" in output
    assert "--require-complete" in output


def test_require_complete_allows_complete_plan(tmp_path, capsys):
    engine = FakeCatalogEngine()
    code, factory = run(
        apply_argv(tmp_path, "--require-complete"),
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record(), record(identifier=7, name="segundo")]),
        engine=engine,
    )
    assert code == update_catalog.EXIT_OK
    assert [call["read_only"] for call in factory.calls] == [True, False, True]
    assert sorted(engine.repos) == [7, 42]
    assert "Aplicado" in capsys.readouterr().out


def test_apply_with_incomplete_plan_stays_allowed_without_flag(tmp_path):
    """Compatibilidad: sin la bandera el comportamiento previo no cambia."""
    engine = FakeCatalogEngine()
    code, _ = run(
        apply_argv(tmp_path),
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    assert code == update_catalog.EXIT_WARNINGS
    assert sorted(engine.repos) == [42]


def test_max_writes_blocks_apply_when_plan_exceeds_limit(tmp_path, capsys):
    engine = FakeCatalogEngine()
    code, factory = run(
        apply_argv(tmp_path, "--max-writes", "1"),
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record(), record(identifier=7, name="segundo")]),
        engine=engine,
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WRITE_BLOCKED
    assert not any(
        sql.startswith(("INSERT", "UPDATE", "DELETE")) for sql in engine.statements()
    )
    assert engine.repos == {}
    assert "--max-writes 1" in output


def test_max_writes_allows_plan_within_limit(tmp_path):
    engine = FakeCatalogEngine()
    code, _ = run(
        apply_argv(tmp_path, "--max-writes", "2"),
        environ=WRITE_ENV,
        fetcher=FakeFetcher([record(), record(identifier=7, name="segundo")]),
        engine=engine,
    )
    assert code == update_catalog.EXIT_OK
    assert sorted(engine.repos) == [7, 42]


def test_max_writes_must_be_positive():
    with pytest.raises(SystemExit) as error:
        update_catalog.run(["--live", "--max-writes", "0"], environ={})
    assert error.value.code == 2


def test_fail_on_incomplete_returns_error_in_dry_run(tmp_path, capsys):
    engine = FakeCatalogEngine()
    code, factory = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--fail-on-incomplete",
            "--repositories",
            write_approved(tmp_path, "example/proyecto", "example/segundo"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record()]),
        engine=engine,
    )
    assert code == update_catalog.EXIT_ERROR
    assert [call["read_only"] for call in factory.calls] == [True]
    assert engine.repos == {}
    assert "Completitud: INCOMPLETA" in capsys.readouterr().out


def test_incomplete_dry_run_keeps_warning_code_without_flag(tmp_path):
    code, _ = run(
        [
            "--live",
            "--dry-run",
            "--target",
            "supabase",
            "--repositories",
            write_approved(tmp_path, "example/proyecto", "example/segundo"),
        ],
        environ=BASE_ENV,
        fetcher=FakeFetcher([record()]),
    )
    assert code == update_catalog.EXIT_WARNINGS
