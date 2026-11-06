"""Medición de las ideas contra la referencia (sin llamar al LLM)."""

from pathlib import Path

from ai.eval.evaluate_ideas import load_criteria, load_reference, score_run, stable_repos

FRAMEWORKS = Path(__file__).parents[1] / "eval" / "ideas_reference_frameworks.json"


def _idea(tipo, title="Idea", snippet=None):
    return {"integration_type": tipo, "title": title, "snippet": snippet}


def _registro(nombre, *ideas, failed=False):
    return {"full_name": nombre, "ideas": list(ideas),
            "review": {"failed": failed, "dropped_ideas": []}}


REF = {
    "a/sdk": {"required": [{"type": "sdk", "evidence": "x"}], "admissible": ["docker"],
              "forbidden": ["webhook"], "forbidden_snippets": ["testcluster"]},
    "b/vacio": {"required": [], "admissible": [], "forbidden": [], "max_ideas": 0},
    "c/uno": {"required": [{"type": "docker", "evidence": "y"}], "admissible": [],
              "forbidden": [], "max_ideas": 1},
}


def _corrida(**cambios):
    run = {"a/sdk": _registro("a/sdk", _idea("sdk")),
           "b/vacio": _registro("b/vacio"),
           "c/uno": _registro("c/uno", _idea("docker"))}
    run.update(cambios)
    return run


def test_la_referencia_tiene_15_repos_15_requeridas_y_sus_criterios():
    referencia = load_reference()
    assert len(referencia) == 15
    assert sum(len(r["required"]) for r in referencia.values()) == 15
    assert load_criteria() == {"min_required": 12, "min_stable": 12}


def test_la_referencia_de_frameworks_no_repite_repos_de_la_principal():
    frameworks = load_reference(FRAMEWORKS)
    assert len(frameworks) == 3
    assert not set(frameworks) & set(load_reference())
    assert all("rest_api" in r["forbidden"] for r in frameworks.values())


def test_corrida_perfecta():
    score = score_run(_corrida(), REF)
    assert (score["found"], score["required"]) == (2, 2)
    assert (score["empty_ok"], score["empty_total"]) == (1, 1)
    assert score["forbidden"] == [] and score["over_max"] == [] and score["unexpected"] == []


def test_idea_en_repo_que_debia_quedar_vacio_es_prohibida():
    score = score_run(_corrida(**{"b/vacio": _registro("b/vacio", _idea("sdk"))}), REF)
    assert score["empty_ok"] == 0
    assert "debía quedar sin ideas" in score["forbidden"][0]


def test_tipo_y_snippet_prohibidos():
    run = _corrida(**{"a/sdk": _registro("a/sdk", _idea("sdk", snippet="from testcluster import x"),
                                         _idea("webhook", "W"))})
    assert len(score_run(run, REF)["forbidden"]) == 2


def test_tope_superado_y_tipo_fuera_de_la_referencia():
    run = _corrida(**{"c/uno": _registro("c/uno", _idea("docker"), _idea("rest_api", "R"))})
    score = score_run(run, REF)
    assert score["over_max"] == ["c/uno"]
    assert score["unexpected"] == ["c/uno · rest_api · R"]


def test_sin_respuesta_valida_cuenta_como_faltante():
    score = score_run(_corrida(**{"a/sdk": _registro("a/sdk", failed=True)}), REF)
    assert score["missing"] == ["a/sdk"] and score["found"] == 1


def test_estabilidad_compara_los_tipos_por_repo():
    otra = _corrida(**{"a/sdk": _registro("a/sdk", _idea("sdk"), _idea("docker", "D"))})
    assert stable_repos([_corrida(), otra], REF) == ["b/vacio", "c/uno"]
