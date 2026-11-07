"""Comparación de corridas del enriquecimiento."""

from ai.catalog import load_categories
from ai.eval.compare_enrichment import model_metrics, named_in_examples


def test_detecta_los_repos_nombrados_en_los_ejemplos_de_categorias():
    categorias = load_categories()
    assert named_in_examples("hashicorp/vault", categorias)
    assert not named_in_examples("apache/beam", categorias)


def _registro(categorias, intentos=1):
    return {"categories": categorias, "use_cases": [], "review": {
        "attempts": intentos, "dropped_use_cases": [], "input_tokens": 100,
        "output_tokens": 10, "seconds": 1.0}}


def test_cuenta_estabilidad_y_coincidencia_con_la_semilla():
    corrida1 = {"a/a": _registro(["search"]), "b/b": _registro(["database"], intentos=2)}
    corrida2 = {"a/a": _registro(["search"]), "b/b": _registro(["cache"])}
    m = model_metrics([corrida1, corrida2], ["a/a", "b/b"], {"a/a": "search"})
    assert m["misma categoría principal en las 2 corridas"] == "1 de 2"
    assert m["válidas al primer intento"] == "3 de 4"
    assert m["principal igual a la semilla (referencia)"] == "2 de 2"
