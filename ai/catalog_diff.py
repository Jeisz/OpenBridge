"""Compara el catálogo de la vista con lo que tiene la IA y dice qué hay que actualizar.

No lee archivos ni la base: recibe los datos ya cargados. Así sirve igual si lo que
tiene la IA viene de los archivos del repo o de las tablas de la IA.

Qué compara, por github_id (no cambia aunque el repo cambie de nombre):
- repos nuevos, eliminados y renombrados frente al catálogo que usa la IA;
- si la huella guardada de cada dato de la IA (enriquecimiento, ideas) sigue saliendo de
  lo que lee el modelo hoy. Se recalcula con la versión de las reglas y el proveedor del
  registro, así solo cuenta un cambio de la entrada; un cambio de reglas lo decide el
  guard de versión del lote, no esta comparación;
- cambios de `archived` (un repo archivado queda sin ideas sin llamar al modelo);
- en cada registro de la IA, el nombre y el estado de archivado con que se generó: así la
  comparación no "olvida" un renombrado o un archivado cuando el snapshot ya se refrescó
  y una corrida anterior se cortó antes de regenerar;
- el resto de campos de la ingesta (estrellas, licencia, fechas): solo hay que refrescar la copia.
"""

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from ai.enrich import input_hash, readme_input, user_message
from ai.ideas import ideas_input
from ai.llm import PROVIDERS
from shared.contracts.repo import Repo

AI_FIELDS = {"categories", "summary_es", "use_cases"}   # los escribe la IA, no la ingesta

NO_RECORD = "sin datos de la IA"
INPUT_CHANGED = "cambió lo que lee el modelo"
OTHER_MODEL = "el registro es de otro modelo"
NAME_CHANGED = "el registro tiene otro nombre del repo"
ARCHIVED_CHANGED = "cambió archived"

ARCHIVED_SKIP = "repo archivado"   # así marca ai.ideas un repo archivado (sin llamar al modelo)


def enrichment_message(repo: Repo) -> str:
    """Lo que lee el modelo para enriquecer un repo (como en ai.scripts.enrich_catalog)."""
    return user_message(repo, readme_input(repo))


def ideas_message(repo: Repo) -> str:
    """Lo que lee el modelo para las ideas de un repo (como en ai.scripts.generate_ideas)."""
    return user_message(repo, ideas_input(repo).text)


def with_unix_newlines(repo: Repo) -> Repo:
    """El repo con los saltos de línea del README como los deja el snapshot (\\n).

    Al leer un archivo, Python convierte \\r\\n en \\n; la base devuelve el texto tal cual.
    Sin esto, un README igual daría otra huella.
    """
    text = repo.readme_text
    if not text or "\r" not in text:
        return repo
    return repo.model_copy(update={"readme_text": text.replace("\r\n", "\n")})


def stale_reason(repo: Repo, record: dict | None, message_of: Callable[[Repo], str]) -> str | None:
    """None si el registro sigue al día para este repo; si no, el motivo."""
    if record is None:
        return NO_RECORD
    spec = PROVIDERS.get(record["provider"])
    if spec is None or spec.model != record["model"]:
        return OTHER_MODEL
    expected = input_hash(message_of(repo), record["provider"], record["prompt_version"])
    if expected != record["ai_input_hash"]:
        return INPUT_CHANGED
    if record["full_name"] != repo.full_name:
        return NAME_CHANGED
    return None


def ideas_stale_reason(repo: Repo, record: dict | None) -> str | None:
    """Como `stale_reason`, más el archivado: las ideas de un repo archivado se vacían y las
    de un repo que deja de estarlo se generan. `archived` no entra en la huella."""
    reason = stale_reason(repo, record, ideas_message)
    if reason is None and (record["review"].get("skipped") == ARCHIVED_SKIP) != repo.archived:
        return ARCHIVED_CHANGED
    return reason


@dataclass(frozen=True)
class CatalogDiff:
    """Diferencias entre la vista y lo que tiene la IA. Listas ordenadas por nombre."""

    new: list[Repo] = field(default_factory=list)
    removed: list[Repo] = field(default_factory=list)
    renamed: list[tuple[Repo, Repo]] = field(default_factory=list)   # (antes, ahora)
    archived_changed: list[Repo] = field(default_factory=list)
    enrichment_stale: list[tuple[Repo, str]] = field(default_factory=list)   # (repo, motivo)
    ideas_stale: list[tuple[Repo, str]] = field(default_factory=list)
    orphans: dict[str, list[int]] = field(default_factory=dict)   # github_id sin repo en la vista
    field_changes: dict[str, int] = field(default_factory=dict)   # campo → repos que cambiaron

    @property
    def has_changes(self) -> bool:
        return any((self.new, self.removed, self.renamed, self.archived_changed,
                    self.enrichment_stale, self.ideas_stale, self.field_changes,
                    any(self.orphans.values())))


def _by_name(repos: Iterable[Repo]) -> list[Repo]:
    return sorted(repos, key=lambda r: r.full_name.lower())


def _stale(repos: list[Repo], records: dict[int, dict],
           reason_of: Callable[[Repo, dict | None], str | None]) -> list[tuple[Repo, str]]:
    found = [(r, reason_of(r, records.get(r.github_id))) for r in repos]
    return [(r, reason) for r, reason in found if reason is not None]


def enrichment_stale_reason(repo: Repo, record: dict | None) -> str | None:
    return stale_reason(repo, record, enrichment_message)


def diff_catalog(live: list[Repo], known: list[Repo],
                 enrichment: dict[int, dict], ideas: dict[int, dict]) -> CatalogDiff:
    """Compara la vista (`live`) con el catálogo que usa la IA (`known`) y sus registros.

    enrichment, ideas: registros de la IA por github_id, con provider, model,
    prompt_version y ai_input_hash (como los guarda el lote).
    """
    live_by = {r.github_id: r for r in live}
    known_by = {r.github_id: r for r in known}
    common = [live_by[i] for i in live_by.keys() & known_by.keys()]

    changes: Counter[str] = Counter()
    for repo in common:
        now = repo.model_dump(mode="json", exclude=AI_FIELDS)
        before = known_by[repo.github_id].model_dump(mode="json", exclude=AI_FIELDS)
        changes.update(name for name in now if now[name] != before[name])

    live_repos = _by_name(live_by.values())
    return CatalogDiff(
        new=_by_name(live_by[i] for i in live_by.keys() - known_by.keys()),
        removed=_by_name(known_by[i] for i in known_by.keys() - live_by.keys()),
        renamed=[(known_by[r.github_id], r) for r in _by_name(common)
                 if r.full_name != known_by[r.github_id].full_name],
        archived_changed=[r for r in _by_name(common)
                          if r.archived != known_by[r.github_id].archived],
        enrichment_stale=_stale(live_repos, enrichment, enrichment_stale_reason),
        ideas_stale=_stale(live_repos, ideas, ideas_stale_reason),
        orphans={"enriquecimiento": sorted(enrichment.keys() - live_by.keys()),
                 "ideas": sorted(ideas.keys() - live_by.keys())},
        field_changes=dict(sorted(changes.items())),
    )
