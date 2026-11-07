"""Lote reanudable sobre el catálogo: procesa los repos uno por uno con el LLM.

Lo usan los scripts que generan datos con el modelo (enriquecimiento, ideas de
integración). Guarda cada repo apenas llega, así que una corrida cortada se retoma
donde quedó: un repo cuyo hash de entrada no cambió no se vuelve a pedir al modelo.
Si el archivo es de otra versión de las reglas, se detiene, salvo pedido explícito.
"""

import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

from ai.llm import LLMError, LLMRateLimited, LLMUnavailable
from shared.contracts.repo import Repo

WAIT_SECONDS = 30.0      # espera ante un límite por minuto que no dice cuánto esperar
MAX_WAIT_SECONDS = 120   # si el proveedor pide más, es el límite del día: se detiene
MAX_WAITS = 5            # esperas seguidas por el mismo repo antes de rendirse
REPLACE_TRIES = 5        # en Windows, un antivirus o un editor puede retener el archivo un momento
TRANSIENT_WAIT_SECONDS = 10.0  # espera ante un error temporal del proveedor (503)


def select_repos(repos: list[Repo], wanted: list[str] | None) -> list[Repo]:
    """Los repos pedidos por nombre (owner/name), o todos si no se pide ninguno.

    Termina el programa si algún nombre no está en el catálogo.
    """
    if not wanted:
        return repos
    selected = [r for r in repos if r.full_name in set(wanted)]
    missing = set(wanted) - {r.full_name for r in selected}
    if missing:
        sys.exit(f"No están en el catálogo: {', '.join(sorted(missing))}")
    return selected


def load_records(path: Path) -> dict[int, dict]:
    """Registros ya guardados, por github_id. Vacío si el archivo no existe."""
    if not path.is_file():
        return {}
    return {r["github_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))["repos"]}


def stored_version(path: Path) -> str | None:
    """Versión de las reglas con que se escribió el archivo. None si no existe."""
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("prompt_version")


def check_version(path: Path, prompt_version: str, allow_change: bool) -> None:
    """Termina el programa si el archivo es de otra versión de las reglas, salvo pedido explícito.

    Seguir regeneraría todos los repos (la versión entra en el hash de cada uno) y,
    si la corrida se corta, dejaría en el archivo registros de dos versiones.
    """
    stored = stored_version(path)
    if stored is None or stored == prompt_version or allow_change:
        return
    sys.exit(f"{path} tiene datos de la versión {stored} de las reglas y el código está en la "
             f"versión {prompt_version}: seguir regeneraría los repos con las reglas nuevas "
             "(todos, o los de --repos, y el archivo quedaría con dos versiones mezcladas).\n"
             "Si es lo que quieres, agrega --new-version. Para probar sin tocar ese archivo, "
             "usa --out con otro archivo.")


def save_records(path: Path, records: dict[int, dict], prompt_version: str) -> None:
    """Escribe todos los registros, ordenados por nombre para que el diff sea legible.

    Primero a un archivo temporal y luego se reemplaza: si el proceso se corta
    a mitad de la escritura, el archivo anterior queda intacto. En Windows, el
    reemplazo falla si otro programa tiene el archivo abierto; se reintenta unas veces.
    """
    ordered = sorted(records.values(), key=lambda r: r["full_name"].lower())
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"prompt_version": prompt_version, "repos": ordered},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for attempt in range(1, REPLACE_TRIES + 1):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == REPLACE_TRIES:
                raise PermissionError(f"No se pudo reemplazar {path}: ¿está abierto en otro "
                                      f"programa? Lo nuevo quedó en {tmp}.") from None
            time.sleep(0.5 * attempt)


def run_batch(repos: list[Repo], out: Path, prompt_version: str, *,
              current_hash: Callable[[Repo], str],
              process: Callable[[Repo], dict],
              is_done: Callable[[dict | None, str], bool],
              describe: Callable[[dict], str],
              force: bool = False,
              allow_version_change: bool = False) -> list[dict]:
    """Procesa los repos en orden y devuelve los registros de esta corrida.

    current_hash: huella de la entrada de un repo (se compara con la guardada).
    process: llama al modelo para un repo y devuelve su registro.
    is_done: si el registro guardado sirve para este hash (cada script decide qué es "hecho").
    describe: una línea con el resultado de un repo, para el progreso.
    allow_version_change: seguir aunque el archivo sea de otra versión de las reglas.
    Ante el límite del día guarda lo hecho y termina el programa.
    """
    check_version(out, prompt_version, allow_version_change)
    records = load_records(out)
    done = []
    for n, repo in enumerate(repos, start=1):
        prefix = f"[{n}/{len(repos)}] {repo.full_name}"
        if not force and is_done(records.get(repo.github_id), current_hash(repo)):
            print(f"{prefix}: sin cambios, se salta")
            done.append(records[repo.github_id])
            continue
        for _ in range(MAX_WAITS):
            try:
                record = process(repo)
                break
            except LLMRateLimited as err:
                wait = err.retry_after or WAIT_SECONDS
                if wait > MAX_WAIT_SECONDS:
                    save_records(out, records, prompt_version)
                    sys.exit(f"{err}\nParece el límite del día. Lo hecho quedó guardado: "
                             "vuelve a correr el mismo comando más tarde.")
                print(f"    límite por minuto: espero {wait:.0f} s")
                time.sleep(wait)
            except LLMUnavailable as err:
                if not err.transient:
                    print(f"{prefix}: ERROR {err}")
                    record = None
                    break
                print(f"    error temporal del proveedor: espero {TRANSIENT_WAIT_SECONDS:.0f} s")
                time.sleep(TRANSIENT_WAIT_SECONDS)
            except LLMError as err:
                print(f"{prefix}: ERROR {err} (se reintenta en otra corrida)")
                record = None
                break
        else:
            sys.exit("Demasiadas esperas seguidas; lo hecho quedó guardado.")
        if record is None:
            continue
        records[repo.github_id] = record
        save_records(out, records, prompt_version)
        done.append(record)
        print(f"{prefix}: {describe(record)}")
    return done
