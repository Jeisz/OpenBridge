"""Pruebas sin internet del extractor GitHub. No tocan PostgreSQL."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import requests

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "extract_github.py"
spec = importlib.util.spec_from_file_location("openbridge_extract", MODULE_PATH)
assert spec is not None and spec.loader is not None
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


class FakeResponse:
    def __init__(self, status=200, payload=None, *, headers=None, content=b"# README"):
        self.status_code = status
        self._payload = payload
        self.headers = headers or {}
        self.content = content

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def repo(slug="apache/airflow", *, fork=False, github_id=42):
    return {"id": github_id, "full_name": slug, "fork": fork, "topics": ["workflow"]}


def queued_get(items):
    queue = iter(items)
    seen = []

    def getter(url, **kwargs):
        seen.append((url, kwargs))
        response = next(queue)
        if isinstance(response, Exception):
            raise response
        return response

    return getter, seen


def test_desactivado_cero_solicitudes():
    def must_not_call(*args, **kwargs):
        raise AssertionError("No se debe consultar la red")

    assert extract.fetch_repositories(enabled=False, http_get=must_not_call) == ([], [])


def test_lista_blanca_bloquea_urls_externas_duplicados_y_lista_vacia():
    for slugs in (["outside/project"], ["https://evil.com/a"], ["apache/airflow", "APACHE/AIRFLOW"], []):
        with pytest.raises(ValueError):
            extract.fetch_repositories(slugs, enabled=True, http_get=lambda *_args, **_kwargs: None)


def test_metadatos_y_readme_exito():
    fake, calls = queued_get([FakeResponse(200, repo()), FakeResponse(200, content="# Hola 👋".encode())])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert len(records) == 1 and len(audit) == 2
    assert records[0]["id"] == 42
    assert records[0]["_readme_text"] == "# Hola 👋"
    assert records[0]["_readme_status"] == "DISPONIBLE"
    assert records[0]["_metadata_is_simulated"] is True
    assert audit[0]["stage"] == "metadata" and audit[1]["stage"] == "readme"
    assert all(item["success"] for item in audit)
    assert len(calls) == 2
    assert calls[0][0] == "https://api.github.com/repos/apache/airflow"
    assert calls[1][0] == "https://api.github.com/repos/apache/airflow/readme"
    assert all(kwargs["allow_redirects"] is False and kwargs["timeout"] == 10 for _, kwargs in calls)
    assert calls[0][1]["headers"]["Accept"] == "application/vnd.github+json"
    assert calls[1][1]["headers"]["Accept"] == "application/vnd.github.raw+json"


def test_metadata_solo_una_llamada():
    fake, calls = queued_get([FakeResponse(200, repo())])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, include_readme=False, http_get=fake)
    assert len(calls) == len(audit) == 1 and len(records) == 1
    assert records[0]["_readme_status"] == "NO_CONSULTADO"


def test_readme_404_no_elimina_repositorio():
    fake, _ = queued_get([FakeResponse(200, repo()), FakeResponse(404)])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert len(records) == 1 and records[0]["_readme_text"] is None
    assert records[0]["_readme_status"] == "NO_ENCONTRADO"
    assert audit[1]["error_type"] == "HTTP_404_no_encontrado"


def test_fork_excluido_sin_pedir_readme():
    fake, calls = queued_get([FakeResponse(200, repo(fork=True))])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert records == [] and len(calls) == 1 and audit[-1]["error_type"] == "Fork_excluido_T05"


@pytest.mark.parametrize("payload,error", [
    ({"id": True, "full_name": "apache/airflow", "fork": False}, "Identificadores_invalidos"),
    (repo(github_id=-2), "Identificadores_invalidos"),
    ({"id": 1, "full_name": "other/repo", "fork": False}, "Identidad_no_coincide"),
    ({"id": 1, "full_name": "apache/airflow"}, "Fork_no_booleano"),
    ([], "JSON_no_objeto"),
    (ValueError("JSON malo"), "JSON_invalido"),
])
def test_contrato_metadata_invalido(payload, error):
    fake, calls = queued_get([FakeResponse(200, payload)])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert records == [] and len(calls) == 1
    assert audit[-1]["success"] is False and audit[-1]["error_type"] == error


def test_404_metadata_no_hace_readme():
    fake, calls = queued_get([FakeResponse(404)])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert not records and len(calls) == 1 and audit[0]["http_status"] == 404


def test_301_no_sigue_redireccion():
    fake, calls = queued_get([FakeResponse(301)])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert records == [] and len(calls) == 1
    assert audit[-1]["error_type"] == "Redireccion_bloqueada"


def test_503_reintenta_con_backoff():
    fake, calls = queued_get([FakeResponse(503), FakeResponse(200, repo())])
    waits = []
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, include_readme=False,
        http_get=fake, sleeper=waits.append)
    assert len(calls) == len(audit) == 2 and len(records) == 1
    assert waits == [1.0] and audit[0]["error_type"] == "HTTP_503"
    assert audit[1]["attempt"] == 2


def test_timeout_reintento_y_recuperacion():
    fake, calls = queued_get([requests.exceptions.Timeout("simulado"), FakeResponse(200, repo())])
    waits = []
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, include_readme=False,
        http_get=fake, sleeper=waits.append)
    assert len(records) == 1 and len(calls) == 2 and waits == [1.0]
    assert audit[0]["error_type"] == "Timeout"


def test_429_respeta_retry_after():
    fake, calls = queued_get([FakeResponse(429, headers={"Retry-After": "2"}), FakeResponse(200, repo())])
    waits = []
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, include_readme=False,
        http_get=fake, sleeper=waits.append)
    assert len(records) == 1 and len(calls) == 2 and waits == [2.0]
    assert audit[0]["error_type"] == "HTTP_429_limite_solicitudes"


def test_limite_primario_largo_detiene_todo_el_lote():
    fake, calls = queued_get([FakeResponse(403, headers={
        "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1000"
    })])
    records, audit = extract.fetch_repositories(["apache/airflow", "react/react"], enabled=True,
        http_get=fake, clock=lambda: 100.0, sleeper=lambda seconds: pytest.fail("No debe esperar"))
    assert records == [] and len(calls) == len(audit) == 1
    assert audit[0]["error_type"] == "HTTP_403_limite_solicitudes"


def test_403_acceso_denegado_no_reintenta():
    fake, calls = queued_get([FakeResponse(403, payload={"message": "Forbidden"})])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert records == [] and len(calls) == 1
    assert audit[0]["error_type"] == "HTTP_403_acceso_denegado"


def test_limite_secundario_sin_cabecera_detiene_lote():
    fake, calls = queued_get([FakeResponse(429), FakeResponse(200, repo("react/react"))])
    _, audit = extract.fetch_repositories(["apache/airflow", "react/react"], enabled=True,
        http_get=fake, sleeper=lambda _: pytest.fail("No debe esperar 60s"))
    assert len(calls) == len(audit) == 1


def test_utf8_invalido_en_readme():
    fake, _ = queued_get([FakeResponse(200, repo()), FakeResponse(200, content=b"\xff")])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert records[0]["_readme_status"] == "UTF8_INVALIDO"
    assert audit[-1]["error_type"] == "README_UTF8_invalido"


def test_readme_grande_se_rechaza():
    fake, _ = queued_get([FakeResponse(200, repo()), FakeResponse(200, content=b"x" * (extract.MAX_README_BYTES + 1))])
    records, _ = extract.fetch_repositories(["apache/airflow"], enabled=True, http_get=fake)
    assert records[0]["_readme_status"] == "CONTENIDO_INVALIDO_O_GRANDE"


def test_lista_de_diez_aprobada():
    assert len(extract.APPROVED_REPOSITORIES) == 10
    assert len(set(x.casefold() for x in extract.APPROVED_REPOSITORIES)) == 10
    queue = [FakeResponse(200, repo(slug, github_id=i + 1)) for i, slug in enumerate(extract.APPROVED_REPOSITORIES)]
    fake, calls = queued_get(queue)
    records, audit = extract.fetch_repositories(extract.APPROVED_REPOSITORIES, enabled=True,
        include_readme=False, http_get=fake)
    assert len(records) == len(audit) == len(calls) == 10


def test_no_se_registra_token_en_auditoria():
    fake, calls = queued_get([FakeResponse(200, repo())])
    records, audit = extract.fetch_repositories(["apache/airflow"], enabled=True, include_readme=False,
        http_get=fake, token="TOKEN_FICTICIO_NO_PUBLICAR")
    assert len(records) == 1
    assert calls[0][1]["headers"]["Authorization"] == "Bearer TOKEN_FICTICIO_NO_PUBLICAR"
    assert "TOKEN_FICTICIO_NO_PUBLICAR" not in str(audit)


def test_max_attempts_limits():
    with pytest.raises(ValueError):
        extract.fetch_repositories(enabled=False, max_attempts=0)
    with pytest.raises(ValueError):
        extract.fetch_repositories(enabled=False, max_wait_seconds=-1)
