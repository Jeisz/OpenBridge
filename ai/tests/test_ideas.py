"""Ideas de integración: entrada del modelo y validación de su salida (sin llamar al LLM)."""

import json

from ai import llm
from ai.ideas import (NO_LANGUAGE, PROMPT_VERSION, SNIPPET_MAX_LINES, CodeBlock, IdeaDraft,
                      IdeasDraft, check_ideas, docs_url, github_slug, ideas_for_repo, ideas_input,
                      rule_problems, sections, split_readme)
from ai.scripts.generate_ideas import up_to_date
from shared.contracts.integration_idea import IntegrationIdea
from shared.contracts.repo import Repo

README = """# Tool

Tool is a job queue for Python and Go services.

## Install

```sh
pip install tool
```

## Docker

Run the server with Docker:

```
docker run -p 8080:8080 acme/tool
```

## REST API

Tool has an HTTP API for submitting jobs.
"""

def _repo(readme: str | None, **cambios) -> Repo:
    datos = {"full_name": "acme/tool", "github_id": 1, "description": "Tool",
             "topics": [], "stargazers_count": 1, "pushed_at": "2026-10-01T00:00:00Z",
             "archived": False, "readme_text": readme}
    return Repo.model_validate({**datos, **cambios})


# --- Bloques de código ---

def test_separa_prosa_y_bloques_en_orden():
    partes = split_readme("Intro.\n\n```python\nimport x\n```\n\nFin.")
    assert partes[0].strip() == "Intro."
    assert partes[1] == CodeBlock("python", "import x")
    assert partes[2].strip() == "Fin."


def test_el_lenguaje_es_la_primera_palabra_de_la_marca_en_minusculas():
    partes = split_readme('```Python hl_lines="7 12"\nprint(1)\n```')
    assert partes == [CodeBlock("python", "print(1)")]


def test_sin_marca_el_lenguaje_es_text():
    assert split_readme("```\npip install tool\n```") == [CodeBlock(NO_LANGUAGE, "pip install tool")]


def test_cerca_de_virgulillas_y_cierre_con_el_mismo_caracter():
    partes = split_readme("~~~sh\necho ```\n~~~")
    assert partes == [CodeBlock("sh", "echo ```")]


def test_bloque_sin_cerrar_llega_hasta_el_final():
    assert split_readme("```bash\nmake\nmake install") == [CodeBlock("bash", "make\nmake install")]


def test_bloques_vacios_se_omiten():
    assert split_readme("```\n\n```\nTexto.") == ["Texto."]


# --- Entrada del modelo ---

def test_el_codigo_conserva_las_urls_y_la_prosa_no():
    readme = ("See https://docs.tool.dev for more.\n\n"
              "```\ncurl http://localhost:8080/api/chat -d '{}'\n```")
    entrada = ideas_input(_repo(readme))
    assert "https://docs.tool.dev" not in entrada.text
    assert entrada.blocks[1].code == "curl http://localhost:8080/api/chat -d '{}'"
    assert "[bloque 1 · text]" in entrada.text


def test_los_bloques_se_numeran_en_orden_desde_uno():
    readme = "```sh\npip install tool\n```\n\nUso:\n\n```python\nimport tool\n```"
    entrada = ideas_input(_repo(readme))
    assert [(n, b.language) for n, b in entrada.blocks.items()] == [(1, "sh"), (2, "python")]


def test_el_recorte_nunca_parte_un_bloque():
    largo = "\n".join(f"linea {i}" for i in range(50))
    readme = "Intro corta.\n\n```\n" + largo + "\n```\n\nFin."
    entrada = ideas_input(_repo(readme), limit=100)
    assert entrada.blocks == {}
    assert "linea" not in entrada.text
    assert entrada.text == "Intro corta."


def test_todo_bloque_numerado_esta_completo_en_el_texto():
    readme = "\n\n".join(f"Paso {i}.\n\n```sh\ncomando-{i} --opcion\n```" for i in range(30))
    entrada = ideas_input(_repo(readme), limit=500)
    assert len(entrada.text) <= 500
    assert entrada.blocks
    for numero, bloque in entrada.blocks.items():
        assert f"[bloque {numero} · sh]\n```\n{bloque.code}\n```" in entrada.text


def test_sin_readme_no_hay_texto_ni_bloques():
    entrada = ideas_input(_repo(None))
    assert entrada.text == "" and entrada.blocks == {}




# --- Validación de cada idea contra la fuente ---

def _idea(**cambios) -> IdeaDraft:
    datos = {"title": "Encolar trabajos desde Python", "integration_type": "sdk",
             "summary": "Usa la librería para encolar trabajos.", "evidence": "pip install tool",
             "code_block": 1, "compatible_stack": ["Python"], "dependencies": ["Servidor de Tool"],
             "difficulty": "medium", "triggers": ["Pedido del usuario"]}
    return IdeaDraft.model_validate({**datos, **cambios})


def _check(*ideas, repo=None):
    repo = repo or _repo(README, homepage="https://tool.dev")
    return check_ideas(IdeasDraft(ideas=list(ideas)), ideas_input(repo), repo, "h1")


