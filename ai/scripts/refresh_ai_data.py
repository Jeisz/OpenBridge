"""Actualiza los datos de la IA cuando cambia el catálogo: solo lo que cambió.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.refresh_ai_data              # muestra el plan; no toca nada
    python -m ai.scripts.refresh_ai_data --generar    # refresca la copia y regenera con el modelo (solo archivos)
    python -m ai.scripts.refresh_ai_data --escribir   # escribe los archivos en las tablas de la IA
    python -m ai.scripts.refresh_ai_data --escribir --borrar-huerfanos

Lo publicado vive en la base (tablas ai.*, con ai.ai_processing diciendo con qué se generó
cada dato); los archivos de ai/data/catalog/ son el borrador, la caché del lote y la copia para
las evaluaciones. Cada corrida compara la vista con lo publicado y con los archivos
(ai/catalog_diff.py) y hace lo que falta: un repo cuyo borrador ya está al día se publica sin
llamar al modelo. Si se corta (por ejemplo, por el límite del día del proveedor), se vuelve a
correr el mismo comando y termina. Un cambio de reglas (otra versión del prompt, otro modelo)
no se regenera aquí: queda como pendiente, porque es una decisión aparte.

Al escribir también se calculan y guardan los vectores de búsqueda que faltan o quedaron viejos
(ai.ai_embeddings), con lo publicado en esa misma transacción; el modelo de embeddings se carga
solo si hay alguno que calcular.

Requiere AI_READER_DATABASE_URL (leer la vista y lo publicado); con --generar, la clave del proveedor;
con --escribir, AI_DATABASE_URL (usuario escritor). Después de --generar: revisar
`git diff ai/data/catalog/`, reiniciar el servicio del asistente y hacer commit de los archivos.
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from ai.catalog import ENRICHMENT_FILE, load_categories, load_repos
from ai.catalog_diff import (ARCHIVED_CHANGED, INPUT_CHANGED, NAME_CHANGED, NO_RECORD,
                             CatalogDiff, diff_catalog)
from ai.enrich import PROMPT_VERSION as ENRICHMENT_VERSION
from ai.ideas import PROMPT_VERSION as IDEAS_VERSION
from ai.llm import PROVIDERS
from ai.published import (UPSERT_EMBEDDING, UPSERT_PROCESSING, VECTOR_DIMS, fetch_catalog,
                          processing_rows, published_catalog)
from ai.scripts import write_enrichment, write_ideas
from ai.scripts.batch import load_records, save_records, stored_version
from ai.scripts.compare_catalog import fail, read_published, read_view, report
from ai.scripts.enrich_catalog import enrich
from ai.scripts.export_catalog_snapshot import ENV_VAR as READER_ENV_VAR
from ai.scripts.export_catalog_snapshot import REPOS_FILE as SNAPSHOT_FILE
from ai.scripts.export_catalog_snapshot import compare_columns, redact, write_snapshot
from ai.scripts.generate_ideas import OUT_FILE as IDEAS_FILE
from ai.scripts.generate_ideas import generate
from ai.scripts.load_seed_example import ENV_VAR as WRITER_ENV_VAR
from ai.search import plan_vectors
from shared.contracts.repo import Repo

REGENERATE = {NO_RECORD, INPUT_CHANGED}           # cambió la entrada: se pide al modelo
RESET = {NAME_CHANGED, ARCHIVED_CHANGED}          # misma entrada: se quita el registro y se rehace
ORPHANS_SQL = Path(__file__).resolve().parents[1] / "sql" / "consultas" / "huerfanos_ia.sql"
MAX_DELETE = 10   # más huérfanos que esto suele ser un error de lectura de la vista, no repos que salieron

# Solo filas que se pueden regenerar: nunca categorías humanas ni ideas revisadas o de una persona.
DELETE_ORPHANS = (
    "delete from ai.ai_repo_enrichment where github_id = any(%(ids)s)",
    "delete from ai.ai_repo_categories where github_id = any(%(ids)s) and assigned_by = 'llm'",
    "delete from ai.ai_integration_ideas where github_id = any(%(ids)s)"
    " and generated_by = 'llm' and reviewed_at is null",
    "delete from ai.ai_embeddings where github_id = any(%(ids)s)",
    "delete from ai.ai_processing where github_id = any(%(ids)s)",
)


@dataclass
class Plan:
    """Lo que falta para que los archivos de la IA reflejen la vista."""

    refresh_snapshot: bool = False
    drop: dict[str, list[int]] = field(default_factory=dict)   # registros de repos que salieron
    rename: list[Repo] = field(default_factory=list)           # enriquecimiento: solo el nombre
    enrichment: list[Repo] = field(default_factory=list)       # se piden al modelo
    ideas: list[Repo] = field(default_factory=list)
    reset_ideas: list[Repo] = field(default_factory=list)      # se quitan antes de regenerar
    pending: list[tuple[str, Repo, str]] = field(default_factory=list)   # (dato, repo, motivo)
    publish_enrichment: list[Repo] = field(default_factory=list)   # borrador al día, falta publicarlo
    publish_ideas: list[Repo] = field(default_factory=list)
    unpublish: dict[str, list[int]] = field(default_factory=dict)   # publicados que salieron de la vista

    @property
    def needs_generate(self) -> bool:
        return any((self.refresh_snapshot, any(self.drop.values()), self.rename,
                    self.enrichment, self.ideas))

    @property
    def model_calls(self) -> int:
        """Máximo de llamadas al modelo (un repo archivado se salta sin llamar)."""
        return len(self.enrichment) + sum(not r.archived for r in self.ideas)


def version_block(path: Path, code_version: str) -> str | None:
    """Motivo para no regenerar si el archivo es de otra versión de las reglas. None si se puede."""
    stored = stored_version(path)
    if stored is None or stored == code_version:
        return None
    return f"el archivo está en la versión {stored} de las reglas y el código en la {code_version}"


def make_plan(diff: CatalogDiff, enrichment_block: str | None = None,
              ideas_block: str | None = None, published: CatalogDiff | None = None) -> Plan:
    """Decide qué hacer con cada diferencia. No lee ni escribe nada.

    diff: la vista frente a los archivos (borrador). published: la vista frente a lo publicado;
    se publica lo que está desactualizado en la base y ya está al día en el borrador.
    """
    plan = Plan(
        refresh_snapshot=bool(diff.new or diff.removed or diff.renamed
                              or diff.archived_changed or diff.field_changes),
        drop=diff.orphans,
    )
    if published is not None:
        draft_stale = {"enrichment": {r.github_id for r, _ in diff.enrichment_stale},
                       "ideas": {r.github_id for r, _ in diff.ideas_stale}}
        plan.publish_enrichment = [r for r, _ in published.enrichment_stale
                                   if r.github_id not in draft_stale["enrichment"]]
        plan.publish_ideas = [r for r, _ in published.ideas_stale
                              if r.github_id not in draft_stale["ideas"]]
        plan.unpublish = published.orphans
    for repo, why in diff.enrichment_stale:
        if why == NAME_CHANGED:
            plan.rename.append(repo)          # el modelo no lee el nombre: no hace falta llamarlo
        elif why in REGENERATE and not enrichment_block:
            plan.enrichment.append(repo)
        else:
            plan.pending.append(("enriquecimiento", repo, enrichment_block or why))
    for repo, why in diff.ideas_stale:
        if (why in REGENERATE or why in RESET) and not ideas_block:
            plan.ideas.append(repo)
            if why in RESET:                  # la huella no cambió: sin quitarlo, el lote lo saltaría
                plan.reset_ideas.append(repo)
        else:
            plan.pending.append(("ideas", repo, ideas_block or why))
    return plan


def describe_plan(plan: Plan) -> str:
    lines = ["", "Plan:"]
    lines.append(f"- refrescar la copia del catálogo: {'sí' if plan.refresh_snapshot else 'no'}")
    for name, ids in plan.drop.items():
        if ids:
            lines.append(f"- quitar de {name} los repos que salieron: {len(ids)}")
    if plan.rename:
        lines.append(f"- corregir el nombre en el enriquecimiento: {len(plan.rename)}")
    lines.append(f"- enriquecer: {len(plan.enrichment)} · ideas: {len(plan.ideas)} "
                 f"· llamadas al modelo: hasta {plan.model_calls}")
    lines.append(f"- publicar en la base (sin modelo): enriquecimiento {len(plan.publish_enrichment)}"
                 f" · ideas {len(plan.publish_ideas)}")
    unpublished = sorted({i for ids in plan.unpublish.values() for i in ids})
    if unpublished:
        lines.append(f"- publicados que ya no están en la vista: {len(unpublished)} "
                     "(se listan al escribir; se borran con --borrar-huerfanos)")
    for what, repo, why in plan.pending:
        lines.append(f"- pendiente ({what}) {repo.full_name}: {why}")
    return "\n".join(lines)


def check_provider(path: Path, provider: str) -> None:
    """Un solo modelo por archivo: termina si los registros son de otro proveedor."""
    used = {r["provider"] for r in load_records(path).values()}
    if used and used != {provider}:
        fail(f"{path.name} tiene registros de {', '.join(sorted(used))}; con --provider {provider} "
             "el archivo quedaría con dos modelos. Usa el mismo proveedor.")


def edit_records(path: Path, drop: list[int], rename: dict[int, str]) -> None:
    """Quita y renombra registros sin llamar al modelo. Conserva la versión del archivo."""
    if not path.is_file() or not (drop or rename):
        return
    records = load_records(path)
    for github_id in drop:
        records.pop(github_id, None)
    for github_id, name in rename.items():
        if github_id in records:
            records[github_id]["full_name"] = name
    save_records(path, records, stored_version(path))


def generate_files(plan: Plan, live: list[Repo], columns: list[str], provider: str) -> None:
    """Archivos primero, en un orden que se puede repetir: copia → registros → modelo."""
    if plan.refresh_snapshot:
        write_snapshot(live, compare_columns(columns))
        print("Copia del catálogo actualizada.")
    edit_records(ENRICHMENT_FILE, plan.drop.get("enriquecimiento", []),
                 {r.github_id: r.full_name for r in plan.rename})
    edit_records(IDEAS_FILE, plan.drop.get("ideas", []) + [r.github_id for r in plan.reset_ideas], {})
    if plan.ideas:
        generate(plan.ideas, IDEAS_FILE, provider)
    if plan.enrichment:
        enrich(plan.enrichment, ENRICHMENT_FILE, provider)


def current_state(live: list[Repo], published: dict[str, dict[int, dict]]) -> Plan:
    """Compara la vista con lo publicado y con los archivos tal como están ahora, y arma el plan."""
    known = load_repos("snapshot")
    draft = diff_catalog(live, known, load_records(ENRICHMENT_FILE), load_records(IDEAS_FILE))
    public = diff_catalog(live, known, published["enrichment"], published["ideas"])
    plan = make_plan(draft, version_block(ENRICHMENT_FILE, ENRICHMENT_VERSION),
                     version_block(IDEAS_FILE, IDEAS_VERSION), published=public)
    print(report(public, len(live), len(known)))
    print(describe_plan(plan))
    return plan


def stale_vectors() -> int:
    """Vectores guardados que hoy faltan o quedaron viejos frente a lo publicado (solo lectura)."""
    repos, stored = fetch_catalog(os.environ[READER_ENV_VAR])
    return len(plan_vectors(repos, stored)[1])


def publish_vectors(conn: psycopg.Connection, cur: psycopg.Cursor) -> tuple[int, int]:
    """Calcula y guarda los vectores que faltan o quedaron viejos. Devuelve (al día, calculados).

    Lee lo publicado dentro de la transacción de `conn`, así los vectores salen de los textos
    que se acaban de escribir. El modelo se carga solo si hay alguno que calcular.
    """
    from ai import embeddings

    spec = embeddings.model_spec()
    if spec.dims != VECTOR_DIMS:
        print(f"vectores: no se guardan ({spec.name} da {spec.dims} dimensiones; la columna es "
              f"de {VECTOR_DIMS}). El servicio los calcula al arrancar.")
        return 0, 0
    repos, stored = published_catalog(conn)
    current, missing = plan_vectors(repos, stored)
    if missing:
        vectors = embeddings.embed_documents([text for _, text, _ in missing])
        cur.executemany(UPSERT_EMBEDDING, [
            {"github_id": repo.github_id, "embedding": vector.tolist(), "model": spec.name,
             "ai_input_hash": fingerprint}
            for (repo, _, fingerprint), vector in zip(missing, vectors)])
    return len(current), len(missing)


def write_database(plan: Plan, delete_orphans: bool, max_delete: int = MAX_DELETE) -> None:
    """Publica en ai.* lo que el plan marca, en una sola transacción, con los escritores de siempre.

    Solo los repos desactualizados en la base; con su fila en ai_processing.
    """
    snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    wanted = {r.github_id for r in plan.publish_enrichment}
    enrichment = [r for r in load_records(ENRICHMENT_FILE).values() if r["github_id"] in wanted]
    wanted = {r.github_id for r in plan.publish_ideas}
    ideas = [r for r in load_records(IDEAS_FILE).values() if r["github_id"] in wanted]
    try:
        write_enrichment.validate_records(enrichment, snapshot, set(load_categories()))
        write_ideas.validate_records(ideas, snapshot)
    except ValueError as e:
        fail(str(e))
    enrichment_rows, category_rows = write_enrichment.to_rows(enrichment)

    url = os.environ.get(WRITER_ENV_VAR)
    if not url:
        fail(f"Falta {WRITER_ENV_VAR} en .env (ver .env.example)")
    try:
        # Una sola transacción: al salir del with sin error se confirma; con error no cambia nada.
        with psycopg.connect(url) as conn, conn.cursor() as cur:
            cur.execute(ORPHANS_SQL.read_text(encoding="utf-8"))
            orphans = sorted({row[1] for row in cur.fetchall()})
            if delete_orphans and len(orphans) > max_delete:
                fail(f"{len(orphans)} repos con datos de la IA no están en la vista (máximo para "
                     f"borrar: {max_delete}). ¿La vista devolvió todo? No se cambió nada.")
            counts = write_enrichment.write(cur, enrichment_rows, category_rows)
            counts |= write_ideas.write(cur, ideas)
            cur.executemany(UPSERT_PROCESSING, processing_rows("enrichment", enrichment)
                            + processing_rows("ideas", ideas))
            current, computed = publish_vectors(conn, cur)
            counts |= {"vectores al día": current, "vectores calculados y guardados": computed}
            if delete_orphans and orphans:
                for statement in DELETE_ORPHANS:
                    cur.execute(statement, {"ids": orphans})
    except psycopg.Error as e:
        fail(f"No se pudo escribir en la base (no se cambió nada): {redact(str(e), url)}")
    except ValueError as e:     # lo publicado no cumple el contrato al releerlo
        fail(f"No se pudo escribir en la base (no se cambió nada): {e}")
    for key, value in counts.items():
        print(f"{key}: {value}")
    action = "borrados" if delete_orphans else "sin borrar (--borrar-huerfanos)"
    print(f"repos con datos de la IA que no están en la vista: {len(orphans)} {orphans or ''} "
          f"→ {action if orphans else 'ninguno'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Actualiza los datos de la IA según la vista.")
    parser.add_argument("--generar", action="store_true",
                        help="refresca la copia y regenera con el modelo (solo archivos)")
    parser.add_argument("--escribir", action="store_true",
                        help="escribe los archivos en las tablas de la IA")
    parser.add_argument("--borrar-huerfanos", action="store_true",
                        help="con --escribir: borra las filas regenerables de repos que salieron")
    parser.add_argument("--max-borrar", type=int, default=MAX_DELETE,
                        help=f"máximo de repos huérfanos a borrar (por defecto {MAX_DELETE})")
    parser.add_argument("--provider", default="gemini", choices=list(PROVIDERS))
    args = parser.parse_args()
    if args.borrar_huerfanos and not args.escribir:
        parser.error("--borrar-huerfanos solo va con --escribir")

    live, columns = read_view()           # se lee una vez: la comparación y la copia usan lo mismo
    published = read_published()
    plan = current_state(live, published)
    print(f"- vectores de búsqueda desactualizados en la base: {stale_vectors()} "
          "(más los de los repos que se publiquen; se calculan al escribir)")

    if args.generar and plan.needs_generate:
        for path in (ENRICHMENT_FILE, IDEAS_FILE):
            check_provider(path, args.provider)
        print()
        generate_files(plan, live, columns, args.provider)
        print("\nDespués de generar:")
        plan = current_state(live, published)   # lo que quedó: si algo falló, se ve aquí
        print("\nRevisa `git diff ai/data/catalog/`, reinicia el servicio del asistente y haz commit.")

    if args.escribir:
        if plan.needs_generate:
            fail("Los archivos no reflejan la vista: corre primero --generar (o vuelve a "
                 "correrlo si se cortó). No se escribió nada.")
        load_dotenv()
        write_database(plan, args.borrar_huerfanos, args.max_borrar)
    elif not args.generar:
        print("\nSin --generar ni --escribir no se toca nada.")


if __name__ == "__main__":
    main()
