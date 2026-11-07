"""Tests de la comparación entre la vista y lo que tiene la IA: sin base y sin modelo."""

import pytest

from ai.catalog import ENRICHMENT_FILE, load_repos
from ai.catalog_diff import (INPUT_CHANGED, NO_RECORD, OTHER_MODEL, diff_catalog,
                             enrichment_message, with_unix_newlines)
from ai.enrich import input_hash
from ai.scripts import compare_catalog
from ai.scripts.batch import load_records
from ai.scripts.generate_ideas import OUT_FILE as IDEAS_FILE


@pytest.fixture(scope="module")
def data():
    """El snapshot y los registros de la IA del repo, tal como están."""
    return load_repos("snapshot"), load_records(ENRICHMENT_FILE), load_records(IDEAS_FILE)


def changed(repo, **fields):
    return repo.model_copy(update=fields)


def test_las_huellas_guardadas_se_reproducen(data):
    # Si falla, cambió lo que lee el modelo (limpieza del README, recorte, etiquetas) y la
    # próxima actualización regeneraría todos los repos: revisar antes de seguir.
    # Los registros son de otra versión de las reglas que el código y aun así coinciden:
    # la comparación recalcula con la versión de cada registro.
    repos, enrichment, ideas = data
    diff = diff_catalog(repos, repos, enrichment, ideas)
    assert not diff.has_changes
    assert diff.enrichment_stale == [] and diff.ideas_stale == []


def test_repo_nuevo_sin_datos_de_la_ia(data):
    repos, enrichment, ideas = data
    new = repos[0]
    known = repos[1:]
    enrichment = {k: v for k, v in enrichment.items() if k != new.github_id}
    ideas = {k: v for k, v in ideas.items() if k != new.github_id}
    diff = diff_catalog(repos, known, enrichment, ideas)
    assert diff.new == [new]
    assert diff.enrichment_stale == [(new, NO_RECORD)]
    assert diff.ideas_stale == [(new, NO_RECORD)]


def test_repo_eliminado_deja_datos_de_la_ia_sin_repo(data):
    repos, enrichment, ideas = data
    gone = repos[0]
    diff = diff_catalog(repos[1:], repos, enrichment, ideas)
    assert diff.removed == [gone]
    assert diff.orphans == {"enriquecimiento": [gone.github_id], "ideas": [gone.github_id]}
    assert diff.has_changes


def test_readme_cambiado_pide_regenerar(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    live = [changed(repo, readme_text="Párrafo nuevo al inicio.\n\n" + (repo.readme_text or ""))]
    live += repos[1:]
    diff = diff_catalog(live, repos, enrichment, ideas)
    assert [(r.github_id, why) for r, why in diff.enrichment_stale] == [(repo.github_id, INPUT_CHANGED)]
    assert [(r.github_id, why) for r, why in diff.ideas_stale] == [(repo.github_id, INPUT_CHANGED)]
    assert diff.field_changes == {"readme_text": 1}


def test_cambio_despues_del_recorte_no_pide_regenerar(data):
    # La huella mide lo que lee el modelo, no el README entero: lo que queda después del
    # recorte no cambia la salida, así que no se paga otra llamada.
    repos, enrichment, ideas = data
    repo = max(repos, key=lambda r: len(r.readme_text or ""))
    live = [changed(repo, readme_text=repo.readme_text + "\n\nSección nueva al final.")]
    live += [r for r in repos if r is not repo]
    diff = diff_catalog(live, repos, enrichment, ideas)
    assert diff.enrichment_stale == [] and diff.ideas_stale == []
    assert diff.field_changes == {"readme_text": 1}     # la copia sí se refresca


def test_estrellas_solo_refrescan_la_copia(data):
    repos, enrichment, ideas = data
    live = [changed(repos[0], stargazers_count=repos[0].stargazers_count + 10)] + repos[1:]
    diff = diff_catalog(live, repos, enrichment, ideas)
    assert diff.enrichment_stale == [] and diff.ideas_stale == []
    assert diff.field_changes == {"stargazers_count": 1}
    assert diff.has_changes


def test_otra_version_de_las_reglas_no_cuenta_como_cambio(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    record = dict(enrichment[repo.github_id], prompt_version="99")
    record["ai_input_hash"] = input_hash(enrichment_message(repo), record["provider"], "99")
    diff = diff_catalog(repos, repos, {**enrichment, repo.github_id: record}, ideas)
    assert diff.enrichment_stale == []


def test_registro_de_otro_modelo(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    record = dict(enrichment[repo.github_id], model="modelo-anterior")
    diff = diff_catalog(repos, repos, {**enrichment, repo.github_id: record}, ideas)
    assert diff.enrichment_stale == [(repo, OTHER_MODEL)]


def test_mismo_repo_con_otro_nombre(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    live = [changed(repo, full_name=repo.full_name + "-nuevo")] + repos[1:]
    diff = diff_catalog(live, repos, enrichment, ideas)
    assert [(a.full_name, b.full_name) for a, b in diff.renamed] == [
        (repo.full_name, repo.full_name + "-nuevo")]
    assert diff.new == [] and diff.removed == []


def test_cambio_de_archived(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    live = [changed(repo, archived=not repo.archived)] + repos[1:]
    diff = diff_catalog(live, repos, enrichment, ideas)
    assert [r.github_id for r in diff.archived_changed] == [repo.github_id]


def test_saltos_de_linea_de_windows_no_cambian_la_huella(data):
    repos, enrichment, ideas = data
    repo = next(r for r in repos if r.readme_text and "\n" in r.readme_text)
    windows = changed(repo, readme_text=repo.readme_text.replace("\n", "\r\n"))
    assert with_unix_newlines(windows).readme_text == repo.readme_text
    live = [with_unix_newlines(windows) if r is repo else r for r in repos]
    assert not diff_catalog(live, repos, enrichment, ideas).has_changes


# --- Comando ---

@pytest.mark.parametrize("drop, code", [(0, compare_catalog.NO_CHANGES),
                                        (1, compare_catalog.CHANGES)])
def test_codigo_de_salida(data, monkeypatch, capsys, drop, code):
    repos, _, _ = data
    monkeypatch.setattr(compare_catalog, "read_view", lambda: (repos[drop:], ["github_id"]))
    with pytest.raises(SystemExit) as exit_:
        compare_catalog.main()
    assert exit_.value.code == code
    out = capsys.readouterr().out
    assert ("sin diferencias" in out) == (drop == 0)


def test_sin_variable_de_entorno_no_compara(monkeypatch, capsys):
    monkeypatch.setattr(compare_catalog, "load_dotenv", lambda: None)
    monkeypatch.delenv(compare_catalog.ENV_VAR, raising=False)
    with pytest.raises(SystemExit) as exit_:
        compare_catalog.read_view()
    assert exit_.value.code == compare_catalog.FAILED
    assert compare_catalog.ENV_VAR in capsys.readouterr().err