def test_una_idea_con_respaldo_cumple_el_contrato():
    aceptadas, descartadas = _check(_idea())
    assert descartadas == []
    idea = IntegrationIdea.model_validate({k: v for k, v in aceptadas[0].items() if k != "evidence"})
    assert idea.id == "llm-1-1"
    assert idea.snippet == "pip install tool" and idea.snippet_language == "sh"
    assert idea.generated_by == "llm" and idea.reviewed_at is None and idea.based_on_hash == "h1"
    assert str(idea.docs_url) == "https://github.com/acme/tool#install"


def test_el_snippet_se_copia_del_readme_con_sus_urls_y_sin_marca_es_text():
    aceptadas, _ = _check(_idea(integration_type="docker", evidence="Run the server with Docker",
                                code_block=2, compatible_stack=["Docker"]))
    assert aceptadas[0]["snippet"] == "docker run -p 8080:8080 acme/tool"
    assert aceptadas[0]["snippet_language"] == NO_LANGUAGE


def test_sin_bloque_no_hay_snippet():
    aceptadas, _ = _check(_idea(integration_type="rest_api", code_block=None,
                                evidence="Tool has an HTTP API for submitting jobs."))
    assert aceptadas[0]["snippet"] is None and aceptadas[0]["snippet_language"] is None


def test_un_bloque_largo_no_se_ofrece_como_snippet():
    largo = "\n".join(f"step {i}" for i in range(SNIPPET_MAX_LINES + 1))
    repo = _repo(f"Install it with pip and Python.\n\n```sh\n{largo}\n```")
    aceptadas, _ = _check(_idea(evidence="Install it with pip and Python."), repo=repo)
    assert aceptadas[0]["snippet"] is None


def test_cita_que_no_esta_en_la_entrada_se_descarta():
    _, descartadas = _check(_idea(evidence="Tool ships an official Java client library"))
    assert descartadas[0]["reason"] == "la cita no está en la entrada"


def test_cita_corta_se_descarta():
    _, descartadas = _check(_idea(evidence="Tool"))
    assert descartadas[0]["reason"] == "cita demasiado corta"


def test_el_stack_solo_conserva_nombres_que_aparecen_como_palabra_completa():
    aceptadas, _ = _check(_idea(compatible_stack=["Python", "Kubernetes", "Go"]))
    assert aceptadas[0]["compatible_stack"] == ["Python", "Go"]


def test_sin_stack_con_respaldo_la_idea_se_descarta():
    _, descartadas = _check(_idea(compatible_stack=["Kubernetes", "React"]))
    assert descartadas[0]["reason"] == "ningún nombre del stack aparece en la entrada"


def test_repo_archivado_no_lleva_ideas():
    repo = _repo(README, archived=True)
    aceptadas, descartadas = _check(_idea(), repo=repo)
    assert aceptadas == [] and descartadas[0]["reason"] == "repo archivado"


def test_lista_vacia_es_una_respuesta_valida():
    assert _check() == ([], [])


def test_orden_de_menor_a_mayor_dificultad_y_ids_en_ese_orden():
    aceptadas, _ = _check(
        _idea(title="A", difficulty="high"),
        _idea(title="B", difficulty="low", integration_type="docker", code_block=2,
              evidence="Run the server with Docker", compatible_stack=["Docker"]),
        _idea(title="C", difficulty="medium", integration_type="rest_api", code_block=None,
              evidence="Tool has an HTTP API for submitting jobs."))
    assert [(i["title"], i["id"]) for i in aceptadas] == [("B", "llm-1-1"), ("C", "llm-1-2"),
                                                          ("A", "llm-1-3")]


def test_titulo_repetido_se_descarta():
    _, descartadas = _check(_idea(), _idea(title="encolar trabajos desde python "))
    assert [d["reason"] for d in descartadas] == ["repetida"]


def test_triggers_maximo_dos_y_sin_vacios():
    aceptadas, _ = _check(_idea(triggers=["Uno", " ", "Dos", "Tres"]))
    assert aceptadas[0]["triggers"] == ["Uno", "Dos"]


# --- Reintento: errores de forma ---

def test_bloque_inexistente_o_mas_de_tres_ideas_piden_reintento():
    entrada = ideas_input(_repo(README))
    problemas = rule_problems(IdeasDraft(ideas=[_idea(code_block=9)] * 4), entrada.blocks)
    assert any("máximo es 3" in p for p in problemas)
    assert any("el bloque 9 no existe; válidos: 1, 2" in p for p in problemas)


# --- docs_url ---

def test_slug_como_github():
    assert github_slug("Documentation, Getting Started, and Certification Exams") == \
        "documentation-getting-started-and-certification-exams"
    assert github_slug("`docker run` quick start!") == "docker-run-quick-start"


def test_un_comentario_dentro_del_codigo_no_es_un_titulo():
    texto = "## Uso\n\n[bloque 1 · sh]\n```\n# instala\npip install tool\n```"
    assert [a for a, _ in sections(texto)] == [None, "uso"]


