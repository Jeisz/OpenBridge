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
    INSERT_REPOSITORY_SQL,
    READ_STATE_SQL,
    REQUIRED_COLUMNS,
    REQUIRED_COLUMNS_SQL,
    SYNC_WRITE_CONFIRMATION,
    UPDATE_REPOSITORY_SQL,
    apply_sync_plan,
    read_catalog_state,
    verify_sync_result,
)
from sync_plan import CatalogState, build_sync_plan, validate_plan  # noqa: E402

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


def test_apply_accepts_pooler_user_with_project_suffix():
    # El pooler exige "rol.<ref>"; dentro de la sesión current_user es "rol".
    engine = FakeCatalogEngine(user="openbridge_data_sync")
    plan = plan_for(repo_row(), engine)
    target = supabase_target(user="openbridge_data_sync.abcd1234")
    summary = apply(engine, plan, target=target)
    assert summary.inserted_repositories == 1
    assert 42 in engine.repos


def test_apply_blocks_pooler_user_with_other_session_role():
    engine = FakeCatalogEngine(user="otro_rol")
    plan = plan_for(repo_row(), engine)
    target = supabase_target(user="openbridge_data_sync.abcd1234")
    with pytest.raises(LoadPlanError, match="Usuario de conexión"):
        apply(engine, plan, target=target)
    assert engine.rollback_count == 1
    assert 42 not in engine.repos


def test_apply_keeps_strict_user_check_outside_pooler():
    # Fuera del pooler no se quita ningún sufijo: el usuario debe coincidir tal cual.
    engine = FakeCatalogEngine(user="openbridge_data_sync")
    plan = plan_for(repo_row(), engine)
    target = supabase_target(
        host="db.abcd1234.supabase.co", user="openbridge_data_sync.abcd1234"
    )
    with pytest.raises(LoadPlanError, match="Usuario de conexión"):
        apply(engine, plan, target=target)
    assert engine.rollback_count == 1
    assert 42 not in engine.repos


def test_database_role_strips_suffix_only_on_pooler():
    pooler = supabase_target(user="openbridge_data_sync.abcd1234")
    direct = supabase_target(
        host="db.abcd1234.supabase.co", user="openbridge_data_sync.abcd1234"
    )
    plain = supabase_target(user="openbridge_data_sync")
    assert pooler.database_role == "openbridge_data_sync"
    assert direct.database_role == "openbridge_data_sync.abcd1234"
    assert plain.database_role == "openbridge_data_sync"


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


def test_apply_persists_operational_fields():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    summary = apply(engine, plan)
    assert summary.inserted_repositories == 1
    assert engine.repos[42]["disabled"] is False
    assert engine.repos[42]["open_issues_count"] == 7
    assert "is_maintained" not in engine.repos[42]
    assert verify_sync_result(engine, plan) == ()


def test_apply_updates_operational_fields_without_changing_the_hash():
    engine = FakeCatalogEngine({42: stored_row(repo_row(), supplementary={"open_issues_count": 3})}, {42: TEXT})
    plan = plan_for(repo_row(), engine)
    action = plan.actions[0]
    assert action.repository_action == "UPDATE"
    summary = apply(engine, plan)
    assert summary.updated_repositories == 1
    assert engine.repos[42]["open_issues_count"] == 7
    assert engine.repos[42]["content_hash"] == action.previous_content_hash


def test_apply_updates_disabled_without_changing_the_hash():
    engine = FakeCatalogEngine(
        {42: stored_row(repo_row(), supplementary={"disabled": True})}, {42: TEXT}
    )
    plan = plan_for(repo_row(), engine)
    action = plan.actions[0]
    assert action.repository_action == "UPDATE"
    assert action.reasons == ("supplementary_changed",)
    summary = apply(engine, plan)
    assert summary.updated_repositories == 1
    assert engine.repos[42]["disabled"] is False
    assert engine.repos[42]["content_hash"] == action.previous_content_hash


def test_apply_blocks_missing_operational_column():
    engine = FakeCatalogEngine(missing_columns=("open_issues_count",))
    plan = plan_for(repo_row(), engine)
    with pytest.raises(LoadPlanError, match="open_issues_count"):
        apply(engine, plan)
    assert 42 not in engine.repos
    assert engine.rollback_count == 1


def test_apply_runs_without_a_physical_is_maintained_column():
    """El pipeline no depende de una columna física ``is_maintained``."""
    engine = FakeCatalogEngine(missing_columns=("is_maintained",))
    plan = plan_for(repo_row(), engine)
    assert apply(engine, plan).inserted_repositories == 1
    assert engine.repos[42]["disabled"] is False
    assert engine.repos[42]["open_issues_count"] == 7
    assert verify_sync_result(engine, plan) == ()


def test_sync_statements_never_reference_is_maintained():
    for statement in (
        REQUIRED_COLUMNS_SQL,
        READ_STATE_SQL,
        INSERT_REPOSITORY_SQL,
        UPDATE_REPOSITORY_SQL,
    ):
        assert "is_maintained" not in statement
    assert "is_maintained" not in REQUIRED_COLUMNS


def test_verify_sync_result_detects_operational_mismatch():
    engine = FakeCatalogEngine()
    plan = plan_for(repo_row(), engine)
    apply(engine, plan)
    engine.repos[42]["open_issues_count"] = 1
    problems = verify_sync_result(engine, plan)
    assert problems
    assert "open_issues_count" in problems[0]

