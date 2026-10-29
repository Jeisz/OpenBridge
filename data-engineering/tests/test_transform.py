"""Pruebas offline de transform_records; no acceden a GitHub ni PostgreSQL."""
from pathlib import Path
import sys
import copy
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from transform import TransformationError, transform_records


def sample(**overrides):
    record = {
        "id": 123, "full_name": "example/project", "name": "project",
        "description": "  Proyecto  ", "homepage": "   ", "language": "Python",
        "topics": ["Backend", "backend", "API"], "stargazers_count": 6,
        "forks_count": 0, "pushed_at": "2026-10-20T12:30:00Z",
        "archived": False, "fork": False, "license": {"spdx_id": "MIT"},
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
