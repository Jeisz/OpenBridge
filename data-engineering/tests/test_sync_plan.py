"""Pruebas offline del planificador incremental (sin red ni PostgreSQL)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent / "src"))

from hash_contract import HASH_VERSION, content_hash_v1  # noqa: E402
from sync_doubles import (  # noqa: E402
    make_result,
    pg_topics,
    record,
    repo_row,
    stored_row,
)
from sync_load import _state_from_rows  # noqa: E402
from sync_plan import (  # noqa: E402
    README_INSERT,
    README_NONE,
    README_PRESERVE,
    README_UNCHANGED,
    README_UPDATE,
    REPO_INSERT,
    REPO_PRESERVE,
    REPO_UNCHANGED,
    REPO_UPDATE,
    CatalogState,
    SyncPlanError,
    build_sync_plan,
    parse_stored_topics,
    validate_plan,
)
from transform import transform_records  # noqa: E402

TEXT = "# README\n"


def transformed(*records):
    return transform_records(list(records))


def state_from(rows, *, text=TEXT):
    """Construye el estado del catálogo con la misma conversión de producción."""
    prepared = []
    for row in (rows if isinstance(rows, list) else [rows]):
        item = dict(row)
        if text is None:
            item["readme_github_id"] = None
            item["readme_text"] = None
        else:
            item["readme_github_id"] = row["github_id"]
            item["readme_text"] = text
        prepared.append(item)
    return _state_from_rows(prepared)


def plan_for(result, state=None, approved=("example/proyecto",)):
    plan = build_sync_plan(
        result,
        CatalogState.empty() if state is None else state,
        approved=approved,
    )
    validate_plan(plan)
    return plan


def test_new_repository_is_inserted_with_v1_hash():
    result = transformed(record())
    plan = plan_for(result)
    action = plan.actions[0]
    assert action.repository_action == REPO_INSERT
    assert action.readme_action == README_INSERT
    assert action.content_hash_version == HASH_VERSION
    assert action.content_hash == content_hash_v1(
        result.repositories[0], result.readmes[0]["readme_text"]
    )
    assert plan.inserted_repositories == 1
    assert plan.inserted_readmes == 1
    assert plan.approved_total == 1
    assert not plan.incomplete


def test_metadata_change_updates_row():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    old = dict(repo)
    old["stargazers_count"] = 4
    plan = plan_for(result, state_from(stored_row(old, text=text)))
    action = plan.actions[0]
    assert action.repository_action == REPO_UPDATE
    assert action.readme_action == README_UNCHANGED
    assert "metadata_changed" in action.reasons
    assert action.previous_content_hash == content_hash_v1(old, text)
    assert action.content_hash != action.previous_content_hash


def test_changed_readme_updates_readme_and_hash():
    result = transformed(record())
    repo = result.repositories[0]
    old_text = "# antiguo\n"
    row = stored_row(repo, text=old_text)
    plan = plan_for(result, state_from(row, text=old_text))
    action = plan.actions[0]
    assert action.repository_action == REPO_UPDATE
    assert action.readme_action == README_UPDATE
    assert "readme_changed" in action.reasons
    assert plan.updated_readmes == 1


def test_unchanged_content_has_no_writes():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    plan = plan_for(result, state_from(stored_row(repo, text=text), text=text))
    action = plan.actions[0]
    assert action.repository_action == REPO_UNCHANGED
    assert action.readme_action == README_UNCHANGED
    assert plan.writes == 0
    assert plan.has_writes is False


def test_plan_uses_contract_hash_version():
    assert HASH_VERSION == "openbridge-ai-v1"
    plan = plan_for(transformed(record()))
    assert plan.hash_version == HASH_VERSION
    assert plan.actions[0].content_hash_version == HASH_VERSION


def test_stored_hash_inconsistent_with_data_is_preserved():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    row = stored_row(repo, text=text, content_hash="a" * 64)
    plan = plan_for(result, state_from(row, text=text))
    action = plan.actions[0]
    assert action.repository_action == REPO_PRESERVE
    assert action.content_hash is None
    assert plan.inconsistent_hash_ids == (repo["github_id"],)
    assert plan.writes == 0


def test_confirmed_missing_readme_inserts_without_readme_row():
    result = transformed(record(status="NO_ENCONTRADO"))
    plan = plan_for(result)
    action = plan.actions[0]
    assert action.repository_action == REPO_INSERT
    assert action.readme_action == README_NONE
    assert action.content_hash == content_hash_v1(result.repositories[0], None)
    assert plan.inserted_readmes == 0
    assert not plan.incomplete


def test_transient_readme_error_preserves_existing_row():
    result = transformed(record(status="ERROR_HTTP"))
    repo = result.repositories[0]
    text = TEXT
    plan = plan_for(result, state_from(stored_row(repo, text=text), text=text))
    action = plan.actions[0]
    assert action.repository_action == REPO_PRESERVE
    assert action.readme_action == README_PRESERVE
    assert plan.unresolved_readme == (repo["full_name"],)
    assert plan.incomplete is True
    assert plan.writes == 0


def test_rate_limit_does_not_insert_partial_row():
    result = transformed(record(status="LIMITE_API"))
    plan = plan_for(result)
    assert plan.inserted_repositories == 0
    assert plan.actions[0].repository_action == REPO_PRESERVE
    assert plan.incomplete is True


def test_unverifiable_row_is_rejected():
    repo = repo_row()
    del repo["pushed_at"]
    result = make_result([repo], [{"github_id": 42, "readme_text": TEXT}])
    with pytest.raises(SyncPlanError, match="Hash no calculable"):
        build_sync_plan(result, CatalogState.empty(), approved=("example/proyecto",))


def test_duplicate_repository_is_rejected():
    result = make_result(
        [repo_row(), repo_row()],
        [{"github_id": 42, "readme_text": TEXT}],
    )
    with pytest.raises(SyncPlanError, match="duplicado"):
        build_sync_plan(result, CatalogState.empty(), approved=("example/proyecto",))


def test_duplicate_approved_entry_is_rejected():
    with pytest.raises(SyncPlanError, match="duplicado"):
        build_sync_plan(
            transformed(record()),
            CatalogState.empty(),
            approved=("example/proyecto", "Example/Proyecto"),
        )


def test_ambiguous_readme_state_is_rejected():
    repo = repo_row()
    result = make_result(
        [repo],
        [{"github_id": 42, "readme_text": TEXT}],
        [{"full_name": repo["full_name"], "readme_status": "NO_ENCONTRADO"}],
    )
    with pytest.raises(SyncPlanError, match="ambiguo"):
        build_sync_plan(result, CatalogState.empty(), approved=("example/proyecto",))


def test_legacy_hash_without_version_is_preserved():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    row = stored_row(repo, text=text, version=None)
    plan = plan_for(result, state_from(row, text=text))
    action = plan.actions[0]
    assert action.repository_action == REPO_PRESERVE
    assert plan.legacy_hash_ids == (repo["github_id"],)
    assert plan.writes == 0
    assert any("sin versión" in warning for warning in plan.warnings)


def test_identity_conflict_is_preserved():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    row = stored_row(repo, text=text, full_name="example/antiguo")
    plan = plan_for(result, state_from(row, text=text))
    assert plan.actions[0].repository_action == REPO_PRESERVE
    assert "identity_conflict" in plan.actions[0].reasons
    assert plan.writes == 0


def test_stored_readme_with_confirmed_404_is_not_deleted():
    result = transformed(record(status="NO_ENCONTRADO"))
    repo = result.repositories[0]
    row = stored_row(repo, text=TEXT)
    plan = plan_for(result, state_from(row, text=TEXT))
    action = plan.actions[0]
    assert action.repository_action == REPO_PRESERVE
    assert action.readme_action == README_PRESERVE
    assert plan.preserved_readmes == 1
    assert plan.writes == 0


def test_unapproved_repository_is_rejected():
    with pytest.raises(SyncPlanError, match="fuera de la lista aprobada"):
        build_sync_plan(
            transformed(record()),
            CatalogState.empty(),
            approved=("otro/repositorio",),
        )


def test_missing_approved_repository_marks_incomplete():
    plan = plan_for(
        transformed(record()),
        approved=("example/proyecto", "example/pendiente"),
    )
    assert plan.missing_repositories == ("example/pendiente",)
    assert plan.incomplete is True


def test_readme_desync_repairs_only_the_readme():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    row = stored_row(repo, text=text)
    plan = plan_for(result, state_from(row, text="# viejo\n"))
    action = plan.actions[0]
    assert action.repository_action == REPO_UNCHANGED
    assert action.readme_action == README_UPDATE
    assert action.reasons == ("readme_desync",)
    assert action.writes_repository is False
    assert plan.writes == 1


def test_validate_plan_rejects_tampered_hash():
    plan = plan_for(transformed(record()))
    tampered = replace(
        plan,
        actions=(replace(plan.actions[0], content_hash="b" * 64),),
    )
    with pytest.raises(SyncPlanError, match="Hash inconsistente"):
        validate_plan(tampered)


def test_validate_plan_rejects_write_without_hash():
    plan = plan_for(transformed(record()))
    tampered = replace(
        plan,
        actions=(replace(plan.actions[0], content_hash=None),),
    )
    with pytest.raises(SyncPlanError, match="Escritura sin hash verificable"):
        validate_plan(tampered)


def test_validate_plan_rejects_preserve_with_new_hash():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    plan = plan_for(result, state_from(stored_row(repo, text=text, version=None)))
    tampered = replace(
        plan,
        actions=(replace(plan.actions[0], content_hash="c" * 64),),
    )
    with pytest.raises(SyncPlanError, match="preservada"):
        validate_plan(tampered)


def test_parse_stored_topics_accepts_both_encodings():
    assert parse_stored_topics(None) == []
    assert parse_stored_topics("{}") == []
    assert parse_stored_topics('{"API","backend"}') == ["api", "backend"]
    assert parse_stored_topics('["api", "backend"]') == ["api", "backend"]
    assert parse_stored_topics('{"a,b","c"}') == ["a,b", "c"]
    with pytest.raises(ValueError):
        parse_stored_topics("sin-formato")


def test_unverifiable_topics_are_preserved():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    row = stored_row(
        repo,
        text=text,
        hash_repo=dict(repo, topics=["otro"]),
        topics="sin-formato",
    )
    plan = plan_for(result, state_from(row, text=text))
    action = plan.actions[0]
    assert action.repository_action == REPO_PRESERVE
    assert "stored_topics_unverifiable" in action.reasons
    assert plan.writes == 0


def test_topics_change_updates_metadata():
    result = transformed(record())
    repo = result.repositories[0]
    text = result.readmes[0]["readme_text"]
    old = dict(repo)
    old["topics"] = ["otro"]
    row = stored_row(old, text=text, topics=pg_topics(old["topics"]))
    plan = plan_for(result, state_from(row, text=text))
    action = plan.actions[0]
    assert action.repository_action == REPO_UPDATE
    assert "metadata_changed" in action.reasons
