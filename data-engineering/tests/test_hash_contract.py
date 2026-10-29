"""Pruebas 100% offline del contrato de hashes OpenBridge v1."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hash_contract import (
    HASH_VERSION,
    ContentHashError,
    canonical_json,
    content_hash_v1,
    preview_transformation_hashes,
)
from transform import TransformationResult, transform_records


def record(**overrides):
    data = {
        "id": 42, "full_name": "example/proyecto", "name": "proyecto",
        "fork": False, "archived": False, "description": "Café ☕",
        "homepage": None, "language": "Python", "topics": ["api", "backend"],
        "stargazers_count": 5, "forks_count": 1,
        "pushed_at": "2026-10-20T12:30:00Z",
        "license": {"spdx_id": "MIT"},
        "_readme_status": "DISPONIBLE", "_readme_text": "# Café ☕\n",
    }
    data.update(overrides)
    return data


def transformed(**overrides):
    return transform_records([record(**overrides)])


def hashed(result=None):
    return preview_transformation_hashes(result if result is not None else transformed())


def pair():
    result = transformed()
    return result.repositories[0], result.readmes[0]["readme_text"]


def mutate(field, value):
    repo, readme = pair()
    changed = dict(repo)
    changed[field] = value
    return changed, readme


def test_hash_is_sha256_hex_64():
    repo, readme = pair()
    assert re.fullmatch(r"[0-9a-f]{64}", content_hash_v1(repo, readme))


def test_exact_reference_vector_matches_fixture():
    reference = Path(__file__).resolve().parents[1] / "docs" / "content_hash_v1_vectors.json"
    doc = json.loads(reference.read_text(encoding="utf-8"))
    assert doc["contract_version"] == HASH_VERSION
    assert len(doc["vectors"]) == 3
    for vector in doc["vectors"]:
        assert content_hash_v1(vector["repository"], vector["readme_text"]) == vector["sha256"]
        assert canonical_json(vector["repository"], vector["readme_text"]) == vector["canonical_json"]


def test_sha256_is_over_utf8_canonical_bytes():
    repo, readme = pair()
    assert content_hash_v1(repo, readme) == hashlib.sha256(canonical_json(repo, readme).encode("utf-8")).hexdigest()


def test_repeat_stable():
    repo, readme = pair()
    assert content_hash_v1(repo, readme) == content_hash_v1(repo, readme)


def test_repository_mapping_order_ignored():
    repo, readme = pair()
    assert content_hash_v1(repo, readme) == content_hash_v1(dict(reversed(list(repo.items()))), readme)


def test_topics_order_ignored():
    repo, readme = mutate("topics", ["backend", "api"])
    old, old_readme = pair()
    assert content_hash_v1(repo, readme) == content_hash_v1(old, old_readme)


def test_unicode_nfc_equivalence():
    repo, readme = pair()
    other = dict(repo, description="Cafe\u0301 ☕")
    assert content_hash_v1(repo, readme) == content_hash_v1(other, "# Cafe\u0301 ☕\n")


def test_pushed_at_timezone_equivalence():
    repo, readme = pair()
    other = dict(repo, pushed_at="2026-10-20T07:30:00-05:00")
    assert content_hash_v1(repo, readme) == content_hash_v1(other, readme)


def test_pushed_at_zero_offset_equivalence():
    repo, readme = pair()
    other = dict(repo, pushed_at="2026-10-20T12:30:00+00:00")
    assert content_hash_v1(repo, readme) == content_hash_v1(other, readme)


def test_utc_timestamp_format_is_explicit():
    repo, readme = pair()
    doc = json.loads(canonical_json(repo, readme))
    assert doc["repository"]["pushed_at"] == "2026-10-20T12:30:00.000000Z"


@pytest.mark.parametrize("field,value", [
    ("github_id", 43), ("description", "Nuevo texto"),
    ("homepage", "https://example.org"), ("language", "Go"),
    ("topics", ["api"]), ("stargazers_count", 6),
    ("forks_count", 2), ("pushed_at", "2026-10-21T12:30:00Z"),
    ("archived", True), ("license_spdx_id", "Apache-2.0"),
    ("full_name", "another/proyecto"), ("name", "proyecto2"),
])
def test_any_contracted_field_change_changes_hash(field, value):
    repo, readme = pair()
    edited = deepcopy(repo)
    edited[field] = value
    # Full name/name must be mutually consistent to compare a valid changed value.
    if field == "name":
        edited["full_name"] = "example/proyecto2"
    assert content_hash_v1(repo, readme) != content_hash_v1(edited, readme)


def test_readme_content_change_changes_hash():
    repo, readme = pair()
    assert content_hash_v1(repo, readme) != content_hash_v1(repo, readme + "más contenido")


def test_readme_whitespace_is_meaningful():
    repo, readme = pair()
    assert content_hash_v1(repo, readme) != content_hash_v1(repo, readme.strip())


def test_readme_newline_style_is_meaningful():
    repo, readme = pair()
    assert content_hash_v1(repo, readme) != content_hash_v1(repo, readme.replace("\n", "\r\n"))


def test_readme_none_different_from_empty():
    repo, _ = pair()
    assert content_hash_v1(repo, None) != content_hash_v1(repo, "")


def test_null_is_json_null_not_text_null():
    repo, _ = pair()
    payload = json.loads(canonical_json(repo, None))
    assert payload["repository"]["homepage"] is None
    assert payload["readme_text"] is None


def test_schema_version_is_inside_payload():
    repo, readme = pair()
    assert json.loads(canonical_json(repo, readme))["contract_version"] == HASH_VERSION


def test_extract_timestamp_not_in_hash_inputs():
    repo, readme = pair()
    assert "extracted_at" not in canonical_json(repo, readme)
    assert "updated_at" not in canonical_json(repo, readme)


def test_reject_unknown_field_including_legacy_hash():
    repo, readme = pair()
    repo["content_hash"] = "a" * 64
    with pytest.raises(ContentHashError, match="sobran"):
        content_hash_v1(repo, readme)


def test_reject_missing_required_field():
    repo, readme = pair()
    del repo["pushed_at"]
    with pytest.raises(ContentHashError, match="faltan"):
        content_hash_v1(repo, readme)


@pytest.mark.parametrize("invalid", [True, "42", 0, -1, None])
def test_invalid_github_id(invalid):
    repo, readme = mutate("github_id", invalid)
    with pytest.raises(ContentHashError, match="github_id"):
        content_hash_v1(repo, readme)


@pytest.mark.parametrize("invalid", [True, -1, "5", 3.1, None])
def test_invalid_stars(invalid):
    repo, readme = mutate("stargazers_count", invalid)
    with pytest.raises(ContentHashError, match="stargazers_count"):
        content_hash_v1(repo, readme)


@pytest.mark.parametrize("invalid", ["false", 0, None])
def test_invalid_archived(invalid):
    repo, readme = mutate("archived", invalid)
    with pytest.raises(ContentHashError, match="archived"):
        content_hash_v1(repo, readme)


@pytest.mark.parametrize("invalid", ["sin fecha", "2026-10-20T12:30:00", 123])
def test_invalid_date(invalid):
    repo, readme = mutate("pushed_at", invalid)
    with pytest.raises(ContentHashError, match="pushed_at"):
        content_hash_v1(repo, readme)


@pytest.mark.parametrize("invalid", ["api", ["API"], [" api"], ["api", "api"], [None]])
def test_invalid_topics(invalid):
    repo, readme = mutate("topics", invalid)
    with pytest.raises(ContentHashError, match="topics"):
        content_hash_v1(repo, readme)


def test_reject_readme_nonstring():
    repo, _ = pair()
    with pytest.raises(ContentHashError, match="readme_text"):
        content_hash_v1(repo, 100)


def test_happy_preview_available():
    result = transformed()
    output = hashed(result)
    assert len(output) == 1
    assert output[0].github_id == 42
    assert output[0].readme_state == "DISPONIBLE"
    assert output[0].content_hash_version == HASH_VERSION
    assert output[0].content_hash == content_hash_v1(result.repositories[0], result.readmes[0]["readme_text"])


def test_404_confirmed_can_hash_null():
    result = transformed(_readme_status="NO_ENCONTRADO", _readme_text=None)
    output = hashed(result)
    assert output[0].readme_state == "NO_ENCONTRADO"
    assert output[0].content_hash == content_hash_v1(result.repositories[0], None)


@pytest.mark.parametrize("status", ["NO_CONSULTADO", "ERROR_HTTP", "LIMITE_API", "UTF8_INVALIDO", "CONTENIDO_INVALIDO_O_GRANDE"])
def test_transient_or_unknown_readme_cannot_hash(status):
    with pytest.raises(ContentHashError, match="README no verificable"):
        hashed(transformed(_readme_status=status, _readme_text=None))


def test_missing_readme_without_observation_is_rejected():
    result = transformed()
    result.readmes.clear()
    with pytest.raises(ContentHashError, match="faltan resultados"):
        hashed(result)


def test_unknown_observation_rejected():
    result = transformed()
    result.observations.append({"full_name": "other/repo", "readme_status": "NO_ENCONTRADO"})
    with pytest.raises(ContentHashError, match="observación sin repositorio"):
        hashed(result)


def test_conflicting_readme_404_rejected():
    result = transformed()
    result.observations.append({"full_name": "example/proyecto", "readme_status": "NO_ENCONTRADO"})
    with pytest.raises(ContentHashError, match="incompatible"):
        hashed(result)


def test_duplicate_readme_rejected():
    result = transformed()
    result.readmes.append(dict(result.readmes[0]))
    with pytest.raises(ContentHashError, match="duplicado"):
        hashed(result)


def test_orphan_readme_rejected():
    result = transformed()
    result.readmes.append({"github_id": 999, "readme_text": "extra"})
    with pytest.raises(ContentHashError, match="huérfano"):
        hashed(result)


def test_duplicate_repo_rejected():
    result = transformed()
    result.repositories.append(dict(result.repositories[0]))
    with pytest.raises(ContentHashError, match="duplicados"):
        hashed(result)


def test_input_unmodified():
    result = transformed()
    original = deepcopy(result)
    hashed(result)
    assert result == original


def test_preview_multiple_records_and_order():
    result = transform_records([
        record(),
        record(id=43, full_name="another/tool", name="tool", _readme_status="NO_ENCONTRADO", _readme_text=None),
    ])
    output = hashed(result)
    assert [item.github_id for item in output] == [42, 43]
    assert [item.readme_state for item in output] == ["DISPONIBLE", "NO_ENCONTRADO"]


def test_bad_result_type_rejected():
    with pytest.raises(ContentHashError, match="TransformationResult"):
        hashed({})


def test_safe_cli_never_uses_network_or_sql():
    source = Path(__file__).resolve().parents[1] / "src" / "hash_contract.py"
    process = subprocess.run([sys.executable, str(source)], text=True, capture_output=True, check=True)
    assert "0 HTTP, 0 conexiones SQL, 0 escrituras" in process.stdout
    assert process.stderr == ""
