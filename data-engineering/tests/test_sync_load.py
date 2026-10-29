"""Pruebas offline de la aplicación transaccional del plan (sin PostgreSQL)."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent / "src"))

from hash_contract import HASH_VERSION  # noqa: E402
from load import LoadPlanError  # noqa: E402
from sync_doubles import (  # noqa: E402
    FakeCatalogEngine,
    one_result,
    repo_row,
    stored_row,
    supabase_target,
)
from sync_load import (  # noqa: E402
    SYNC_WRITE_CONFIRMATION,
    apply_sync_plan,
    read_catalog_state,
    verify_sync_result,
)
from sync_plan import (  # noqa: E402
    README_UPDATE,
    CatalogState,
    build_sync_plan,
    validate_plan,
)

TEXT = "# README\n"


def plan_for(repo, engine, readme_text=TEXT):
    result = one_result(repo, readme_text)
    plan = build_sync_plan(
        result, read_catalog_state(engine), approved=(repo["full_name"],)
    )
    validate_plan(plan)
    engine.begin_calls = 0
    engine.calls.clear()
    return plan


def apply(engine, plan, *, target=None, authorization=SYNC_WRITE_CONFIRMATION):
    return apply_sync_plan(
        engine,
        plan,
        target=supabase_target() if target is None else target,
        authorization=authorization,
    )


def test_read_catalog_state_uses_read_only_transaction():
    engine = FakeCatalogEngine()
    state = read_catalog_state(engine)
    assert isinstance(state, CatalogState)
    assert engine.calls[0][0] == "SET TRANSACTION READ ONLY"
    assert engine.connect_calls == 1
    assert engine.begin_calls == 1
    assert not any(
        sql.startswith(("INSERT", "UPDATE", "DELETE"))
        for sql in engine.statements()
    )


def test_read_catalog_state_rejects_orphan_readme():
    repo = repo_row()
    engine = FakeCatalogEngine(
        {repo["github_id"]: stored_row(repo)},
        {repo["github_id"]: TEXT},
        readme_alias={repo["github_id"]: 99},
    )
    with pytest.raises(LoadPlanError, match="huérfano"):
        read_catalog_state(engine)


def test_apply_inserts_new_repository_and_readme():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    summary = apply(engine, plan)
    assert summary.inserted_repositories == 1
    assert summary.inserted_readmes == 1
    assert engine.repos[42]["full_name"] == "example/proyecto"
    assert engine.repos[42]["content_hash_version"] == HASH_VERSION
    assert engine.repos[42]["content_hash"] == plan.actions[0].content_hash
    assert engine.readmes[42] == TEXT
    assert engine.begin_calls == 1


def test_apply_updates_metadata_and_readme():
    repo = repo_row()
    old = dict(repo)
    old["stargazers_count"] = 4
    engine = FakeCatalogEngine({42: stored_row(old, text="# antiguo\n")}, {42: "# antiguo\n"})
    plan = plan_for(repo, engine, "# nuevo\n")
    summary = apply(engine, plan)
    assert summary.updated_repositories == 1
    assert summary.updated_readmes == 1
    assert engine.repos[42]["stargazers_count"] == 5
    assert engine.readmes[42] == "# nuevo\n"
    assert engine.repos[42]["content_hash"] == plan.actions[0].content_hash


def test_apply_repairs_readme_only():
    repo = repo_row()
    engine = FakeCatalogEngine({42: stored_row(repo)}, {42: "# viejo\n"})
    plan = plan_for(repo, engine)
    summary = apply(engine, plan)
    assert summary.updated_repositories == 0
    assert summary.updated_readmes == 1
    assert engine.readmes[42] == TEXT


def test_apply_without_changes_opens_no_transaction():
    repo = repo_row()
    engine = FakeCatalogEngine({42: stored_row(repo)}, {42: TEXT})
    plan = plan_for(repo, engine)
    summary = apply(engine, plan)
    assert engine.begin_calls == 0
    assert engine.calls == []
    assert summary.inserted_repositories == 0
    assert summary.updated_repositories == 0
    assert summary.unchanged_repositories == 1


def test_apply_requires_confirmation_token():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    with pytest.raises(PermissionError, match="confirmación"):
        apply(engine, plan, authorization="otra-cosa")
    assert engine.calls == []
    assert engine.begin_calls == 0


def test_apply_requires_writable_target():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    with pytest.raises(PermissionError, match="habilitado"):
        apply(engine, plan, target=supabase_target(writes_allowed=False))
    assert engine.calls == []


def test_apply_blocks_unexpected_database():
    engine = FakeCatalogEngine(database="openbridge_db")
    plan = plan_for(repo_row(), engine)
    with pytest.raises(LoadPlanError, match="Base de datos inesperada"):
        apply(engine, plan)
    assert engine.rollback_count == 1
    assert 42 not in engine.repos


def test_apply_blocks_admin_connection_user():
    engine = FakeCatalogEngine(user="postgres")
    plan = plan_for(repo_row(), engine)
    with pytest.raises(LoadPlanError, match="Usuario de conexión"):
        apply(engine, plan)
    assert engine.rollback_count == 1
    assert 42 not in engine.repos


def test_apply_blocks_missing_hash_version_column():
    engine = FakeCatalogEngine(has_version_column=False)
    plan = plan_for(repo_row(), engine)
    with pytest.raises(LoadPlanError, match="content_hash_version"):
        apply(engine, plan)
    assert 42 not in engine.repos


def test_apply_rolls_back_when_readme_write_fails():
    engine = FakeCatalogEngine(fail_readme_for=42)
    plan = plan_for(repo_row(), engine)
    with pytest.raises(RuntimeError):
        apply(engine, plan)
    assert engine.repos == {}
    assert engine.readmes == {}
    assert engine.rollback_count == 1


def test_apply_detects_stale_plan():
    repo = repo_row()
    old = dict(repo)
    old["stargazers_count"] = 4
    engine = FakeCatalogEngine({42: stored_row(old)}, {42: TEXT})
    plan = plan_for(repo, engine)
    engine.repos[42]["content_hash"] = "d" * 64
    with pytest.raises(LoadPlanError, match="Plan obsoleto"):
        apply(engine, plan)
    assert engine.rollback_count == 1
    assert engine.repos[42]["stargazers_count"] == 4


def test_apply_never_issues_delete():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    apply(engine, plan)
    assert not any("DELETE" in sql.upper() for sql in engine.statements())


def test_verify_sync_result_accepts_applied_plan():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    apply(engine, plan)
    assert verify_sync_result(engine, plan) == ()


def test_verify_sync_result_detects_mismatch():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    apply(engine, plan)
    engine.repos[42]["content_hash"] = "f" * 64
    problems = verify_sync_result(engine, plan)
    assert problems
    assert "content_hash" in problems[0]


def test_second_run_after_insert_is_idempotent():
    engine = FakeCatalogEngine()
    repo = repo_row()
    first = plan_for(repo, engine)
    apply(engine, first)
    second = plan_for(repo, engine)
    assert second.writes == 0
    assert second.unchanged_repositories == 1
    summary = apply(engine, second)
    assert summary.inserted_repositories == 0
    assert summary.updated_repositories == 0
    assert engine.begin_calls == 0


def test_second_run_after_update_is_idempotent():
    repo = repo_row()
    old = dict(repo)
    old["stargazers_count"] = 4
    engine = FakeCatalogEngine({42: stored_row(old)}, {42: TEXT})
    first = plan_for(repo, engine)
    apply(engine, first)
    second = plan_for(repo, engine)
    assert second.writes == 0
    assert engine.repos[42]["stargazers_count"] == 5
    assert engine.repos[42]["content_hash"] == first.actions[0].content_hash


def legacy_engine(readme_text=TEXT):
    """Catálogo con una fila histórica: versión NULL y hash no v1."""
    repo = repo_row()
    row = stored_row(repo, version=None, content_hash="0" * 64)
    return FakeCatalogEngine({42: row}, {42: readme_text}), repo


def test_apply_backfills_legacy_hash_and_version_atomically():
    engine, repo = legacy_engine()
    plan = plan_for(repo, engine)
    action = plan.actions[0]
    assert action.legacy_backfill is True
    summary = apply(engine, plan)
    assert summary.updated_repositories == 1
    assert summary.backfilled_repositories == 1
    assert engine.repos[42]["content_hash"] == action.content_hash
    assert engine.repos[42]["content_hash_version"] == HASH_VERSION
    updates = [
        sql
        for sql in engine.statements()
        if sql.startswith("UPDATE public.catalog_repositories")
    ]
    assert len(updates) == 1
    # Hash y versión se escriben en la misma sentencia (atomicidad).
    assert "content_hash = :content_hash" in updates[0]
    assert "content_hash_version = :content_hash_version" in updates[0]
    assert verify_sync_result(engine, plan) == ()


def test_backfill_is_idempotent_on_second_run():
    engine, repo = legacy_engine()
    first = plan_for(repo, engine)
    apply(engine, first)
    second = plan_for(repo, engine)
    assert second.writes == 0
    assert second.legacy_backfill_ids == ()
    assert second.unchanged_repositories == 1
    summary = apply(engine, second)
    assert summary.updated_repositories == 0
    assert summary.backfilled_repositories == 0


def test_backfill_rolls_back_when_readme_write_fails():
    engine, repo = legacy_engine(readme_text="# viejo\n")
    engine.fail_readme_for = 42
    plan = plan_for(repo, engine)
    assert plan.actions[0].readme_action == README_UPDATE
    with pytest.raises(RuntimeError):
        apply(engine, plan)
    assert engine.repos[42]["content_hash"] == "0" * 64
    assert engine.repos[42]["content_hash_version"] is None
    assert engine.readmes[42] == "# viejo\n"
    assert engine.rollback_count == 1


def test_backfill_conflict_is_not_overwritten():
    engine, repo = legacy_engine()
    plan = plan_for(repo, engine)
    engine.repos[42]["content_hash"] = "e" * 64
    with pytest.raises(LoadPlanError, match="Plan obsoleto"):
        apply(engine, plan)
    assert engine.repos[42]["content_hash"] == "e" * 64
    assert engine.repos[42]["content_hash_version"] is None
    assert engine.rollback_count == 1


def test_backfill_never_deletes_rows():
    engine, repo = legacy_engine()
    plan = plan_for(repo, engine)
    apply(engine, plan)
    assert 42 in engine.repos
    assert 42 in engine.readmes
    assert not any("DELETE" in sql.upper() for sql in engine.statements())
