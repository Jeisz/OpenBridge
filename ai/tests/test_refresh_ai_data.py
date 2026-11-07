"""Tests de la actualización de los datos de la IA: sin base, sin modelo y sin tocar los archivos del repo."""

import shutil

import pytest

from ai import catalog
from ai.catalog import ENRICHMENT_FILE, load_repos
from ai.catalog_diff import ARCHIVED_CHANGED, NAME_CHANGED, OTHER_MODEL, diff_catalog
from ai.published import UPSERT_PROCESSING, processing_rows, to_records
from ai.scripts import export_catalog_snapshot, refresh_ai_data as refresh
from ai.scripts.batch import load_records, save_records, stored_version
from ai.scripts.generate_ideas import OUT_FILE as IDEAS_FILE

BLOCK = "el archivo está en otra versión"


@pytest.fixture(scope="module")
def data():
    return load_repos("snapshot"), load_records(ENRICHMENT_FILE), load_records(IDEAS_FILE)


def plan_for(live, known, enrichment, ideas, enrichment_block=None, ideas_block=None):
    return refresh.make_plan(diff_catalog(live, known, enrichment, ideas),
                             enrichment_block, ideas_block)


# --- Plan ---

def test_sin_diferencias_no_hay_nada_que_hacer(data):
    repos, enrichment, ideas = data
    plan = plan_for(repos, repos, enrichment, ideas)
    assert not plan.needs_generate and plan.pending == [] and plan.model_calls == 0


def test_repo_nuevo_con_el_enriquecimiento_en_otra_version(data):
    # Las ideas están en la versión del código: se generan. El enriquecimiento no: queda
    # pendiente con el motivo, en vez de mezclar versiones en el archivo.
    repos, enrichment, ideas = data
    new = repos[0]
    without = lambda records: {k: v for k, v in records.items() if k != new.github_id}
    plan = plan_for(repos, repos[1:], without(enrichment), without(ideas), enrichment_block=BLOCK)
    assert plan.refresh_snapshot
    assert plan.ideas == [new] and plan.enrichment == []
    assert plan.pending == [("enriquecimiento", new, BLOCK)]
    assert plan.model_calls == 1


def test_repo_nuevo_con_las_versiones_al_dia(data):
    repos, enrichment, ideas = data
    new = repos[0]
    without = lambda records: {k: v for k, v in records.items() if k != new.github_id}
    plan = plan_for(repos, repos[1:], without(enrichment), without(ideas))
    assert plan.enrichment == [new] and plan.ideas == [new] and plan.model_calls == 2


def test_repo_eliminado_sale_de_los_archivos(data):
    repos, enrichment, ideas = data
    gone = repos[0]
    plan = plan_for(repos[1:], repos, enrichment, ideas)
    assert plan.drop == {"enriquecimiento": [gone.github_id], "ideas": [gone.github_id]}
    assert plan.model_calls == 0