def test_titulos_repetidos_llevan_sufijo_como_en_github():
    texto = "## Python\nuno\n## Python\ndos con pip install"
    repo = _repo(texto)
    assert docs_url("dos con pip install", texto, repo) == "https://github.com/acme/tool#python-1"


def test_titulo_subrayado_tambien_es_seccion():
    texto = "Getting Started\n===============\n\nRun pip install tool now."
    assert docs_url("Run pip install tool now.", texto, _repo(texto)) == \
        "https://github.com/acme/tool#getting-started"


def test_sin_titulo_usa_el_sitio_y_si_no_hay_el_repo():
    texto = "Tool is a job queue for Python services."
    con_sitio = _repo(texto, homepage="https://tool.dev")
    assert docs_url("a job queue for Python", texto, con_sitio) == "https://tool.dev/"
    assert docs_url("a job queue for Python", texto, _repo(texto)) == "https://github.com/acme/tool"




# --- Reintento: texto dañado y palabras de venta ---

def test_texto_danado_pide_reintento():
    entrada = ideas_input(_repo(README))
    problemas = rule_problems(IdeasDraft(ideas=[_idea(summary="Procesa grandes vol3menes")]),
                              entrada.blocks)
    assert any("caracteres dañados" in p for p in problemas)


def test_versiones_y_nombres_con_numeros_no_son_texto_danado():
    entrada = ideas_input(_repo(README))
    idea = _idea(summary="Usa OAuth2 con Python 3.9+ en K8s y guarda en S3.")
    assert rule_problems(IdeasDraft(ideas=[idea]), entrada.blocks) == []


def test_palabras_de_venta_piden_reintento():
    entrada = ideas_input(_repo(README))
    problemas = rule_problems(IdeasDraft(ideas=[_idea(summary="Un cliente moderno y potente.")]),
                              entrada.blocks)
    assert any("marketing (moderno, potente)" in p for p in problemas)


# --- Una idea por tipo ---

def test_segunda_idea_del_mismo_tipo_se_descarta():
    aceptadas, descartadas = _check(_idea(), _idea(title="Otra forma con la librería"))
    assert len(aceptadas) == 1
    assert [d["reason"] for d in descartadas] == ["tipo repetido"]


# --- Un repo de punta a punta, con el modelo simulado ---

def _simular(monkeypatch, *respuestas):
    """Reemplaza llm.generar: cada llamada devuelve la siguiente respuesta (dict)."""
    pendientes = [json.dumps(r) for r in respuestas]

    def falso(messages, *, schema=None, provider=None, deadline=None):
        texto = pendientes.pop(0)
        return llm.Generation(text=texto, provider=provider, model="m", seconds=0.1,
                              input_tokens=100, output_tokens=20,
                              data=schema.model_validate_json(texto))
    monkeypatch.setattr(llm, "generar", falso)


def test_registro_con_una_idea_y_su_huella(monkeypatch):
    _simular(monkeypatch, {"ideas": [_idea().model_dump()]})
    registro = ideas_for_repo(_repo(README), "gemini")
    assert [i["id"] for i in registro["ideas"]] == ["llm-1-1"]
    assert registro["prompt_version"] == PROMPT_VERSION
    assert registro["model"] == llm.PROVIDERS["gemini"].model
    assert registro["ideas"][0]["based_on_hash"] == registro["ai_input_hash"]
    assert registro["review"]["failed"] is False and registro["review"]["attempts"] == 1


def test_lista_vacia_del_modelo_es_un_registro_valido(monkeypatch):
    _simular(monkeypatch, {"ideas": []})
    registro = ideas_for_repo(_repo(README), "gemini")
    assert registro["ideas"] == [] and registro["review"]["failed"] is False


def test_reintenta_y_guarda_lo_corregido(monkeypatch):
    _simular(monkeypatch, {"ideas": [_idea(code_block=9).model_dump()]},
             {"ideas": [_idea().model_dump()]})
    registro = ideas_for_repo(_repo(README), "gemini")
    assert registro["review"]["attempts"] == 2
    assert registro["ideas"][0]["snippet"] == "pip install tool"


def test_readme_casi_vacio_o_archivado_no_llama_al_modelo(monkeypatch):
    def no_llamar(*args, **kwargs):
        raise AssertionError("no debería llamar al modelo")
    monkeypatch.setattr(llm, "generar", no_llamar)
    assert ideas_for_repo(_repo("Moved to Codeberg."), "gemini")["review"]["skipped"] == \
        "README sin contenido suficiente"
    assert ideas_for_repo(_repo(README, archived=True), "gemini")["review"]["skipped"] == \
        "repo archivado"


# --- Lote: qué cuenta como hecho ---

def test_sin_ideas_cuenta_como_hecho_y_sin_respuesta_valida_no():
    hecho = {"ai_input_hash": "h1", "ideas": [], "review": {"failed": False}}
    assert up_to_date(hecho, "h1")
    assert not up_to_date(hecho, "h2")
    assert not up_to_date({**hecho, "review": {"failed": True}}, "h1")
    assert not up_to_date(None, "h1")
