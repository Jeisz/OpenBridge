"""Enriquecimiento: entrada del modelo y validación de su salida contra la fuente."""

import json

import pytest
from pydantic import ValidationError

from ai import llm
from ai.catalog import load_categories
from ai.enrich import (check_use_cases, clean_readme, cut_text, enrich_repo, enrichment_schema,
                       input_hash, normalize, readme_input, rule_problems, system_prompt,
                       user_message)
from ai.scripts import enrich_catalog
from ai.scripts.enrich_catalog import load_records, save_records, up_to_date
from shared.contracts.repo import Repo


def test_quita_insignias_en_linea():
    texto = "[![CI](https://x/badge.svg)](https://x/actions) Fast tool."
    assert clean_readme(texto) == "Fast tool."


def test_quita_insignias_por_referencia_y_sus_definiciones():
    texto = "[![MIT][license-badge]][license]\n\nFast tool.\n\n[license]: https://x/LICENSE"
    assert clean_readme(texto) == "Fast tool."


def test_conserva_el_texto_de_los_enlaces():
    texto = "See the [Flink site](https://flink.apache.org/) for more."
    assert clean_readme(texto) == "See the Flink site for more."


def test_quita_html_y_junta_lineas_en_blanco_y_espacios():
    texto = '<p align="center"><img src="logo.svg"></p>\n\n\n\n**Kafka** is   fast.'
    assert clean_readme(texto) == "**Kafka** is fast."


def test_no_recorta_un_texto_corto():
    assert cut_text("corto", 100) == "corto"


def test_recorta_al_final_de_un_parrafo():
    texto = "a" * 60 + "\n\n" + "b" * 60
    assert cut_text(texto, 100) == "a" * 60


def test_corta_en_el_limite_si_el_parrafo_deja_menos_de_la_mitad():
    texto = "a" * 30 + "\n\n" + "b" * 90
    assert cut_text(texto, 100) == texto[:100]


# --- Entrada del modelo ---

def _repo(**cambios) -> Repo:
    datos = {"full_name": "acme/stream", "github_id": 1, "description": "Stream processor",
             "topics": ["streaming", "java"], "stargazers_count": 10,
             "pushed_at": "2026-10-01T00:00:00Z", "archived": False}
    return Repo.model_validate({**datos, **cambios})


def test_el_prompt_lista_todas_las_categorias():
    categorias = load_categories()
    prompt = system_prompt(categorias)
    assert all(f"- {id_}:" in prompt for id_ in categorias)


def test_el_mensaje_separa_los_datos_con_etiquetas():
    mensaje = user_message(_repo(), "Fast **streams**.")
    assert "<descripcion>Stream processor</descripcion>" in mensaje
    assert "<topics>streaming, java</topics>" in mensaje
    assert "<readme>\nFast **streams**.\n</readme>" in mensaje


def test_sin_descripcion_ni_readme_las_etiquetas_quedan_vacias():
    repo = _repo(description=None, topics=[])
    assert readme_input(repo) == ""
    assert "<descripcion></descripcion>" in user_message(repo, "")


def test_el_hash_cambia_con_la_entrada_y_con_el_proveedor():
    base = input_hash("entrada", "claude-haiku")
    assert base == input_hash("entrada", "claude-haiku")
    assert base != input_hash("entrada distinta", "claude-haiku")
    assert base != input_hash("entrada", "gemini")
    # Mismo modelo, con y sin razonamiento: salidas distintas, huellas distintas.
    assert base != input_hash("entrada", "claude-haiku-razona")


# --- Salida del modelo ---

Enrichment = enrichment_schema(["data-processing", "messaging"])


def _salida(**cambios):
    datos = {"categories": ["data-processing"], "summary_es": "Framework de flujos.",
             "use_cases": []}
    return Enrichment.model_validate({**datos, **cambios})


def test_el_esquema_rechaza_una_categoria_que_no_existe():
    with pytest.raises(ValidationError):
        _salida(categories=["payments"])


