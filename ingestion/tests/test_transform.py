"""Pruebas offline de transform_records; no acceden a GitHub ni PostgreSQL."""
from pathlib import Path
import sys
import copy
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from transform import (  # noqa: E402
    MAINTENANCE_WINDOW_DAYS,
    TransformationError,
    is_maintained,
    transform_records,
)


def sample(**overrides):
    record = {
        "id": 123, "full_name": "example/project", "name": "project",
        "description": "  Proyecto  ", "homepage": "   ", "language": "Python",
        "topics": ["Backend", "backend", "API"], "stargazers_count": 6,
        "forks_count": 0, "pushed_at": "2026-10-20T12:30:00Z",
        "archived": False, "fork": False, "license": {"spdx_id": "MIT"},
        "disabled": False, "open_issues_count": 4,
        "_readme_status": "DISPONIBLE", "_readme_text": "# Proyecto\n",
    }
    record.update(overrides)
    return record


def test_happy_path():
    result = transform_records([sample()])
    assert len(result.repositories) == len(result.readmes) == 1
    assert result.repositories[0]["homepage"] is None
    assert result.repositories[0]["topics"] == ["backend", "api"]
    assert result.repositories[0]["description"] == "Proyecto"
    assert result.repositories[0]["license_spdx_id"] == "MIT"
    assert result.readmes[0] == {"github_id": 123, "readme_text": "# Proyecto\n"}
    assert "content_hash" not in result.repositories[0]


@pytest.mark.parametrize("homepage,expected", [(None, None), ("", None), ("  ", None), ("https://example.org/", "https://example.org/")])
def test_homepage(homepage, expected):
    assert transform_records([sample(homepage=homepage)]).repositories[0]["homepage"] == expected


def test_missing_readme_no_fake_row():
    result = transform_records([sample(_readme_status="NO_ENCONTRADO", _readme_text=None)])
    assert len(result.repositories) == 1 and not result.readmes
    assert result.observations[0]["readme_status"] == "NO_ENCONTRADO"


@pytest.mark.parametrize("status", ["ERROR_HTTP", "LIMITE_API", "UTF8_INVALIDO", "CONTENIDO_INVALIDO_O_GRANDE", "NO_CONSULTADO"])
def test_readme_other_states_do_not_create_rows(status):
    result = transform_records([sample(_readme_status=status, _readme_text=None)])
    assert not result.readmes and result.observations[0]["readme_status"] == status


def test_empty_available_readme_is_preserved():
    assert transform_records([sample(_readme_text="")]).readmes[0]["readme_text"] == ""


def test_fork_excluded():
    with pytest.raises(TransformationError, match="forks"):
        transform_records([sample(fork=True)])


@pytest.mark.parametrize("github_id", [None, 0, -10, True, "123"])
def test_invalid_id(github_id):
    with pytest.raises(TransformationError, match="id GitHub"):
        transform_records([sample(id=github_id)])


@pytest.mark.parametrize("value", [None, True, "10", -2, 1.1])
def test_invalid_stars(value):
    with pytest.raises(TransformationError, match="stargazers_count"):
        transform_records([sample(stargazers_count=value)])


@pytest.mark.parametrize("date", ["2026-10-20", "no fecha", 3])
def test_invalid_date(date):
    with pytest.raises(TransformationError, match="pushed_at"):
        transform_records([sample(pushed_at=date)])


def test_date_can_be_null():
    assert transform_records([sample(pushed_at=None)]).repositories[0]["pushed_at"] is None


def test_bad_topics():
    with pytest.raises(TransformationError, match="topics"):
        transform_records([sample(topics="python")])


def test_bad_archived():
    with pytest.raises(TransformationError, match="archived"):
        transform_records([sample(archived="False")])


def test_bad_license():
    with pytest.raises(TransformationError, match="license"):
        transform_records([sample(license="MIT")])


def test_missing_license():
    assert transform_records([sample(license=None)]).repositories[0]["license_spdx_id"] is None


def test_available_readme_without_text_rejected():
    with pytest.raises(TransformationError, match="README disponible"):
        transform_records([sample(_readme_text=None)])


