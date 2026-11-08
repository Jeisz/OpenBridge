"""Pruebas sin red ni PostgreSQL: simulan una transacción completa."""
from __future__ import annotations

import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hash_contract import HASH_VERSION
from load import (CatalogSnapshot, LoadPlanError, WRITE_CONFIRMATION,
                  insert_new_batch, prepare_write_batch)
from transform import TransformationResult


class Result:
    def __init__(self, rows=None, scalar=None):
        self.rows = rows or []
        self.scalar = scalar
    def mappings(self):
        return self
    def all(self):
        return self.rows
    def scalar_one(self):
        return self.scalar
    def scalar_one_or_none(self):
        return self.scalar


class FakeEngine:
    def __init__(self, existing=None, readmes=None, db="openbridge_db", version=True):
        self.repos = dict(existing or {})
        self.readmes = dict(readmes or {})
        self.db, self.version = db, version
        self.calls = []
        self.begin_calls = 0
        self.fail_readme_for = None
        self.rollback_count = 0

    def begin(self):
        engine = self
        class Context:
            def __enter__(self):
                engine.begin_calls += 1
                self.previous_repos = copy.deepcopy(engine.repos)
                self.previous_readmes = copy.deepcopy(engine.readmes)
                return engine
            def __exit__(self, exc_type, exc, tb):
                if exc_type is not None:
                    engine.repos = self.previous_repos
                    engine.readmes = self.previous_readmes
                    engine.rollback_count += 1
                return False
        return Context()

    def execute(self, statement, params=None):
        statement = " ".join(str(statement).split())
        self.calls.append((statement, params))
        if statement == "SELECT current_database()":
            return Result(scalar=self.db)
        if "information_schema.columns" in statement:
            return Result(scalar=1 if self.version else 0)
        if statement == "SELECT github_id, full_name FROM public.catalog_repositories":
            return Result(rows=[{"github_id": k, "full_name": v["full_name"]} for k,v in self.repos.items()])
        if statement == "SELECT github_id FROM public.catalog_readmes":
            return Result(rows=[{"github_id": k} for k in self.readmes])
        if statement == "SELECT full_name FROM public.catalog_repositories WHERE github_id = :github_id":
            actual = self.repos.get(params["github_id"])
            return Result(scalar=actual["full_name"] if actual else None)
        if statement.startswith("INSERT INTO public.catalog_repositories"):
            assert "ON CONFLICT (github_id) DO NOTHING" in statement
            identifier = params["github_id"]
            if identifier in self.repos:
                return Result(scalar=None)
            self.repos[identifier] = dict(params)
            return Result(scalar=identifier)
        if statement.startswith("INSERT INTO public.catalog_readmes"):
            identifier = params["github_id"]
            if identifier == self.fail_readme_for:
                raise RuntimeError("Fallo simulado en inserción README")
            if identifier in self.readmes:
                return Result(scalar=None)
            self.readmes[identifier] = params["readme_text"]
            return Result(scalar=identifier)
        raise AssertionError(f"SQL no esperado: {statement}")


def repo(identifier, name="nuevo"):
    return {
        "github_id": identifier,
        "full_name": f"org/{name}", "name": name,
        "description": "demo", "homepage": None, "language": "Python",
        "topics": ["data", "etl"], "stargazers_count": 11,
        "forks_count": 3, "pushed_at": "2026-10-20T16:00:00Z",
        "archived": False, "license_spdx_id": "MIT",
    }


def transformed(*identifiers, with_readme=True):
    repos = [repo(i, f"repo{i}") for i in identifiers]
    readmes = ([{"github_id": i, "readme_text": f"# README {i}"} for i in identifiers]
               if with_readme else [])
    obs = ([] if with_readme else
           [{"full_name": f"org/repo{i}", "readme_status": "NO_ENCONTRADO"} for i in identifiers])
    return TransformationResult(repos, readmes, obs)


def prepared(*identifiers, with_readme=True, snapshot=None):
    return prepare_write_batch(transformed(*identifiers, with_readme=with_readme),
                               snapshot or CatalogSnapshot({}, frozenset()))


def test_prepare_is_pure_and_v1():
    p = prepared(6, 7)
    assert len(p.repositories) == 2
    assert set(p.hashes_by_id) == {6, 7}
    assert all(h.content_hash_version == HASH_VERSION for h in p.hashes_by_id.values())


def test_prepare_preserves_existing():
    p = prepared(5, 6, snapshot=CatalogSnapshot({5: "org/repo5"}, frozenset({5})))
    assert [r["github_id"] for r in p.repositories] == [6]
    assert p.preserved_repositories == 1 and p.preserved_readmes == 1


def test_authorization_required_before_connection():
    db = FakeEngine()
    with pytest.raises(PermissionError):
        insert_new_batch(db, prepared(6))
    assert db.begin_calls == 0


def test_wrong_database_name_blocks_before_connection():
    db = FakeEngine()
    with pytest.raises(LoadPlanError, match="Nombre de base"):
        insert_new_batch(db, prepared(6), authorization=WRITE_CONFIRMATION, expected_database="otra")
    assert db.begin_calls == 0


def test_connected_to_wrong_database_rolls_back():
    db = FakeEngine(db="otra")
    with pytest.raises(LoadPlanError, match="inesperada"):
        insert_new_batch(db, prepared(6), authorization=WRITE_CONFIRMATION)
    assert db.repos == {} and db.rollback_count == 1


def test_missing_migration_blocks_all_inserts():
    db = FakeEngine(version=False)
    with pytest.raises(LoadPlanError, match="migración"):
        insert_new_batch(db, prepared(6), authorization=WRITE_CONFIRMATION)
    assert db.repos == {} and not any(sql.startswith("INSERT") for sql,_ in db.calls)


