#!/usr/bin/env python
"""Coordinador de sincronización diaria del catálogo OpenBridge.

Flujo: configuración → lista aprobada → extracción → transformación →
validación → hashes → lectura del destino → plan → (opcional) aplicación
transaccional → verificación → resumen.

Modo predeterminado: ``--dry-run`` (cero escrituras). Sin ``--live`` no se
realiza ninguna petición HTTP ni conexión SQL. ``--apply`` exige destino
habilitado y confirmación explícita por variables de entorno.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from extract_github import fetch_repositories  # noqa: E402
from hash_contract import (  # noqa: E402
    HASH_VERSION,
    ContentHashError,
    content_hash_v1,
)
from load import LoadPlanError  # noqa: E402
from sync_config import (  # noqa: E402
    GITHUB_TOKEN_ENV,
    TARGET_ENV,
    WRITES_ENABLED_ENV,
    WRITE_CONFIRMATION_ENV,
    DatabaseTarget,
    SyncConfigError,
    create_target_engine,
    is_admin_user,
    load_approved_repositories,
    load_target,
    redact,
)
from sync_load import (  # noqa: E402
    SYNC_WRITE_CONFIRMATION,
    apply_sync_plan,
    read_catalog_state,
    verify_sync_result,
)
from sync_plan import (  # noqa: E402
    SyncPlan,
    SyncPlanError,
    build_sync_plan,
    validate_plan,
)
from transform import TransformationError, transform_records  # noqa: E402

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_WARNINGS = 3
EXIT_WRITE_BLOCKED = 4

CONFIRMED_MISSING = "NO_ENCONTRADO"


@dataclass(frozen=True)
class Preflight:
    """Conteos previos al plan, disponibles incluso sin base de datos."""

    approved: int
    extracted: int
    readme_available: int
    readme_confirmed_missing: int
    readme_unresolved: int
    hash_ready: int
    missing: tuple[str, ...]


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sincronización incremental del catálogo OpenBridge"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="autoriza solicitudes HTTP reales y conexiones SQL",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="solo planifica y compara (predeterminado)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help=(
            "aplica el plan; requiere OPENBRIDGE_SYNC_ALLOW_WRITES=1 y "
            "OPENBRIDGE_SYNC_CONFIRMATION"
        ),
    )
    parser.add_argument(
        "--target",
        choices=("local", "supabase"),
        default=None,
        help="destino autorizado (por defecto OPENBRIDGE_SYNC_TARGET)",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="no abre conexiones; ejecuta extracción/transformación/validación",
    )
    parser.add_argument(
        "--repositories",
        default=None,
        help="ruta de la lista aprobada (por defecto la lista de 100)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="procesa solo los primeros N repositorios aprobados",
    )
    parser.add_argument(
        "--summary-file",
        default=None,
        help="escribe el resumen saneado en un archivo (Markdown)",
    )
    args = parser.parse_args(list(argv))
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit debe ser un entero positivo")
    return args


def _missing_approved(
    approved: Sequence[str], records: Sequence[Mapping[str, Any]]
) -> tuple[str, ...]:
    extracted = {
        str(record.get("full_name", "")).casefold()
        for record in records
        if isinstance(record.get("full_name"), str)
    }
    return tuple(name for name in approved if name.casefold() not in extracted)


def _audit_stats(audit: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(audit)
    success = sum(1 for row in audit if row.get("success"))
    quota = sum(1 for row in audit if row.get("http_status") in (403, 429))
    error_types = sorted(
        {
            str(row.get("error_type"))
            for row in audit
            if not row.get("success") and row.get("error_type")
        }
    )
    return {
        "total": total,
        "success": success,
        "errors": total - success,
        "quota": quota,
        "error_types": error_types,
    }


def _preflight(
    result,
    approved: Sequence[str],
    missing: Sequence[str],
) -> Preflight:
    """Comprueba que cada repositorio resuelto produce un hash v1 válido."""
    repositories = {repo["github_id"]: repo for repo in result.repositories}
    readmes = {item["github_id"]: item["readme_text"] for item in result.readmes}
    statuses = {
        str(observation.get("full_name", "")).casefold(): observation.get(
            "readme_status"
        )
        for observation in result.observations
    }
    available = len(readmes)
    confirmed = 0
    hash_ready = 0
    for identifier, repository in repositories.items():
        text = readmes.get(identifier)
        if text is None:
            status = statuses.get(str(repository["full_name"]).casefold())
            if status != CONFIRMED_MISSING:
                continue
            confirmed += 1
        try:
            content_hash_v1(repository, text)
        except ContentHashError:
            continue
        hash_ready += 1
    unresolved = len(repositories) - available - confirmed
    return Preflight(
        approved=len(approved),
        extracted=len(repositories),
        readme_available=available,
        readme_confirmed_missing=confirmed,
        readme_unresolved=unresolved,
        hash_ready=hash_ready,
        missing=tuple(missing),
    )


def _write_gate(
    environ: Mapping[str, str], target: DatabaseTarget | None
) -> str | None:
    """Motivo por el que se bloquea la escritura, o ``None`` si está permitida."""
    enabled = str(environ.get(WRITES_ENABLED_ENV, "")).strip()
    if enabled != "1":
        return (
            "escrituras deshabilitadas; defina "
            f"{WRITES_ENABLED_ENV}=1 solo tras la aprobación explícita"
        )
    confirmation = str(environ.get(WRITE_CONFIRMATION_ENV, "")).strip()
    if confirmation != SYNC_WRITE_CONFIRMATION:
        return (
            "falta la confirmación explícita de sincronización en "
            f"{WRITE_CONFIRMATION_ENV}"
        )
    if target is None:
        return "no hay destino validado"
    if not target.writes_allowed:
        return "el destino no está habilitado para escritura"
    if is_admin_user(target.user):
        return "no se admite una cuenta administrativa"
    return None


def _safe_error(
    exc: BaseException, *secrets: str | None
) -> str:
    return redact(f"{type(exc).__name__}: {exc}", *secrets)


def _dispose(engine: Any) -> None:
    dispose = getattr(engine, "dispose", None)
    if callable(dispose):
        dispose()


def _write_summary(path: str | None, report: str, *secrets: str | None) -> None:
    if not path:
        return
    try:
        Path(path).write_text(redact(report, *secrets) + "\n", encoding="utf-8")
        print(f"Resumen saneado escrito en {Path(path).name}")
    except OSError as exc:
        print(f"ADVERTENCIA: no se pudo escribir el resumen ({type(exc).__name__})")


def _header(target: DatabaseTarget | None, apply_mode: bool) -> list[str]:
    mode = "ESCRITURA AUTORIZADA (--apply)" if apply_mode else "SOLO LECTURA (dry-run)"
    destination = target.describe() if target is not None else "no comparado"
    return [
        "OpenBridge — sincronización de catálogo",
        f"Contrato de hash: {HASH_VERSION}",
        f"Modo: {mode}",
        f"Destino: {destination}",
    ]


def _stats_lines(preflight: Preflight, stats: Mapping[str, Any]) -> list[str]:
    return [
        f"Repositorios aprobados: {preflight.approved} | "
        f"extraídos: {preflight.extracted}",
        f"README disponibles: {preflight.readme_available} | "
        f"404 confirmados: {preflight.readme_confirmed_missing} | "
        f"no verificables: {preflight.readme_unresolved}",
        f"Hashes v1 verificables: {preflight.hash_ready}/{preflight.extracted}",
        f"HTTP: {stats.get('success', 0)}/{stats.get('total', 0)} correctas | "
        f"errores: {stats.get('errors', 0)} | respuestas 403/429: "
        f"{stats.get('quota', 0)}",
    ]


def _preflight_report(
    preflight: Preflight,
    target: DatabaseTarget | None,
    apply_mode: bool,
    stats: Mapping[str, Any],
    reason: str,
) -> str:
    lines = _header(target, apply_mode)
    lines.extend(_stats_lines(preflight, stats))
    lines.append(f"Comparación con el destino: OMITIDA ({reason})")
    if preflight.missing:
        lines.append(
            "Repositorios aprobados sin metadatos: " + ", ".join(preflight.missing)
        )
    lines.append(
        "Completitud: INCOMPLETA"
        if preflight.missing or preflight.readme_unresolved
        else "Completitud: completa (sin comparar el catálogo)"
    )
    lines.append("0 escrituras ejecutadas: no se generó ni aplicó ningún plan.")
    return "\n".join(lines)


def _plan_report(
    plan: SyncPlan,
    preflight: Preflight,
    target: DatabaseTarget | None,
    apply_mode: bool,
    stats: Mapping[str, Any],
) -> str:
    lines = _header(target, apply_mode)
    lines.extend(_stats_lines(preflight, stats))
    lines.append("")
    lines.append("Acción por repositorio (repo | readme | motivos):")
    for action in plan.actions:
        lines.append(
            f"- {action.full_name} | {action.repository_action} | "
            f"{action.readme_action} | {','.join(action.reasons)}"
        )
    lines.append("")
    lines.append(
        "Repositorios: INSERT={} UPDATE={} sin_cambios={} preservados={}".format(
            plan.inserted_repositories,
            plan.updated_repositories,
            plan.unchanged_repositories,
            plan.preserved_repositories,
        )
    )
    lines.append(
        "READMEs: INSERT={} UPDATE={} sin_cambios={} preservados={}".format(
            plan.inserted_readmes,
            plan.updated_readmes,
            plan.unchanged_readmes,
            plan.preserved_readmes,
        )
    )
    lines.append(f"Escrituras planificadas: {plan.writes}")
    if plan.missing_repositories:
        lines.append(
            "Faltan repositorios aprobados: "
            + ", ".join(plan.missing_repositories)
        )
    if plan.unresolved_readme:
        lines.append("README no verificable: " + ", ".join(plan.unresolved_readme))
    if plan.legacy_backfill_ids:
        lines.append(
            f"Hashes históricos sin versión a recalcular con {HASH_VERSION}: "
            f"{plan.backfilled_repositories} (IDs: "
            + ", ".join(str(item) for item in plan.legacy_backfill_ids)
            + ")"
        )
    if plan.unsupported_version_ids:
        lines.append(
            "Hashes con versión no soportada preservados (IDs): "
            + ", ".join(str(item) for item in plan.unsupported_version_ids)
        )
    if plan.inconsistent_hash_ids:
        lines.append(
            "Hashes inconsistentes preservados (IDs): "
            + ", ".join(str(item) for item in plan.inconsistent_hash_ids)
        )
    if plan.warnings:
        lines.append("Advertencias:")
        lines.extend(f"  - {warning}" for warning in plan.warnings)
    lines.append(
        "Completitud: INCOMPLETA" if plan.incomplete else "Completitud: completa"
    )
    if not apply_mode:
        lines.append("0 escrituras ejecutadas (dry-run).")
    else:
        lines.append("Escritura habilitada: se aplicará en una única transacción.")
    return "\n".join(lines)


def run(
    argv: Sequence[str],
    *,
    environ: Mapping[str, str] | None = None,
    fetcher: Callable[..., Any] | None = None,
    engine_factory: Callable[..., Any] | None = None,
) -> int:
    """Ejecuta el coordinador y devuelve el código de salida."""
    environment: Mapping[str, str] = dict(
        os.environ if environ is None else environ
    )
    fetch = fetch_repositories if fetcher is None else fetcher
    factory = create_target_engine if engine_factory is None else engine_factory
    args = _parse_args(argv)
    apply_mode = bool(args.apply)
    token = environment.get(GITHUB_TOKEN_ENV) or None

    if not args.live:
        print("\n".join(_header(None, apply_mode)))
        print("MODO SEGURO: 0 solicitudes HTTP y 0 conexiones SQL.")
        print(
            "Añada --live para ejecutar las fases reales; el modo "
            "predeterminado seguirá siendo --dry-run."
        )
        return EXIT_OK
    if apply_mode and args.skip_db:
        print("ERROR: --apply no puede combinarse con --skip-db")
        return EXIT_USAGE

    try:
        approved = load_approved_repositories(args.repositories)
    except SyncConfigError as exc:
        print(f"ERROR: {redact(exc, token)}")
        return EXIT_USAGE
    if args.limit is not None:
        approved = approved[: args.limit]
    if not approved:
        print("ERROR: no hay repositorios aprobados para procesar")
        return EXIT_USAGE
    print(f"Repositorios seleccionados: {len(approved)}")

    env_target = str(environment.get(TARGET_ENV, "")).strip() or None
    target_name = args.target or env_target
    target: DatabaseTarget | None = None
    target_problem = ""
    if args.skip_db:
        target_problem = "comparación omitida por --skip-db"
    elif target_name is None:
        target_problem = f"sin destino configurado ({TARGET_ENV} o --target)"
    else:
        try:
            target = load_target(target_name, environ=environment)
        except SyncConfigError as exc:
            target_problem = redact(exc, token)
    if apply_mode and target is None:
        print(f"ERROR: --apply requiere un destino válido: {target_problem}")
        return EXIT_USAGE

    secrets: tuple[str | None, ...] = (
        token,
        target.password if target is not None else None,
    )
    if apply_mode:
        gate = _write_gate(environment, target)
        if gate:
            print(f"ESCRITURA BLOQUEADA: {gate}")
            print("No se realizó ninguna petición HTTP ni conexión SQL.")
            return EXIT_WRITE_BLOCKED

    print(f"Extrayendo {len(approved)} repositorios desde GitHub...")
    try:
        records, audit = fetch(
            approved,
            enabled=True,
            include_readme=True,
            token=token,
            approved_repositories=approved,
        )
    except Exception as exc:  # noqa: BLE001 - se reporta sin credenciales
        print(f"ERROR de extracción: {_safe_error(exc, *secrets)}")
        return EXIT_ERROR

    stats = _audit_stats(audit)
    missing = _missing_approved(approved, records)
    try:
        result = transform_records(records)
    except (TransformationError, ValueError) as exc:
        print(f"ERROR de transformación (0 escrituras): {redact(exc, *secrets)}")
        return EXIT_ERROR

    preflight = _preflight(result, approved, missing)
    if target is None:
        report = _preflight_report(
            preflight, target, apply_mode, stats, target_problem
        )
        print(redact(report, *secrets))
        _write_summary(args.summary_file, report, *secrets)
        return EXIT_WARNINGS

    read_engine = None
    try:
        read_engine = factory(target, read_only=True)
        state = read_catalog_state(read_engine)
    except Exception as exc:  # noqa: BLE001
        print(f"ADVERTENCIA: no se pudo leer el catálogo: {_safe_error(exc, *secrets)}")
        report = _preflight_report(
            preflight, target, apply_mode, stats, "error de lectura del destino"
        )
        print(redact(report, *secrets))
        _write_summary(args.summary_file, report, *secrets)
        return EXIT_ERROR if apply_mode else EXIT_WARNINGS
    finally:
        if read_engine is not None:
            _dispose(read_engine)

    try:
        plan = build_sync_plan(result, state, approved=approved)
        validate_plan(plan)
    except (SyncPlanError, ContentHashError) as exc:
        print(f"ERROR de planificación: {redact(exc, *secrets)}")
        return EXIT_ERROR

    report = _plan_report(plan, preflight, target, apply_mode, stats)
    print(redact(report, *secrets))

    if apply_mode:
        write_engine = None
        try:
            write_engine = factory(target, read_only=False)
            summary = apply_sync_plan(
                write_engine,
                plan,
                target=target,
                authorization=str(
                    environment.get(WRITE_CONFIRMATION_ENV, "")
                ).strip(),
            )
        except (PermissionError, SyncConfigError, LoadPlanError, SyncPlanError) as exc:
            print(f"ERROR de aplicación (transacción revertida): {redact(exc, *secrets)}")
            return EXIT_ERROR
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR inesperado de aplicación: {_safe_error(exc, *secrets)}")
            return EXIT_ERROR
        finally:
            if write_engine is not None:
                _dispose(write_engine)

        print("Aplicado: " + summary.to_line())
        verify_engine = None
        problems: tuple[str, ...] | None = None
        try:
            verify_engine = factory(target, read_only=True)
            problems = verify_sync_result(verify_engine, plan)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR de verificación posterior: {_safe_error(exc, *secrets)}")
        finally:
            if verify_engine is not None:
                _dispose(verify_engine)

        if problems is None:
            return EXIT_ERROR
        if problems:
            print("VERIFICACIÓN FALLIDA:")
            for problem in problems:
                print(f"  - {redact(problem, *secrets)}")
            return EXIT_ERROR
        print("Verificación posterior: hashes y READMEs coinciden con el plan.")
        report = "\n".join(
            [
                report,
                "Resultado: " + summary.to_line(),
                "Verificación posterior: correcta.",
            ]
        )

    _write_summary(args.summary_file, report, *secrets)
    return EXIT_WARNINGS if plan.incomplete else EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
