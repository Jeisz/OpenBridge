"""OpenBridge: planificación y carga transaccional controlada, v0.2.

CLI siempre es SOLO LECTURA (sin --live: 0 HTTP y 0 SQL).
La API de escritura exige autorización independiente y el esquema aprobado.
Ninguna importación o ejecución CLI ejecuta DDL, INSERT, UPDATE o DELETE.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Mapping

from sqlalchemy import ARRAY, Text, bindparam, text

from extract_github import APPROVED_REPOSITORIES, fetch_repositories
from transform import TransformationResult, transform_records
from hash_contract import (HASH_VERSION, HashPreview, content_hash_v1,
                           preview_transformation_hashes)


class LoadPlanError(ValueError):
    """Entrada o estado de catálogo incompatible con una carga segura."""


@dataclass(frozen=True)
class CatalogSnapshot:
    # github_id -> full_name observado actualmente en PostgreSQL
    repository_names: Mapping[int, str | None]
    readme_ids: frozenset[int]


@dataclass(frozen=True)
class LoadPlan:
    # Filas únicamente descriptivas. No se convierten en sentencias SQL.
    rows: list[dict[str, Any]]
    observations: list[dict[str, str]]
    existing_repositories: int
    new_repositories: int
    existing_readmes: int
    new_readmes: int
    missing_readmes: int
    identity_warnings: int


def read_catalog_snapshot(engine: Any) -> CatalogSnapshot:
    """Consulta exclusivamente SELECT bajo una transacción READ ONLY de PostgreSQL.

    No usa reflexión, DDL ni tablas auxiliares. Este método requiere PostgreSQL.
    """
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("SET TRANSACTION READ ONLY"))
            repos = conn.execute(text(
                "SELECT github_id, full_name FROM public.catalog_repositories"
            )).mappings().all()
            readmes = conn.execute(text(
                "SELECT github_id FROM public.catalog_readmes"
            )).mappings().all()

    repository_names: dict[int, str | None] = {}
    for row in repos:
        identifier = row["github_id"]
        if type(identifier) is not int or identifier <= 0:
            raise LoadPlanError("Identificador anómalo en catalog_repositories")
        if identifier in repository_names:
            raise LoadPlanError("ID duplicado en catálogo (inesperado con PK)")
        repository_names[identifier] = row["full_name"]

    readme_ids: set[int] = set()
    for row in readmes:
        identifier = row["github_id"]
        if type(identifier) is not int or identifier <= 0:
            raise LoadPlanError("Identificador anómalo en catalog_readmes")
        if identifier not in repository_names:
            raise LoadPlanError("README huérfano en el catálogo")
        readme_ids.add(identifier)
    return CatalogSnapshot(repository_names, frozenset(readme_ids))


def plan_load(result: TransformationResult, snapshot: CatalogSnapshot) -> LoadPlan:
    """Compara filas transformadas y catálogo existente: NUNCA escribe SQL.

    Los datos antiguos quedan marcados como conservación total: no se realiza
    UPSERT de metadatos ni de README hasta acordar el contrato hash con IA.
    """
    if not isinstance(result, TransformationResult):
        raise LoadPlanError("Se requiere TransformationResult válido")
    if not isinstance(snapshot, CatalogSnapshot):
        raise LoadPlanError("Se requiere CatalogSnapshot válido")

    repo_ids: set[int] = set()
    readme_ids: set[int] = set()
    for repo in result.repositories:
        identifier = repo.get("github_id")
        if type(identifier) is not int or identifier <= 0 or identifier in repo_ids:
            raise LoadPlanError("Identificador ausente, inválido o duplicado en repositorios")
        name = repo.get("full_name")
        if not isinstance(name, str) or not name.strip():
            raise LoadPlanError("full_name ausente o inválido")
        if "content_hash" in repo:
            raise LoadPlanError("content_hash no debe venir de una transformación no aprobada")
        repo_ids.add(identifier)
    for readme in result.readmes:
        identifier = readme.get("github_id")
        if type(identifier) is not int or identifier in readme_ids or identifier not in repo_ids:
            raise LoadPlanError("README duplicado o sin repositorio transformado")
        if not isinstance(readme.get("readme_text"), str):
            raise LoadPlanError("README disponible sin texto válido")
        readme_ids.add(identifier)

    rows: list[dict[str, Any]] = []
    existing_repo = new_repo = existing_readmes = new_readmes = missing = warnings = 0
    for repo in result.repositories:
        identifier = repo["github_id"]
        name = repo["full_name"]
        exists = identifier in snapshot.repository_names
        if exists:
            existing_repo += 1
        else:
            new_repo += 1

        previous = snapshot.repository_names.get(identifier)
        different_name = exists and (not isinstance(previous, str) or name.casefold() != previous.casefold())
        if different_name:
            warnings += 1
        readme_extracted = identifier in readme_ids
        readme_exists = identifier in snapshot.readme_ids
        if readme_exists:
            existing_readmes += 1
        elif readme_extracted:
            new_readmes += 1
        else:
            missing += 1

        rows.append({
            "github_id": identifier,
            "full_name": name,
            "repo_plan": "CONSERVAR" if exists else "INSERTAR_PENDIENTE_HASH",
            "readme_plan": (
                "CONSERVAR" if readme_exists else
                "INSERTAR_PENDIENTE_HASH" if readme_extracted else
                "SIN_README_DISPONIBLE"
            ),
            "identity_warning": bool(different_name),
        })
    return LoadPlan(rows, list(result.observations), existing_repo, new_repo,
                    existing_readmes, new_readmes, missing, warnings)


# Esta frase no es una credencial. Es un seguro contra llamadas accidentales.
# Su uso sigue requiriendo autorización HUMANA expresa para la primera escritura.
WRITE_CONFIRMATION = "CONFIRMO_INSERCION_NUEVOS_OPENBRIDGE_V1"
EXPECTED_DATABASE = "openbridge_db"


@dataclass(frozen=True)
class PreparedBatch:
    """Instantánea de inserciones propuestas; los históricos se excluyen."""
    repositories: tuple[dict[str, Any], ...]
    readmes_by_id: Mapping[int, str]
    hashes_by_id: Mapping[int, HashPreview]
    preserved_repositories: int
    preserved_readmes: int


@dataclass(frozen=True)
class InsertSummary:
    inserted_repositories: int
    inserted_readmes: int
    skipped_existing: int


def prepare_write_batch(result: TransformationResult, snapshot: CatalogSnapshot) -> PreparedBatch:
    """Prepara en memoria un lote exclusivo de INSERT, sin I/O.

    Los hashes se calculan a partir de la transformación, nunca se aceptan
    hashes externos. README 404 verificado se representa por null en el hash.
    """
    plan = plan_load(result, snapshot)
    if plan.identity_warnings:
        raise LoadPlanError("Alerta de identidad; no se permite preparar escrituras")
    previews = preview_transformation_hashes(result)
    hash_by_id = {item.github_id: item for item in previews}
    readmes_by_id = {item["github_id"]: item["readme_text"] for item in result.readmes}

    seen_existing_names = {
        name.casefold(): identifier
        for identifier, name in snapshot.repository_names.items()
        if isinstance(name, str)
    }
    newcomers = []
    for repo in result.repositories:
        identifier = repo["github_id"]
        if identifier in snapshot.repository_names:
            continue
        other = seen_existing_names.get(repo["full_name"].casefold())
        if other is not None and other != identifier:
            raise LoadPlanError("full_name ya pertenece a otro github_id en el catálogo")
        newcomers.append(dict(repo))

    return PreparedBatch(
        repositories=tuple(newcomers),
        readmes_by_id={r["github_id"]: readmes_by_id[r["github_id"]]
                       for r in newcomers if r["github_id"] in readmes_by_id},
        hashes_by_id={r["github_id"]: hash_by_id[r["github_id"]] for r in newcomers},
        preserved_repositories=plan.existing_repositories,
        preserved_readmes=plan.existing_readmes,
    )


def _snapshot_in_transaction(conn: Any) -> CatalogSnapshot:
    """Lecturas de coherencia dentro de la MISMA transacción de escritura."""
    repo_rows = conn.execute(text(
        "SELECT github_id, full_name FROM public.catalog_repositories"
    )).mappings().all()
    readme_rows = conn.execute(text(
        "SELECT github_id FROM public.catalog_readmes"
    )).mappings().all()
    names: dict[int, str | None] = {}
    for row in repo_rows:
        identifier = row["github_id"]
        if type(identifier) is not int or identifier <= 0 or identifier in names:
            raise LoadPlanError("Catálogo incompatible: github_id duplicado o inválido")
        names[identifier] = row["full_name"]
    readme_ids: set[int] = set()
    for row in readme_rows:
        identifier = row["github_id"]
        if type(identifier) is not int or identifier not in names:
            raise LoadPlanError("README huérfano o ID inválido en PostgreSQL")
        readme_ids.add(identifier)
    return CatalogSnapshot(names, frozenset(readme_ids))


def insert_new_batch(
    engine: Any,
    prepared: PreparedBatch,
    *,
    authorization: str = "",
    expected_database: str = EXPECTED_DATABASE,
) -> InsertSummary:
    """API explícita para insertar SOLO nuevos IDs en una transacción.

    No hay ruta CLI hacia esta función. DDL debe aprobarse y ejecutarse antes
    por separado. ON CONFLICT DO NOTHING evita sobrescribir filas históricas.
    """
    if authorization != WRITE_CONFIRMATION:
        raise PermissionError("Escritura bloqueada: requiere autorización explícita")
    if not isinstance(prepared, PreparedBatch):
        raise LoadPlanError("Se requiere PreparedBatch validado")
    if expected_database != EXPECTED_DATABASE:
        raise LoadPlanError("Nombre de base de datos diferente del entorno aprobado")

    # Verificación de contenido antes de abrir conexión SQL.
    identifiers: set[int] = set()
    prepared_names: set[str] = set()
    for repo in prepared.repositories:
        identifier = repo.get("github_id")
        if type(identifier) is not int or identifier <= 0 or identifier in identifiers:
            raise LoadPlanError("github_id inválido o duplicado en lote")
        identifiers.add(identifier)
        name = repo.get("full_name")
        if not isinstance(name, str) or not name.strip() or name.casefold() in prepared_names:
            raise LoadPlanError("full_name inválido o duplicado en lote")
        prepared_names.add(name.casefold())
        preview = prepared.hashes_by_id.get(identifier)
        if not isinstance(preview, HashPreview) or preview.content_hash_version != HASH_VERSION:
            raise LoadPlanError("Versión del hash ausente o incompatible")
        if preview.full_name != name:
            raise LoadPlanError("Hash asociado a identidad diferente")
        content = prepared.readmes_by_id.get(identifier)
        if content is not None and not isinstance(content, str):
            raise LoadPlanError("README incompatible")
        status = "DISPONIBLE" if identifier in prepared.readmes_by_id else "NO_ENCONTRADO"
        if preview.readme_state != status:
            raise LoadPlanError("Estado de README diferente del utilizado en hash")
        if content_hash_v1(repo, content) != preview.content_hash:
            raise LoadPlanError("Hash v1 no corresponde a metadatos y README")
    if set(prepared.hashes_by_id) != identifiers or not set(prepared.readmes_by_id).issubset(identifiers):
        raise LoadPlanError("Lote de hashes/README no coincide con repositorios")

    inserted_repos = inserted_readmes = skipped = 0
    with engine.begin() as conn:
        current_db = conn.execute(text("SELECT current_database()" )).scalar_one()
        if current_db != EXPECTED_DATABASE:
            raise LoadPlanError("Conexión a base de datos inesperada: se bloqueó escritura")
        version_column = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'catalog_repositories'
              AND column_name = 'content_hash_version'
        """)).scalar_one()
        if version_column != 1:
            raise LoadPlanError("La migración content_hash_version no está aplicada")

        actual = _snapshot_in_transaction(conn)
        catalog_names = {name.casefold(): identifier
                         for identifier, name in actual.repository_names.items()
                         if isinstance(name, str)}
        for repo in prepared.repositories:
            identifier = repo["github_id"]
            name = repo["full_name"]
            previous_name = actual.repository_names.get(identifier)
            if identifier in actual.repository_names:
                if not isinstance(previous_name, str) or previous_name.casefold() != name.casefold():
                    raise LoadPlanError("Conflicto de identidad concurrente: github_id")
                skipped += 1
                continue
            other = catalog_names.get(name.casefold())
            if other is not None and other != identifier:
                raise LoadPlanError("Conflicto de identidad: full_name pertenece a otro ID")
            preview = prepared.hashes_by_id[identifier]
            values = dict(repo)
            # En tabla TEXT guardamos la sintaxis de arreglo de PostgreSQL.
            # El adaptador convierte la lista en TEXT[], y PostgreSQL la serializa
            # a TEXT para mantener compatibilidad con r.topics::TEXT[] en la vista.
            values["topics"] = sorted(repo["topics"])
            values["content_hash"] = preview.content_hash
            values["content_hash_version"] = HASH_VERSION
            row = conn.execute(text("""
                INSERT INTO public.catalog_repositories (
                    github_id, full_name, name, description, homepage, language,
                    topics, stargazers_count, forks_count, pushed_at,
                    archived, license_spdx_id, content_hash, content_hash_version
                ) VALUES (
                    :github_id, :full_name, :name, :description, :homepage, :language,
                    CAST(:topics AS TEXT[])::TEXT, :stargazers_count,
                    :forks_count, :pushed_at, :archived, :license_spdx_id,
                    :content_hash, :content_hash_version
                ) ON CONFLICT (github_id) DO NOTHING RETURNING github_id
            """).bindparams(bindparam("topics", type_=ARRAY(Text()))), values).scalar_one_or_none()
            if row is None:
                # La inserción perdió una carrera. No tocar una identidad ajena.
                concurrent_name = conn.execute(text(
                    "SELECT full_name FROM public.catalog_repositories WHERE github_id = :github_id"
                ), {"github_id": identifier}).scalar_one_or_none()
                if not isinstance(concurrent_name, str) or concurrent_name.casefold() != name.casefold():
                    raise LoadPlanError("Colisión concurrente de identidad: se revierte todo")
                skipped += 1
                continue
            inserted_repos += 1
            if identifier in prepared.readmes_by_id:
                added = conn.execute(text("""
                    INSERT INTO public.catalog_readmes (github_id, readme_text, updated_at)
                    VALUES (:github_id, :readme_text, CURRENT_TIMESTAMP)
                    ON CONFLICT (github_id) DO NOTHING RETURNING github_id
                """), {"github_id": identifier,
                       "readme_text": prepared.readmes_by_id[identifier]}).scalar_one_or_none()
                if added is None:
                    raise LoadPlanError("README en conflicto inesperado: operación revertida")
                inserted_readmes += 1

    return InsertSummary(inserted_repos, inserted_readmes, skipped)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan OpenBridge: CLI sin escrituras SQL")
    parser.add_argument("--live", action="store_true", help="autoriza GitHub real y consulta SQL de solo lectura")
    parser.add_argument("--count", type=int, choices=(5, 10), default=5)
    args = parser.parse_args()
    if not args.live:
        print("MODO SEGURO: 0 solicitudes HTTP y 0 conexiones SQL.")
        print("Para planificar con datos reales: --live --count 10")
        print("Este programa NO admite escrituras desde CLI en PostgreSQL.")
        return 0

    # Import tardío: sin --live no se leen siquiera credenciales de PostgreSQL.
    from database import engine

    slugs = APPROVED_REPOSITORIES[:args.count]
    records, audit = fetch_repositories(slugs, enabled=True, include_readme=True)
    successful = sum(bool(row.get("success")) for row in audit)
    print(f"HTTP: {successful}/{len(audit)} solicitudes correctas")
    if len(records) != args.count:
        print("ABORTADO: lote incompleto; no se construye plan de carga.")
        return 2

    result = transform_records(records)
    snapshot = read_catalog_snapshot(engine)
    plan = plan_load(result, snapshot)
    print("\n=== PLAN SOLO LECTURA ===")
    for row in plan.rows:
        note = " | REVISAR IDENTIDAD" if row["identity_warning"] else ""
        print(f"{row['full_name']} | REPO={row['repo_plan']} | README={row['readme_plan']}{note}")
    print(f"\nRepositorios existentes: {plan.existing_repositories}")
    print(f"Repositorios nuevos potenciales: {plan.new_repositories}")
    print(f"READMEs existentes: {plan.existing_readmes}")
    print(f"READMEs nuevos potenciales: {plan.new_readmes}")
    print(f"Sin README en origen ni catálogo: {plan.missing_readmes}")
    print(f"Alertas de identidad: {plan.identity_warnings}")
    print(f"Observaciones extracción/transformación: {len(plan.observations)}")
    print("\nBLOQUEADO PARA ESCRITURA DESDE CLI: migración y autorización separadas.")
    print("0 INSERT / UPDATE / DELETE ejecutados; PostgreSQL sin modificaciones.")
    return 0 if not plan.identity_warnings and not plan.observations else 3


if __name__ == "__main__":
    sys.exit(main())