def test_una_salida_correcta_no_tiene_problemas():
    assert rule_problems(_salida()) == []
    assert rule_problems(_salida(summary_es=None)) == []


@pytest.mark.parametrize("cambios, problema", [
    ({"categories": []}, "falta al menos una categoría"),
    ({"categories": ["messaging", "messaging"]}, "repetidas"),
    ({"categories": ["messaging"] * 4}, "el máximo es 3"),
    ({"summary_es": "a" * 251}, "el máximo es 250"),
    ({"summary_es": "  "}, "vacío"),
    ({"summary_es": "Framework con potentes capacidades."}, "marketing (potentes)"),
    ({"summary_es": "Linter extremadamente rápido."}, "marketing (extremadamente)"),
    ({"summary_es": "Framework web moderno."}, "marketing (moderno)"),
])
def test_problemas_que_justifican_un_reintento(cambios, problema):
    assert any(problema in p for p in rule_problems(_salida(**cambios)))


def test_normaliza_formato_espacios_y_mayusculas():
    assert normalize("**Apache  Kafka** is\n`fast`") == "apache kafka is fast"
    assert normalize("a system called [Borg],") == "a system called borg,"


FUENTE = ("<readme>\n**Apache Kafka** is a platform used for high-performance data "
          "pipelines, streaming analytics and data integration.\n</readme>")


def _casos(*pares):
    return Enrichment.model_validate({"categories": ["messaging"], "summary_es": None,
                                      "use_cases": [{"use_case": c, "evidence": e}
                                                    for c, e in pares]}).use_cases


def test_acepta_una_cita_aunque_cambie_el_formato_markdown():
    aceptados, descartados = check_use_cases(
        _casos(("Construir pipelines de datos", "Apache Kafka is a platform used")), FUENTE)
    assert [c["use_case"] for c in aceptados] == ["Construir pipelines de datos"]
    assert descartados == []


def test_acepta_un_elemento_de_lista_de_dos_palabras():
    aceptados, _ = check_use_cases(_casos(("Integrar datos", "data integration")), FUENTE)
    assert [c["use_case"] for c in aceptados] == ["Integrar datos"]


@pytest.mark.parametrize("caso, cita, motivo", [
    ("Analítica en tiempo real", "streaming", "cita demasiado corta"),
    ("Pagos en línea", "used for online payments in banks", "la cita no está en la entrada"),
    ("a" * 101, "high-performance data pipelines", "más de 100 caracteres"),
])
def test_descarta_casos_sin_evidencia_valida(caso, cita, motivo):
    aceptados, descartados = check_use_cases(_casos((caso, cita)), FUENTE)
    assert aceptados == []
    assert motivo in descartados[0]["reason"]


def test_descarta_repetidos_y_los_que_pasan_del_maximo():
    cita = "high-performance data pipelines"
    pares = [("Uso uno", cita), ("uso UNO", cita), ("Uso dos", cita), ("Uso tres", cita),
             ("Uso cuatro", cita), ("Uso cinco", cita)]
    aceptados, descartados = check_use_cases(_casos(*pares), FUENTE)
    assert len(aceptados) == 4
    assert [d["reason"] for d in descartados] == ["repetido", "más de 4"]


# --- Un repo de punta a punta (modelo simulado) ---

README_KAFKA = ("**Apache Kafka** is a platform used for high-performance data pipelines, "
                "streaming analytics and data integration. " + "More text. " * 20)


def _respuesta(categorias, resumen, casos):
    return json.dumps({"categories": categorias, "summary_es": resumen,
                       "use_cases": [{"use_case": c, "evidence": e} for c, e in casos]})


def _simular(monkeypatch, *textos):
    """Reemplaza llm.generar: cada llamada devuelve el siguiente texto."""
    pendientes = list(textos)

    def falso(messages, *, schema=None, provider=None, deadline=None):
        texto = pendientes.pop(0)
        return llm.Generation(text=texto, provider=provider, model="m", seconds=0.1,
                              input_tokens=100, output_tokens=20,
                              data=schema.model_validate_json(texto))
    monkeypatch.setattr(llm, "generar", falso)


