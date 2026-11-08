"""Pruebas del preflight de cuota ``GET /rate_limit`` (sin red ni SQL).

Verifican el parseo del sondeo, la decisión de capacidad y que el coordinador
omita la extracción cuando la cuota no alcanza, sin abrir conexiones de base.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest
import requests

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent / "src"))
sys.path.insert(0, str(TESTS_DIR.parent / "scripts"))

from extract_github import (  # noqa: E402
    RATE_LIMIT_ENDPOINT,
    RATE_LIMIT_HEADROOM,
    REQUESTS_PER_REPOSITORY,
    RateLimitSnapshot,
    check_rate_limit_capacity,
    estimate_required_requests,
    fetch_rate_limit,
)
from sync_config import (  # noqa: E402
    WRITES_ENABLED_ENV,
    WRITE_CONFIRMATION_ENV,
)
from sync_doubles import FakeCatalogEngine, FakeFetcher, record  # noqa: E402
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


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        if self.payload is None:
            raise ValueError("respuesta sin JSON")
        return self.payload


class SpyGetter:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        if self.error is not None:
            raise self.error
        return self.response


class SpyProbe:
    """Sustituto de ``fetch_rate_limit`` inyectado en el coordinador."""

    def __init__(self, snapshot=None, error=None):
        self.snapshot = snapshot
        self.error = error
        self.calls = []

    def __call__(self, *, enabled=False, token=None):
        self.calls.append({"enabled": enabled, "token": token})
        if self.error is not None:
            raise self.error
        return self.snapshot


class EngineFactory:
    def __init__(self, engine):
        self.engine = engine
        self.calls = []

    def __call__(self, target, *, read_only=True):
        self.calls.append({"target": target, "read_only": read_only})
        return self.engine


def payload(remaining, limit=5000, reset=1760000000):
    return {
        "resources": {
            "core": {"remaining": remaining, "limit": limit, "reset": reset}
        }
    }


def write_approved(tmp_path, *names):
    path = tmp_path / "approved.txt"
    path.write_text("\n".join(names) + "\n", encoding="utf-8")
    return str(path)


def run(argv, *, environ, fetcher, probe, engine=None):
    factory = EngineFactory(engine if engine is not None else FakeCatalogEngine())
    code = update_catalog.run(
        argv,
        environ=environ,
        fetcher=fetcher,
        engine_factory=factory,
        rate_limit_fetcher=probe,
    )
    return code, factory


def preflight_argv(tmp_path, *extra):
    return [
        "--live",
        "--dry-run",
        "--target",
        "supabase",
        "--preflight-rate-limit",
        "--repositories",
        write_approved(tmp_path, "example/proyecto", "example/segundo"),
        *extra,
    ]


def test_rate_limit_disabled_makes_no_request():
    getter = SpyGetter(FakeResponse(payload=payload(5000)))
    snapshot = fetch_rate_limit(enabled=False, http_get=getter, token="tok")
    assert getter.calls == []
    assert snapshot.consulted is False


def test_rate_limit_parses_core_resource_without_leaking_token():
    token = "ghp_token_super_secreto"
    getter = SpyGetter(FakeResponse(payload=payload(4200)))
    snapshot = fetch_rate_limit(enabled=True, http_get=getter, token=token)
    assert snapshot == RateLimitSnapshot(
        remaining=4200, limit=5000, reset_epoch=1760000000.0, consulted=True
    )
    call = getter.calls[0]
    assert call["url"] == RATE_LIMIT_ENDPOINT
    assert token not in call["url"]
    assert call["headers"]["Authorization"] == f"Bearer {token}"
    assert call["allow_redirects"] is False


def test_rate_limit_non_200_is_not_consulted():
    getter = SpyGetter(FakeResponse(status_code=500, payload=payload(0)))
    snapshot = fetch_rate_limit(enabled=True, http_get=getter, token=None)
    assert snapshot.consulted is False
    assert snapshot.remaining is None


def test_rate_limit_network_error_is_not_consulted():
    getter = SpyGetter(error=requests.exceptions.ConnectionError("sin red"))
    snapshot = fetch_rate_limit(enabled=True, http_get=getter, token=None)
    assert snapshot.consulted is False


def test_rate_limit_payload_without_core_is_consulted():
    getter = SpyGetter(FakeResponse(payload={"resources": {}}))
    snapshot = fetch_rate_limit(enabled=True, http_get=getter, token=None)
    assert snapshot.consulted is True
    assert snapshot.remaining is None


def test_estimate_required_requests_counts_metadata_and_readme():
    assert REQUESTS_PER_REPOSITORY == 2
    assert estimate_required_requests(100) == 200
    assert estimate_required_requests(0) == 0


def test_estimate_required_requests_rejects_negative():
    with pytest.raises(ValueError):
        estimate_required_requests(-1)


def test_capacity_rejects_insufficient_quota():
    problem = check_rate_limit_capacity(
        RateLimitSnapshot(remaining=100, limit=5000, consulted=True), 200
    )
    assert problem is not None
    assert "insuficiente" in problem


def test_capacity_respects_headroom():
    tight = RateLimitSnapshot(remaining=RATE_LIMIT_HEADROOM - 1, consulted=True)
    enough = RateLimitSnapshot(remaining=RATE_LIMIT_HEADROOM, consulted=True)
    assert check_rate_limit_capacity(tight, 200) is not None
    assert check_rate_limit_capacity(enough, 200) is None


def test_capacity_ignores_unconsulted_snapshot():
    assert check_rate_limit_capacity(RateLimitSnapshot(), 200) is None


def test_capacity_flags_uninterpretable_response():
    problem = check_rate_limit_capacity(
        RateLimitSnapshot(remaining=None, consulted=True), 200
    )
    assert problem is not None
    assert "sin cuota restante interpretable" in problem


def test_preflight_aborts_before_extraction_when_quota_is_low(tmp_path, capsys):
    fetcher = FakeFetcher([record()])
    probe = SpyProbe(RateLimitSnapshot(remaining=10, limit=5000, consulted=True))
    code, factory = run(
        preflight_argv(tmp_path), environ=BASE_ENV, fetcher=fetcher, probe=probe
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WARNINGS
    assert fetcher.calls == []
    assert factory.calls == []
    assert probe.calls == [{"enabled": True, "token": None}]
    assert "Cuota restante: 10" in output
    assert "Extracción: OMITIDA" in output


def test_preflight_continues_when_quota_is_sufficient(tmp_path, capsys):
    fetcher = FakeFetcher([record()])
    probe = SpyProbe(RateLimitSnapshot(remaining=5000, limit=5000, consulted=True))
    code, _ = run(
        preflight_argv(tmp_path), environ=BASE_ENV, fetcher=fetcher, probe=probe
    )
    assert code == update_catalog.EXIT_WARNINGS
    assert len(fetcher.calls) == 1
    assert "Cuota verificada: 5000" in capsys.readouterr().out


def test_preflight_error_degrades_to_previous_behaviour(tmp_path, capsys):
    fetcher = FakeFetcher([record()])
    probe = SpyProbe(error=RuntimeError("sondeo roto"))
    code, _ = run(
        preflight_argv(tmp_path), environ=BASE_ENV, fetcher=fetcher, probe=probe
    )
    output = capsys.readouterr().out
    assert code == update_catalog.EXIT_WARNINGS
    assert len(fetcher.calls) == 1
    assert "ADVERTENCIA: no se pudo consultar /rate_limit" in output
    assert "RuntimeError" in output


def test_preflight_without_flag_does_not_probe(tmp_path):
    fetcher = FakeFetcher([record()])
    probe = SpyProbe(error=AssertionError("no debería sondearse"))
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
        fetcher=fetcher,
        probe=probe,
    )
    assert code == update_catalog.EXIT_OK
    assert probe.calls == []


def test_preflight_blocks_apply_when_require_complete(tmp_path):
    fetcher = FakeFetcher([record()])
    probe = SpyProbe(RateLimitSnapshot(remaining=10, limit=5000, consulted=True))
    code, factory = run(
        [
            "--live",
            "--apply",
            "--target",
            "supabase",
            "--preflight-rate-limit",
            "--require-complete",
            "--repositories",
            write_approved(tmp_path, "example/proyecto", "example/segundo"),
        ],
        environ=WRITE_ENV,
        fetcher=fetcher,
        probe=probe,
    )
    assert code == update_catalog.EXIT_WRITE_BLOCKED
    assert fetcher.calls == []
    assert factory.calls == []


def test_probe_failure_never_allows_writing_an_incomplete_plan(tmp_path, capsys):
    """Un /rate_limit inaccesible degrada el sondeo, no la compuerta del plan."""
    engine = FakeCatalogEngine()
    fetcher = FakeFetcher([record()])
    probe = SpyProbe(error=RuntimeError("sondeo roto"))
    code, factory = run(
        [
            "--live",
            "--apply",
            "--target",
            "supabase",
            "--preflight-rate-limit",
            "--require-complete",
            "--repositories",
            write_approved(tmp_path, "example/proyecto", "example/segundo"),
        ],
        environ=WRITE_ENV,
        fetcher=fetcher,
        probe=probe,
        engine=engine,
    )
    output = capsys.readouterr().out
    assert probe.calls == [{"enabled": True, "token": None}]
    assert len(fetcher.calls) == 1
    assert code == update_catalog.EXIT_WRITE_BLOCKED
    assert [call["read_only"] for call in factory.calls] == [True]
    assert not any(
        sql.startswith(("INSERT", "UPDATE", "DELETE")) for sql in engine.statements()
    )
    assert engine.repos == {}
    assert "ESCRITURA BLOQUEADA" in output