def test_renombrado_corrige_el_nombre_sin_modelo_y_rehace_las_ideas(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    renamed = repo.model_copy(update={"full_name": repo.full_name + "-nuevo"})
    live = [renamed] + repos[1:]
    plan = plan_for(live, repos, enrichment, ideas, enrichment_block=BLOCK)
    assert plan.rename == [renamed] and plan.enrichment == []     # aun con la versión distinta
    assert plan.ideas == [renamed] and plan.reset_ideas == [renamed]


def test_un_renombrado_no_se_olvida_si_la_copia_ya_se_refresco(data):
    # La corrida anterior refrescó el snapshot y se cortó: snapshot y vista ya coinciden,
    # pero los registros de la IA conservan el nombre viejo.
    repos, enrichment, ideas = data
    repo = repos[0]
    renamed = repo.model_copy(update={"full_name": repo.full_name + "-nuevo"})
    live = [renamed] + repos[1:]
    diff = diff_catalog(live, live, enrichment, ideas)
    assert diff.renamed == []
    assert (renamed, NAME_CHANGED) in diff.enrichment_stale
    assert (renamed, NAME_CHANGED) in diff.ideas_stale


def test_archivado_vacia_las_ideas_sin_llamar_al_modelo(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    archived = repo.model_copy(update={"archived": True})
    live = [archived] + repos[1:]
    diff = diff_catalog(live, live, enrichment, ideas)     # aun con la copia ya refrescada
    assert diff.ideas_stale == [(archived, ARCHIVED_CHANGED)]
    plan = refresh.make_plan(diff)
    assert plan.reset_ideas == [archived] and plan.model_calls == 0


def test_cambio_de_modelo_queda_pendiente(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    record = dict(ideas[repo.github_id], model="modelo-anterior")
    plan = plan_for(repos, repos, enrichment, {**ideas, repo.github_id: record})
    assert plan.ideas == [] and plan.pending == [("ideas", repo, OTHER_MODEL)]


def test_primera_publicacion_sin_modelo(data):
    # La base todavía no tiene nada en ai_processing y el borrador está al día: se publica todo
    # sin llamar al modelo, aunque el enriquecimiento esté en otra versión de las reglas.
    repos, enrichment, ideas = data
    nothing = diff_catalog(repos, repos, {}, {})
    plan = refresh.make_plan(diff_catalog(repos, repos, enrichment, ideas),
                             enrichment_block=BLOCK, published=nothing)
    assert len(plan.publish_enrichment) == len(plan.publish_ideas) == len(repos)
    assert plan.model_calls == 0 and plan.pending == [] and not plan.needs_generate


def test_no_publica_un_borrador_desactualizado(data):
    repos, enrichment, ideas = data
    repo = repos[0]
    live = [repo.model_copy(update={"readme_text": "Nuevo.\n\n" + (repo.readme_text or "")})]
    live += repos[1:]
    published = diff_catalog(live, repos, enrichment, ideas)    # la base tenía lo de antes
    plan = refresh.make_plan(diff_catalog(live, repos, enrichment, ideas), published=published)
    assert repo.github_id not in {r.github_id for r in plan.publish_ideas}
    assert [r.github_id for r in plan.ideas] == [repo.github_id]   # primero se regenera


def test_lo_publicado_se_lee_igual_que_los_archivos(data):
    # Ida y vuelta por ai_processing: lo escrito desde los registros, leído de nuevo,
    # no muestra diferencias con la vista.
    repos, enrichment, ideas = data
    rows = processing_rows("enrichment", list(enrichment.values()))
    rows += processing_rows("ideas", list(ideas.values()))
    columns = ("github_id", "kind", "full_name", "ai_input_hash", "provider", "model",
               "prompt_version", "skipped")
    published = to_records([tuple(r[c] for c in columns) for r in rows])
    assert not diff_catalog(repos, repos, published["enrichment"], published["ideas"]).has_changes


def test_bloqueo_por_version_de_los_archivos_del_repo():
    # Hoy: enriquecimiento en una versión anterior al código, ideas al día.
    assert refresh.version_block(ENRICHMENT_FILE, refresh.ENRICHMENT_VERSION) is not None
    assert refresh.version_block(IDEAS_FILE, refresh.IDEAS_VERSION) is None


# --- Archivos (en una copia temporal) ---

@pytest.fixture
def files(tmp_path, monkeypatch):
    """Copia de ai/data/catalog/ en una carpeta temporal; el código apunta a ella."""
    folder = tmp_path / "catalog"
    shutil.copytree(catalog.SOURCE_DIRS["snapshot"], folder)
    monkeypatch.setitem(catalog.SOURCE_DIRS, "snapshot", folder)
    monkeypatch.setattr(refresh, "ENRICHMENT_FILE", folder / "enrichment.json")
    monkeypatch.setattr(refresh, "IDEAS_FILE", folder / "ideas.json")
    monkeypatch.setattr(refresh, "SNAPSHOT_FILE", folder / "repos.json")
    monkeypatch.setattr(catalog, "ENRICHMENT_FILE", folder / "enrichment.json")
    monkeypatch.setattr(export_catalog_snapshot, "REPOS_FILE", folder / "repos.json")
    monkeypatch.setattr(export_catalog_snapshot, "README_DIR", folder / "readmes")
    monkeypatch.setattr(export_catalog_snapshot, "META_FILE", folder / "meta.json")
    return folder


def test_edit_records_quita_y_renombra_sin_cambiar_la_version(files):
    path = files / "enrichment.json"
    version = stored_version(path)
    records = load_records(path)
    first, second = list(records)[:2]
    refresh.edit_records(path, [first], {second: "otro/nombre"})
    after = load_records(path)
    assert first not in after and after[second]["full_name"] == "otro/nombre"
    assert stored_version(path) == version


def test_generar_y_volver_a_comparar_converge(files, monkeypatch):
    # Un repo salió de la vista y otro es nuevo: generar deja los archivos al día
    # (con el modelo simulado) y la comparación siguiente ya no pide nada.
    repos = load_repos("snapshot")
    gone, new = repos[0], repos[1]
    live = [r for r in repos if r is not gone]
    refresh.edit_records(files / "ideas.json", [new.github_id], {})     # "nuevo" para las ideas
    calls = []

    def fake_generate(repos_, out, provider):
        calls.append([r.full_name for r in repos_])
        records = load_records(out)
        original = load_records(IDEAS_FILE)   # el registro real del repo hace de respuesta
        for r in repos_:
            records[r.github_id] = original[r.github_id]
        save_records(out, records, stored_version(out))

    monkeypatch.setattr(refresh, "generate", fake_generate)
    monkeypatch.setattr(refresh, "enrich", lambda *a, **k: pytest.fail("no debe enriquecer"))
    published = {"enrichment": load_records(ENRICHMENT_FILE), "ideas": load_records(IDEAS_FILE)}
    plan = refresh.current_state(live, published)
    assert plan.ideas == [new] and plan.drop["ideas"] == [gone.github_id]
    refresh.generate_files(plan, live, ["github_id"], "gemini")
    after = refresh.current_state(live, published)
    assert calls == [[new.full_name]]
    assert not after.needs_generate
    assert after.unpublish["ideas"] == [gone.github_id]     # publicado, pero ya no está en la vista
    assert gone.github_id not in load_records(files / "enrichment.json")


def test_escribir_se_niega_si_los_archivos_no_reflejan_la_vista(files, monkeypatch, data):
    repos, _, _ = data
    monkeypatch.setattr(refresh, "read_view", lambda: (repos[1:], ["github_id"]))
    monkeypatch.setattr(refresh, "read_published", lambda: {"enrichment": {}, "ideas": {}})
    monkeypatch.setattr("sys.argv", ["refresh_ai_data", "--escribir"])
    monkeypatch.setattr(refresh, "write_database", lambda *a: pytest.fail("no debe escribir"))
    with pytest.raises(SystemExit) as exit_:
        refresh.main()
    assert exit_.value.code == 2


# --- Base (conexión simulada) ---

class FakeCursor:
    def __init__(self, orphans):
        self.orphans = orphans
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def executemany(self, sql, rows):
        self.executed.extend((sql, row) for row in rows)

    def fetchall(self):
        return [("ai_repo_enrichment", g, 1) for g in self.orphans]


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.failed = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *rest):
        self.failed = exc_type is not None     # psycopg deshace la transacción si hay error

    def cursor(self):
        return self

    def execute(self, *a):            # el "with conn.cursor() as cur" devuelve esto mismo
        return self._cursor.execute(*a)

    def executemany(self, *a):
        return self._cursor.executemany(*a)

    def fetchall(self):
        return self._cursor.fetchall()


@pytest.fixture
def database(monkeypatch):
    """Conexión simulada; los escritores de siempre, reemplazados por registros de llamadas."""
    monkeypatch.setenv(refresh.WRITER_ENV_VAR, "postgresql://usuario@servidor/base")
    written = []
    monkeypatch.setattr(refresh.write_enrichment, "write",
                        lambda cur, e, c: written.append(("e", [r["github_id"] for r in e])) or {})
    monkeypatch.setattr(refresh.write_ideas, "write",
                        lambda cur, i: written.append(("i", [r["github_id"] for r in i])) or {})

    def connect(orphans):
        cur = FakeCursor(orphans)
        conn = FakeConnection(cur)
        monkeypatch.setattr(refresh.psycopg, "connect", lambda url: conn)
        return cur, conn
    return connect, written


def test_sin_permiso_de_borrar_solo_lista_los_huerfanos(database):
    connect, written = database
    cur, conn = connect([111])
    refresh.write_database(refresh.Plan(), delete_orphans=False)
    assert [kind for kind, _ in written] == ["e", "i"] and not conn.failed
    assert not any(sql.startswith("delete") for sql, _ in cur.executed)


def test_borra_solo_filas_regenerables(database):
    connect, _ = database
    cur, _ = connect([111, 222])
    refresh.write_database(refresh.Plan(), delete_orphans=True)
    deletes = [(sql, p) for sql, p in cur.executed if sql.startswith("delete")]
    assert len(deletes) == 5 and all(p == {"ids": [111, 222]} for _, p in deletes)
    assert "assigned_by = 'llm'" in deletes[1][0]
    assert "generated_by = 'llm' and reviewed_at is null" in deletes[2][0]


def test_demasiados_huerfanos_no_cambia_nada(database):
    # Si la vista devuelve de menos (permisos, una sincronización a medias), todo parecería
    # huérfano: se detiene antes de escribir.
    connect, written = database
    cur, conn = connect(list(range(1, 50)))
    with pytest.raises(SystemExit):
        refresh.write_database(refresh.Plan(), delete_orphans=True)
    assert written == [] and conn.failed


def test_publica_solo_lo_marcado_y_su_registro(database, data):
    connect, written = database
    repos, _, _ = data
    cur, conn = connect([])
    plan = refresh.Plan(publish_enrichment=[repos[0]], publish_ideas=[repos[1]])
    refresh.write_database(plan, delete_orphans=False)
    assert written == [("e", [repos[0].github_id]), ("i", [repos[1].github_id])]
    processed = [p for sql, p in cur.executed if sql == UPSERT_PROCESSING]
    assert [(p["github_id"], p["kind"]) for p in processed] == [
        (repos[0].github_id, "enrichment"), (repos[1].github_id, "ideas")]
    assert not conn.failed