def test_inserts_only_new_with_hash_and_topics_pg_array():
    db = FakeEngine(existing={5: {"full_name": "org/repo5", "content_hash": "ORIGINAL"}},
                    readmes={5: "# ANTERIOR"})
    p = prepared(5, 6, snapshot=CatalogSnapshot({5: "org/repo5"}, frozenset({5})))
    summary = insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    assert (summary.inserted_repositories, summary.inserted_readmes) == (1, 1)
    assert db.repos[5]["content_hash"] == "ORIGINAL" and db.readmes[5] == "# ANTERIOR"
    assert db.repos[6]["content_hash_version"] == HASH_VERSION
    assert db.repos[6]["topics"] == ["data", "etl"]
    assert db.readmes[6] == "# README 6"
    assert not any(" UPDATE " in f" {sql} " or " DELETE " in f" {sql} " for sql,_ in db.calls)


def test_repeat_batch_idempotent():
    db = FakeEngine()
    p = prepared(6, 7)
    first = insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    second = insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    assert (first.inserted_repositories, first.inserted_readmes) == (2, 2)
    assert (second.inserted_repositories, second.inserted_readmes, second.skipped_existing) == (0, 0, 2)
    assert len(db.repos) == 2 and len(db.readmes) == 2


def test_rollback_on_readme_failure():
    db = FakeEngine()
    db.fail_readme_for = 7
    with pytest.raises(RuntimeError, match="Fallo simulado"):
        insert_new_batch(db, prepared(6, 7), authorization=WRITE_CONFIRMATION)
    assert db.repos == {} and db.readmes == {} and db.rollback_count == 1


def test_collision_on_id_is_blocked():
    db = FakeEngine(existing={6: {"full_name": "otro/nombre"}})
    with pytest.raises(LoadPlanError, match="github_id"):
        insert_new_batch(db, prepared(6), authorization=WRITE_CONFIRMATION)
    assert len(db.repos) == 1


def test_collision_on_fullname_is_blocked():
    db = FakeEngine(existing={999: {"full_name": "org/repo6"}})
    with pytest.raises(LoadPlanError, match="full_name"):
        insert_new_batch(db, prepared(6), authorization=WRITE_CONFIRMATION)
    assert len(db.repos) == 1


def test_prepare_rejects_existing_identity_conflict():
    with pytest.raises(LoadPlanError, match="identidad"):
        prepared(6, snapshot=CatalogSnapshot({6: "otro/nombre"}, frozenset()))


def test_prepare_rejects_fullname_collision():
    with pytest.raises(LoadPlanError, match="full_name"):
        prepared(6, snapshot=CatalogSnapshot({99: "org/repo6"}, frozenset()))


def test_tampered_hash_is_blocked_before_connection():
    p = prepared(6)
    # Dataclass frozen, mapa mutable: la escritura debe revalidar sus valores.
    from dataclasses import replace
    p = replace(p, hashes_by_id={6: replace(p.hashes_by_id[6], content_hash="a" * 64)})
    db = FakeEngine()
    with pytest.raises(LoadPlanError, match="Hash v1"):
        insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    assert db.begin_calls == 0


def test_tampered_readme_is_blocked_before_connection():
    p = prepared(6)
    p.readmes_by_id[6] = "HACK"
    db = FakeEngine()
    with pytest.raises(LoadPlanError, match="Hash v1"):
        insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    assert db.begin_calls == 0


def test_confirmed_404_is_supported_without_readme_insert():
    db = FakeEngine()
    p = prepared(6, with_readme=False)
    summary = insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    assert summary.inserted_repositories == 1 and summary.inserted_readmes == 0
    assert db.readmes == {} and db.repos[6]["content_hash_version"] == HASH_VERSION


def test_unverified_readme_status_aborts_prepare():
    bad = transformed(6, with_readme=False)
    bad.observations[0]["readme_status"] = "ERROR_HTTP"
    with pytest.raises(ValueError, match="README no verificable"):
        prepare_write_batch(bad, CatalogSnapshot({}, frozenset()))


def test_cli_default_still_offline(monkeypatch):
    from load import main
    monkeypatch.setattr(sys, "argv", ["load.py"])
    assert main() == 0


def test_repo_metadata_mutation_blocked_before_connection():
    p = prepared(6)
    p.repositories[0]["stargazers_count"] += 1
    db = FakeEngine()
    with pytest.raises(LoadPlanError, match="Hash v1"):
        insert_new_batch(db, p, authorization=WRITE_CONFIRMATION)
    assert db.begin_calls == 0


def test_exact_openbridge_five_existing_five_new_scenario():
    historic = {i: {"full_name": f"org/repo{i}", "content_hash": f"LEGACY-{i}"}
                for i in range(1, 6)}
    historic_readmes = {i: f"# Historic README {i}" for i in range(1, 6)}
    db = FakeEngine(existing=historic, readmes=historic_readmes)
    snap = CatalogSnapshot({i: f"org/repo{i}" for i in range(1, 6)},
                           frozenset(range(1, 6)))
    batch = prepared(*range(1, 11), snapshot=snap)
    assert len(batch.repositories) == 5 and batch.preserved_repositories == 5
    first = insert_new_batch(db, batch, authorization=WRITE_CONFIRMATION)
    second = insert_new_batch(db, batch, authorization=WRITE_CONFIRMATION)
    assert (first.inserted_repositories, first.inserted_readmes) == (5, 5)
    assert (second.inserted_repositories, second.inserted_readmes) == (0, 0)
    assert len(db.repos) == 10 and len(db.readmes) == 10
    for identifier in range(1, 6):
        assert db.repos[identifier]["content_hash"] == f"LEGACY-{identifier}"
        assert db.readmes[identifier] == f"# Historic README {identifier}"