def test_registro_con_un_caso_de_uso_descartado(monkeypatch):
    _simular(monkeypatch, _respuesta(
        ["messaging", "data-processing"], "Plataforma de streaming de eventos.",
        [("Construir pipelines de datos", "high-performance data pipelines"),
         ("Pagos bancarios", "used by banks for payments")]))
    registro = enrich_repo(_repo(readme_text=README_KAFKA), load_categories(), "gemini")
    assert registro["categories"] == ["messaging", "data-processing"]
    assert registro["summary_es"] == "Plataforma de streaming de eventos."
    assert registro["use_cases"] == ["Construir pipelines de datos"]
    assert registro["evidence"] == ["high-performance data pipelines"]
    assert registro["review"]["dropped_use_cases"][0]["reason"] == "la cita no está en la entrada"
    assert registro["provider"] == "gemini"
    assert registro["model"] == llm.PROVIDERS["gemini"].model
    assert len(registro["ai_input_hash"]) == 64


def test_reintenta_y_guarda_lo_corregido(monkeypatch):
    _simular(monkeypatch,
             _respuesta(["messaging", "messaging"], "Plataforma.", []),
             _respuesta(["messaging"], "Plataforma.", []))
    registro = enrich_repo(_repo(readme_text=README_KAFKA), load_categories(), "gemini")
    assert registro["review"]["attempts"] == 2
    assert registro["categories"] == ["messaging"]


def test_readme_casi_vacio_no_da_casos_de_uso(monkeypatch):
    _simular(monkeypatch, _respuesta(["dev-tools"], "Lenguaje de programación.",
                                     [("Compilar programas", "Moved to Codeberg here")]))
    registro = enrich_repo(_repo(readme_text="Moved to Codeberg here"), load_categories(), "gemini")
    assert registro["use_cases"] == []
    assert registro["review"]["dropped_use_cases"][0]["reason"] == "README sin contenido suficiente"


def test_si_el_resumen_sigue_largo_tras_el_reintento_queda_null(monkeypatch):
    largo = _respuesta(["messaging"], "a" * 300, [])
    _simular(monkeypatch, largo, largo)
    registro = enrich_repo(_repo(readme_text=README_KAFKA), load_categories(), "gemini")
    assert registro["summary_es"] is None
    assert registro["categories"] == ["messaging"]


# --- Guardado y retoma del lote ---

def test_guardar_y_leer_conserva_los_registros(tmp_path):
    ruta = tmp_path / "enrichment.json"
    registros = {2: {"github_id": 2, "full_name": "b/b"}, 1: {"github_id": 1, "full_name": "a/a"}}
    save_records(ruta, registros)
    assert load_records(ruta) == registros
    assert [r["full_name"] for r in json.loads(ruta.read_text(encoding="utf-8"))["repos"]] == ["a/a", "b/b"]


def test_se_salta_solo_lo_que_tiene_el_mismo_hash_y_datos():
    registro = {"ai_input_hash": "h1", "categories": ["messaging"]}
    assert up_to_date(registro, "h1")
    assert not up_to_date(registro, "h2")
    assert not up_to_date({**registro, "categories": []}, "h1")
    assert not up_to_date(None, "h1")


def test_reintenta_el_reemplazo_si_el_archivo_esta_bloqueado(tmp_path, monkeypatch):
    real = enrich_catalog.os.replace
    llamadas = []

    def bloqueado_una_vez(origen, destino):
        llamadas.append(destino)
        if len(llamadas) == 1:
            raise PermissionError("bloqueado")
        real(origen, destino)

    monkeypatch.setattr(enrich_catalog.os, "replace", bloqueado_una_vez)
    monkeypatch.setattr(enrich_catalog.time, "sleep", lambda s: None)  # sin esperas reales
    ruta = tmp_path / "enrichment.json"
    save_records(ruta, {1: {"github_id": 1, "full_name": "a/a"}})
    assert len(llamadas) == 2
    assert load_records(ruta) == {1: {"github_id": 1, "full_name": "a/a"}}
