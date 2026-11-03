"""Genera los datos de ejemplo de la IA a partir de la API de GitHub.

Uso (desde la raíz del repo, con el entorno activo):
    python -m ai.scripts.build_sample_data

Lee cada repo con `gh api`, le agrega las categorías asignadas a mano,
lo valida con el esquema `Repo` y escribe:
    ai/data/repos.json
    ai/data/readmes/<owner>__<name>.md
"""

import json
import subprocess

from ai.catalog import readme_dir, readme_file, repos_file
from shared.contracts.repo import Repo

SOURCE = "sample"

# Clasificación manual de acuerdo a shared/contracts/categories.
# Es la referencia contra la que se evaluará más adelante
# la clasificación automática con un LLM.
CATEGORIES: dict[str, list[str]] = {
    "keycloak/keycloak": ["auth"],
    "ory/kratos": ["auth"],
    "supertokens/supertokens-core": ["auth"],
    "zitadel/zitadel": ["auth"],
    "supabase/supabase": ["database", "auth", "backend"],
    "pocketbase/pocketbase": ["database", "auth", "backend"],
    "redis/redis": ["cache", "database"],
    "juspay/hyperswitch": ["payments"],
    "getlago/lago": ["payments"],
    "killbill/killbill": ["payments"],
    "ollama/ollama": ["ai"],
    "langchain-ai/langchain": ["ai"],
    "run-llama/llama_index": ["ai"],
    "PostHog/posthog": ["analytics"],
    "plausible/analytics": ["analytics"],
    "umami-software/umami": ["analytics"],
    "metabase/metabase": ["analytics"],
    "meilisearch/meilisearch": ["search"],
    "typesense/typesense": ["search"],
    "qdrant/qdrant": ["search", "ai"],
}


def gh_api(path: str, raw: bool = False) -> str:
    """Llama a `gh api` y devuelve la respuesta como texto UTF-8."""
    cmd = ["gh", "api", path]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout.decode("utf-8")


def build_repo(full_name: str, category_ids: list[str]) -> Repo:
    """Descarga un repo y su README, y lo devuelve validado."""
    data = json.loads(gh_api(f"repos/{full_name}"))
    readme = gh_api(f"repos/{full_name}/readme", raw=True)

    # Guardar el README. La API devuelve el nombre actual si el repo fue renombrado.
    readme_file(data["full_name"], SOURCE).write_text(readme, encoding="utf-8", newline="\n")

    return Repo(
        full_name=data["full_name"],
        github_id=data["id"],
        description=data["description"],
        topics=data["topics"],
        language=data["language"],
        license_spdx_id=(data["license"] or {}).get("spdx_id"),
        stargazers_count=data["stargazers_count"],
        pushed_at=data["pushed_at"],
        open_issues_count=data["open_issues_count"],
        archived=data["archived"],
        homepage=data["homepage"],
        readme_text=readme,
        categories=[{"category_id": c, "assigned_by": "human"} for c in category_ids],
    )


def main() -> None:
    readme_dir(SOURCE).mkdir(parents=True, exist_ok=True)
    repos = []
    for full_name, category_ids in CATEGORIES.items():
        print(f"-> {full_name}")
        repos.append(build_repo(full_name, category_ids))

    # El README ya está en su archivo; no se repite dentro de repos.json.
    rows = [r.model_dump(mode="json", exclude={"readme_text"}) for r in repos]
    repos_file(SOURCE).write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"{len(repos)} repos -> {repos_file(SOURCE)}")
