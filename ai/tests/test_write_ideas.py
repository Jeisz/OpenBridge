"""Escritura de las ideas en la base y su revisión (sin base real)."""

import pytest

from ai.scripts.review_ideas import check_ids
from ai.scripts.write_ideas import plan_rows, validate_records
from ai.scripts.load_seed_example import IDEA_COLUMNS

SNAPSHOT = [{"full_name": "a/redis", "github_id": 1, "archived": False},
            {"full_name": "b/viejo", "github_id": 2, "archived": True}]


def _idea(n, tipo="sdk", github_id=1, nombre="a/redis"):
    return {"id": f"llm-{github_id}-{n}", "full_name": nombre, "title": f"Idea {n}",
            "integration_type": tipo, "summary": "Resumen.", "compatible_stack": ["Python"],
            "dependencies": [], "difficulty": "medium", "triggers": [], "snippet": None,
            "snippet_language": None, "docs_url": "https://github.com/a/redis#uso",
            "generated_by": "llm", "reviewed_at": None, "based_on_hash": "h1",
            "evidence": "pip install redis"}


def _registro(*ideas, github_id=1, nombre="a/redis", failed=False):
    return {"github_id": github_id, "full_name": nombre, "ideas": list(ideas),
            "ai_input_hash": "h1", "review": {"failed": failed}}


# --- Validación del archivo ---

def test_archivo_valido_pasa():
    validate_records([_registro(_idea(1), _idea(2, "docker"))], SNAPSHOT)


@pytest.mark.parametrize("registro, error", [
    (_registro(github_id=9, nombre="x/otro"), "no está en el snapshot"),
    (_registro(failed=True), "sin respuesta válida"),
    (_registro(_idea(1, github_id=2, nombre="b/viejo"), github_id=2, nombre="b/viejo"),
     "archivado con ideas"),
    (_registro(_idea(1), _idea(2, "docker"), _idea(3, "rest_api"), _idea(4, "webhook")),
     "el máximo es 3"),
    (_registro(_idea(1), _idea(1, "docker")), "id repetido"),
    (_registro({**_idea(1), "difficulty": "facil"}), "no cumple IntegrationIdea"),
])
def test_archivo_invalido_no_llega_a_la_base(registro, error):
    with pytest.raises(ValueError, match=error):
        validate_records([registro], SNAPSHOT)


# --- Plan de escritura ---

def _protegida(idea_id, tipo, hash_="h1", github_id=1):
    return {"id": idea_id, "github_id": github_id, "integration_type": tipo,
            "based_on_hash": hash_}


def test_sin_protegidas_escribe_todo_sin_la_cita():
    filas, informe = plan_rows([_registro(_idea(1), _idea(2, "docker"))], [])
    assert [f["id"] for f in filas] == ["llm-1-1", "llm-1-2"]
    assert all(set(f) == set(IDEA_COLUMNS) for f in filas)  # sin "evidence" ni "full_name"
    assert informe == {"skipped_type": [], "skipped_full": [], "stale_reviewed": []}


def test_una_revisada_ocupa_su_tipo_y_su_cupo():
    registro = _registro(_idea(1, "docker"), _idea(2), _idea(3, "rest_api"))
    filas, informe = plan_rows([registro], [_protegida("llm-1-1", "docker")])
    assert [(f["id"], f["integration_type"]) for f in filas] == [("llm-1-2", "sdk"),
                                                               ("llm-1-3", "rest_api")]
    assert informe["skipped_type"] == ["a/redis · llm-1-1"]


def test_id_que_choca_con_una_revisada_toma_el_siguiente_libre():
    filas, _ = plan_rows([_registro(_idea(1))], [_protegida("llm-1-1", "docker")])
    assert [f["id"] for f in filas] == ["llm-1-2"]


def test_cupo_lleno_no_escribe_nada_nuevo():
    protegidas = [_protegida("p1", "docker"), _protegida("p2", "rest_api"),
                  _protegida("p3", "webhook")]
    filas, informe = plan_rows([_registro(_idea(1))], protegidas)
    assert filas == [] and informe["skipped_full"] == ["a/redis · llm-1-1"]


def test_revisada_con_readme_cambiado_se_avisa_sin_tocarla():
    _, informe = plan_rows([_registro()], [_protegida("llm-1-1", "sdk", hash_="viejo")])
    assert informe["stale_reviewed"] == ["a/redis · llm-1-1"]


# --- Revisión ---

def test_solo_se_aprueban_ideas_del_llm_sin_revisar():
    en_base = [("a", "llm", False), ("b", "llm", True), ("c", "human", False)]
    assert check_ids(["a"], en_base) == []
    assert check_ids(["b", "c", "d"], en_base) == ["b: ya está revisada",
                                                   "c: no es una idea del LLM",
                                                   "d: no está en la base"]
    assert check_ids(["a", "a"], en_base) == ["hay ids repetidos"]
