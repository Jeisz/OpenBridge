"""Tests de las métricas de la búsqueda (sin modelo)."""

import pytest

from ai.eval.metrics import (QueryOutcome,
                             expected_ranks,
                             suggest_min_score,
                             summarize,
                             threshold_errors,)


def test_posicion_de_cada_esperado():
    ranking = ["a/x", "b/y", "c/z"]
    assert expected_ranks(ranking, ["c/z", "d/w", "a/x"]) == (3, None, 1)


def test_rank_es_el_primer_esperado_que_aparece():
    assert QueryOutcome("q", (3, None, 2), 0.5).rank == 2
    assert QueryOutcome("q", (None,), 0.5).rank is None


def test_acierto_fuera_del_top_k_cuenta_cero():
    s = summarize([QueryOutcome("q", (4,), 0.5)], k=3)
    assert s["hits"] == 0 and s["mrr"] == 0.0 and s["recall"] == 0.0


def test_mrr_premia_la_posicion():
    s = summarize([QueryOutcome("a", (1,), 0.5), QueryOutcome("b", (2,), 0.5)], k=3)
    assert s["hit_rate"] == 1.0
    assert s["mrr"] == pytest.approx(0.75)    # (1 + 1/2) / 2


def test_recall_cuenta_todos_los_esperados():
    # Caso ZITADEL: keycloak 1.º, zitadel 5.º -> acierto, pero solo llegó la mitad.
    s = summarize([QueryOutcome("auth-sso", (1, 5), 0.5)], k=3)
    assert s["hit_rate"] == 1.0
    assert s["recall"] == 0.5


def test_consultas_sin_respuesta_no_cuentan():
    with_answer = [QueryOutcome("a", (1,), 0.5), QueryOutcome("b", (None,), 0.5)]
    without = [QueryOutcome("n", (), 0.5)]
    assert summarize(with_answer + without, k=3) == summarize(with_answer, k=3)


def test_sin_consultas_con_respuesta_falla():
    with pytest.raises(ValueError):
        summarize([QueryOutcome("n", (), 0.5)], k=3)


def test_umbral_separa_los_dos_errores():
    outcomes = [
        QueryOutcome("ok", (1,), 0.40),          # con respuesta, pasa
        QueryOutcome("bloqueada", (1,), 0.15),   # con respuesta, bloqueada (error grave)
        QueryOutcome("frenada", (), 0.10),       # sin respuesta, frenada
        QueryOutcome("se_cuela", (), 0.25),      # sin respuesta, pasa
    ]
    assert threshold_errors(outcomes, 0.20) == (["bloqueada"], ["se_cuela"])


def test_puntaje_igual_al_umbral_pasa():
    assert threshold_errors([QueryOutcome("borde", (1,), 0.20)], 0.20) == ([], [])


def test_umbral_sugerido_con_los_numeros_medidos():
    # Primera medición sobre el catálogo real: el corte calculado a mano fue 0.20.
    outcomes = [
        QueryOutcome("msg", (2,), 0.307),
        QueryOutcome("db", (2, 3), 0.241),
        QueryOutcome("ia", (1, 15), 0.242),
        QueryOutcome("obs", (3, 5, 4), 0.415),
        QueryOutcome("proc", (14, 4), 0.298),    # no resuelta: no cuenta
        QueryOutcome("tableros", (9,), 0.146),   # no resuelta: no cuenta
        QueryOutcome("n1", (), 0.194),
        QueryOutcome("n2", (), 0.121),
    ]
    assert suggest_min_score(outcomes, k=3) == 0.20


def test_umbral_sugerido_si_se_solapan_es_la_peor_resuelta():
    outcomes = [QueryOutcome("ok", (1,), 0.247), QueryOutcome("n", (), 0.30)]
    assert suggest_min_score(outcomes, k=3) == 0.24


def test_umbral_sugerido_con_margen_menor_a_un_centesimo():
    # 0.25 bloquearía la válida (0.249): se baja a 0.24 y la sin respuesta pasa.
    outcomes = [QueryOutcome("ok", (1,), 0.249), QueryOutcome("n", (), 0.243)]
    assert suggest_min_score(outcomes, k=3) == 0.24


def test_umbral_sugerido_si_la_mejor_sin_respuesta_cae_justo_en_el_corte():
    # Un puntaje igual al umbral pasa: con 0.20 exacto, el corte sube a 0.21.
    outcomes = [QueryOutcome("ok", (1,), 0.30), QueryOutcome("n", (), 0.20)]
    assert suggest_min_score(outcomes, k=3) == 0.21


def test_sin_resueltas_no_hay_umbral_sugerido():
    assert suggest_min_score([QueryOutcome("x", (5,), 0.30)], k=3) is None
