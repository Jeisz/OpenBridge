"""Pruebas offline del planificador; sin HTTP ni PostgreSQL."""
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from load import CatalogSnapshot, LoadPlanError, plan_load
from transform import TransformationResult


def result(repos=(1, 2), readmes=(1, 2), observations=()):
    return TransformationResult(
        repositories=[{"github_id": i, "full_name": f"org/repo{i}"} for i in repos],
        readmes=[{"github_id": i, "readme_text": "# test"} for i in readmes],
        observations=list(observations),
    )


def snapshot(repos=None, readmes=()):
    if repos is None:
        repos = {1: "org/repo1"}
    return CatalogSnapshot(repos, frozenset(readmes))


def test_all_existing_remain_preserved():
    plan = plan_load(result(), snapshot({1: "org/repo1", 2: "org/repo2"}, (1, 2)))
    assert plan.existing_repositories == 2 and plan.new_repositories == 0
    assert plan.existing_readmes == 2 and plan.new_readmes == 0
    assert all(row["repo_plan"] == "CONSERVAR" for row in plan.rows)
    assert all(row["readme_plan"] == "CONSERVAR" for row in plan.rows)


def test_five_existing_five_new():
    plan = plan_load(
        result(range(1, 11), range(1, 11)),
        snapshot({i: f"org/repo{i}" for i in range(1, 6)}, range(1, 6)),
    )
    assert (plan.existing_repositories, plan.new_repositories) == (5, 5)
    assert (plan.existing_readmes, plan.new_readmes) == (5, 5)
    assert sum(r["repo_plan"] == "INSERTAR_PENDIENTE_HASH" for r in plan.rows) == 5


def test_repeat_plan_is_deterministic():
    a = plan_load(result(), snapshot({1: "org/repo1"}, (1,)))
    b = plan_load(result(), snapshot({1: "org/repo1"}, (1,)))
    assert a == b


def test_readme_existing_but_not_retrieved_is_preserved():
    plan = plan_load(result([1], []), snapshot({1: "org/repo1"}, (1,)))
    assert plan.rows[0]["readme_plan"] == "CONSERVAR"


def test_new_repo_missing_readme():
    plan = plan_load(result([3], []), snapshot({}, ()))
    assert plan.missing_readmes == 1
    assert plan.rows[0]["readme_plan"] == "SIN_README_DISPONIBLE"


def test_readme_added_for_existing_repository():
    plan = plan_load(result([1], [1]), snapshot({1: "org/repo1"}, ()))
    assert plan.existing_repositories == 1
    assert plan.new_readmes == 1
    assert plan.rows[0]["readme_plan"] == "INSERTAR_PENDIENTE_HASH"


def test_case_only_different_name_not_warning():
    plan = plan_load(result([1], [1]), snapshot({1: "ORG/REPO1"}, ()))
    assert plan.identity_warnings == 0


def test_repo_name_change_warned_no_update():
    plan = plan_load(result([1], [1]), snapshot({1: "old/name"}, (1,)))
    assert plan.identity_warnings == 1
    assert plan.rows[0]["repo_plan"] == "CONSERVAR"


def test_observations_copied():
    observations = [{"full_name": "org/repo1", "readme_status": "NO_ENCONTRADO"}]
    plan = plan_load(result([1], [], observations), snapshot())
    assert plan.observations == observations


@pytest.mark.parametrize("repos,readmes", [([1, 1], [1]), ([0], []), ([-1], []), ([True], []), (["1"], [])])
def test_invalid_repo_ids(repos, readmes):
    with pytest.raises(LoadPlanError):
        plan_load(result(repos, readmes), snapshot())


@pytest.mark.parametrize("readmes", [[1, 1], [999], [True]])
def test_invalid_readmes(readmes):
    with pytest.raises(LoadPlanError):
        plan_load(result([1], readmes), snapshot())


def test_hash_from_transform_rejected():
    r = result([1], [1])
    r.repositories[0]["content_hash"] = "hash-no-aprobado"
    with pytest.raises(LoadPlanError, match="content_hash"):
        plan_load(r, snapshot())


def test_bad_name_rejected():
    r = result([1], [1])
    r.repositories[0]["full_name"] = " "
    with pytest.raises(LoadPlanError):
        plan_load(r, snapshot())


def test_invalid_input_types_rejected():
    with pytest.raises(LoadPlanError):
        plan_load({}, snapshot())
    with pytest.raises(LoadPlanError):
        plan_load(result(), {})


def test_offline_cli_has_no_sql_or_http():
    script = Path(__file__).resolve().parents[1] / "src" / "load.py"
    process = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=True)
    assert "0 solicitudes HTTP y 0 conexiones SQL" in process.stdout
    assert "NO admite escrituras" in process.stdout


def test_read_catalog_snapshot_sets_transaction_read_only_first():
    from load import read_catalog_snapshot

    calls = []

    class Result:
        def __init__(self, rows):
            self.rows = rows

        def mappings(self):
            return self

        def all(self):
            return self.rows

    class Transaction:
        def __enter__(self):
            calls.append("begin")

        def __exit__(self, exc_type, exc, tb):
            calls.append("end")

    class Connection:
        def __enter__(self):
            calls.append("connect")
            return self

        def __exit__(self, exc_type, exc, tb):
            calls.append("disconnect")

        def begin(self):
            return Transaction()

        def execute(self, statement):
            query = str(statement)
            calls.append(query)
            if query == "SET TRANSACTION READ ONLY":
                return Result([])
            if "catalog_repositories" in query:
                return Result([{"github_id": 1, "full_name": "org/repo1"}])
            if "catalog_readmes" in query:
                return Result([{"github_id": 1}])
            raise AssertionError(query)

    class Engine:
        def connect(self):
            return Connection()

    state = read_catalog_snapshot(Engine())
    assert state.repository_names == {1: "org/repo1"}
    assert state.readme_ids == frozenset({1})
    assert calls.index("SET TRANSACTION READ ONLY") < calls.index(
        "SELECT github_id, full_name FROM public.catalog_repositories")
    assert calls.index("SET TRANSACTION READ ONLY") < calls.index(
        "SELECT github_id FROM public.catalog_readmes")
    assert calls[0:2] == ["connect", "begin"]
    assert calls[-2:] == ["end", "disconnect"]