def test_pending_readme_rejected():
    with pytest.raises(TransformationError, match="estado README"):
        transform_records([sample(_readme_status="PENDIENTE")])


def test_identity_inconsistent():
    with pytest.raises(TransformationError, match="inconsistentes"):
        transform_records([sample(name="other")])


def test_duplicate_id_rejected():
    record2 = sample(full_name="other/project")
    with pytest.raises(TransformationError, match="duplicado"):
        transform_records([sample(), record2])


def test_duplicate_name_rejected():
    with pytest.raises(TransformationError, match="duplicado"):
        transform_records([sample(), sample(id=999)])


def test_does_not_mutate_source():
    records = [sample()]
    before = copy.deepcopy(records)
    transform_records(records)
    assert records == before


def test_multiple_distinct():
    result = transform_records([sample(), sample(id=456, full_name="other/tool", name="tool", _readme_status="NO_ENCONTRADO", _readme_text=None)])
    assert len(result.repositories) == 2
    assert len(result.readmes) == 1


def test_rejects_wrong_records_type():
    with pytest.raises(TransformationError, match="secuencia"):
        transform_records("oops")


HASH_FIELDS = {
    "github_id", "full_name", "name", "description", "homepage", "language",
    "topics", "stargazers_count", "forks_count", "pushed_at", "archived",
    "license_spdx_id",
}
REFERENCE = datetime(2026, 10, 25, 0, 0, tzinfo=timezone.utc)


def test_supplementary_fields_stay_out_of_the_hash_payload():
    result = transform_records(
        [sample(disabled=True, open_issues_count=9)], reference_time=REFERENCE
    )
    assert set(result.repositories[0]) == HASH_FIELDS
    assert result.supplementary == [
        {
            "github_id": 123,
            "disabled": True,
            "open_issues_count": 9,
        }
    ]


def test_pipeline_does_not_persist_is_maintained():
    """``is_maintained`` es derivado: no viaja en ``supplementary``."""
    result = transform_records(
        [sample(pushed_at="2026-10-24T12:00:00Z")], reference_time=REFERENCE
    )
    assert "is_maintained" not in result.supplementary[0]
    repository = result.repositories[0]
    assert repository["archived"] is False
    assert repository["pushed_at"] == "2026-10-24T12:00:00Z"
    assert is_maintained(
        repository["archived"], repository["pushed_at"], reference_time=REFERENCE
    ) is True


def test_is_maintained_archived_repository_is_false():
    repository = transform_records([sample(archived=True)]).repositories[0]
    assert is_maintained(
        repository["archived"], repository["pushed_at"], reference_time=REFERENCE
    ) is False


def test_is_maintained_without_recent_activity_is_false():
    repository = transform_records(
        [sample(pushed_at="2026-01-01T00:00:00Z")]
    ).repositories[0]
    assert is_maintained(
        repository["archived"], repository["pushed_at"], reference_time=REFERENCE
    ) is False


def test_is_maintained_window_is_inclusive():
    boundary = REFERENCE - timedelta(days=MAINTENANCE_WINDOW_DAYS)
    inside = boundary.isoformat().replace("+00:00", "Z")
    outside = (boundary - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
    assert is_maintained(False, inside, reference_time=REFERENCE) is True
    assert is_maintained(False, outside, reference_time=REFERENCE) is False


def test_is_maintained_without_pushed_at_is_false():
    assert is_maintained(False, None, reference_time=REFERENCE) is False


def test_reference_time_requires_timezone():
    with pytest.raises(TransformationError, match="reference_time"):
        transform_records([sample()], reference_time=datetime(2026, 10, 25))


@pytest.mark.parametrize("value", [None, "False", 0, 1])
def test_invalid_disabled(value):
    with pytest.raises(TransformationError, match="disabled"):
        transform_records([sample(disabled=value)])


@pytest.mark.parametrize("value", [None, True, "3", -1, 1.5])
def test_invalid_open_issues_count(value):
    with pytest.raises(TransformationError, match="open_issues_count"):
        transform_records([sample(open_issues_count=value)])

