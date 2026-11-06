"""Lote reanudable: guardado, retoma y manejo de los límites del proveedor (sin llamar al LLM)."""

import json

import pytest

from ai.llm import LLMError, LLMRateLimited
from ai.scripts import batch
from ai.scripts.batch import load_records, run_batch, save_records, select_repos
from shared.contracts.repo import Repo


def _repo(github_id: int, full_name: str) -> Repo:
    return Repo.model_validate({"full_name": full_name, "github_id": github_id,
                                "description": "x", "topics": [], "stargazers_count": 1,
                                "pushed_at": "2026-10-01T00:00:00Z", "archived": False})


def _run(repos, out, process, done=lambda record, h: record is not None and record["hash"] == h):
    return run_batch(repos, out, "1", current_hash=lambda r: f"h{r.github_id}",
                     process=process, is_done=done, describe=lambda rec: "ok")


@pytest.fixture(autouse=True)
def sin_esperas(monkeypatch):
    monkeypatch.setattr(batch.time, "sleep", lambda s: None)


# --- Guardado ---

def test_guardar_y_leer_conserva_los_registros(tmp_path):
    ruta = tmp_path / "salida.json"
    registros = {2: {"github_id": 2, "full_name": "b/b"}, 1: {"github_id": 1, "full_name": "a/a"}}
    save_records(ruta, registros, "7")
    assert load_records(ruta) == registros
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["prompt_version"] == "7"
    assert [r["full_name"] for r in datos["repos"]] == ["a/a", "b/b"]


def test_reintenta_el_reemplazo_si_el_archivo_esta_bloqueado(tmp_path, monkeypatch):
    real = batch.os.replace
    llamadas = []

    def bloqueado_una_vez(origen, destino):
        llamadas.append(destino)
        if len(llamadas) == 1:
            raise PermissionError("bloqueado")
        real(origen, destino)

    monkeypatch.setattr(batch.os, "replace", bloqueado_una_vez)
    ruta = tmp_path / "salida.json"
    save_records(ruta, {1: {"github_id": 1, "full_name": "a/a"}}, "1")
    assert len(llamadas) == 2
    assert load_records(ruta) == {1: {"github_id": 1, "full_name": "a/a"}}


# --- Selección ---

def test_sin_nombres_devuelve_todos_y_con_un_nombre_desconocido_termina():
    repos = [_repo(1, "a/a"), _repo(2, "b/b")]
    assert select_repos(repos, None) == repos
    assert select_repos(repos, ["b/b"]) == [repos[1]]
    with pytest.raises(SystemExit):
        select_repos(repos, ["no/existe"])


# --- Ciclo ---

def test_salta_lo_hecho_y_procesa_lo_nuevo(tmp_path):
    out = tmp_path / "salida.json"
    save_records(out, {1: {"github_id": 1, "full_name": "a/a", "hash": "h1"}}, "1")
    llamados = []

    def process(repo):
        llamados.append(repo.full_name)
        return {"github_id": repo.github_id, "full_name": repo.full_name, "hash": f"h{repo.github_id}"}

    hechos = _run([_repo(1, "a/a"), _repo(2, "b/b")], out, process)
    assert llamados == ["b/b"]
    assert [r["full_name"] for r in hechos] == ["a/a", "b/b"]
    assert set(load_records(out)) == {1, 2}


def test_limite_por_minuto_espera_y_reintenta_el_mismo_repo(tmp_path):
    intentos = []

    def process(repo):
        intentos.append(repo.full_name)
        if len(intentos) == 1:
            raise LLMRateLimited("429", retry_after=5)
        return {"github_id": repo.github_id, "full_name": repo.full_name, "hash": "h1"}

    hechos = _run([_repo(1, "a/a")], tmp_path / "salida.json", process)
    assert intentos == ["a/a", "a/a"]
    assert len(hechos) == 1


def test_limite_del_dia_guarda_lo_hecho_y_termina(tmp_path):
    out = tmp_path / "salida.json"

    def process(repo):
        if repo.github_id == 2:
            raise LLMRateLimited("429", retry_after=3600)
        return {"github_id": repo.github_id, "full_name": repo.full_name, "hash": "h1"}

    with pytest.raises(SystemExit):
        _run([_repo(1, "a/a"), _repo(2, "b/b")], out, process)
    assert set(load_records(out)) == {1}


def test_un_error_del_modelo_salta_el_repo_sin_guardarlo(tmp_path):
    out = tmp_path / "salida.json"

    def process(repo):
        raise LLMError("respuesta inválida")

    assert _run([_repo(1, "a/a")], out, process) == []
    assert load_records(out) == {}
