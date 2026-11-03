"""Contrato: Repo (= una herramienta del catálogo en el MVP).

v1.2 · acordado en el Sprint Demo (29-oct-2026). Nombres de la vista v_repos_for_ai (GitHub).
Escribe: la ingesta (mitad de arriba) y la IA (mitad de abajo).
Lee: la IA, la API y el frontend.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class CategoryAssignment(BaseModel):
    """Una categoría asignada al repo."""
    category_id: str  # debe existir en categories.json
    assigned_by: Literal["rule", "llm", "human"]  # "human" nunca se sobrescribe


class Repo(BaseModel):
    # Lector tolerante: si llegan campos extra (name, forks_count, content_hash...), se ignoran.
    model_config = ConfigDict(extra="ignore")

    # ---------- Mitad de arriba: la escribe la ingesta ----------
    full_name: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")  # "owner/name"; para citar. Puede cambiar si se renombra
    github_id: int = Field(gt=0)              # clave estable: no cambia con renombres
    description: str | None = None            # puede faltar → plan B: README
    topics: list[str] = Field(default_factory=list)
    language: str | None = None
    license_spdx_id: str | None = None        # SPDX; "NOASSERTION" = desconocida → no recomendable
    stargazers_count: int = Field(ge=0)
    pushed_at: datetime                       # la vista lo da como texto ISO 8601; Pydantic lo convierte
    open_issues_count: int | None = Field(default=None, ge=0)  # issues + PRs; lo usa la ficha, no la IA
    archived: bool                            # True → no recomendar nunca
    disabled: bool | None = None              # GitHub lo deshabilitó (no se puede clonar); None = sin dato
    is_maintained: bool | None = None         # no archivado y push en los últimos 180 días; None = sin dato
    readme_text: str | None = None            # LEFT JOIN: puede faltar
    homepage: HttpUrl | None = None           # se pide NULL; "" se lee como None
    health_score: float | None = Field(default=None, ge=0, le=100)  # propuesta 0–100

    # ---------- Mitad de abajo: la escribe la IA ----------
    # Opcional hasta que la IA procesa; la primera es la principal.
    categories: list[CategoryAssignment] = Field(default_factory=list, max_length=3)
    use_cases: list[str] = Field(default_factory=list, max_length=4)
    summary_es: str | None = Field(default=None, max_length=250)  # resumen en español para la ficha

    @field_validator("homepage", mode="before")
    @classmethod
    def empty_homepage_is_none(cls, v):
        return None if v == "" else v


class Category(BaseModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")   # "auth", "database"
    name: str                                        # lo que ve el usuario
    description: str                                 # qué es, en positivo; entra al embedding
    llm_notes: str                                   # ejemplos y fronteras; solo para el LLM


class CategoryList(BaseModel):
    version: int
    categories: list[Category]
