"""Contrato: RepoDetail = ficha de un repositorio y las ideas que encajan.

v1 · propuesto en el cierre de Fase 2 (backend, 29-oct-2026). Compone dos
contratos ya acordados: Repo (v1.2) e IntegrationIdea (v1.1); no añade campos.
Escribe: la API. Lee: el frontend.
"""
from pydantic import BaseModel, Field, model_validator

from shared.contracts.integration_idea import IntegrationIdea
from shared.contracts.repo import Repo


class RepoDetail(BaseModel):
    repo: Repo
    integration_ideas: list[IntegrationIdea] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def check_ideas(self) -> "RepoDetail":
        if any(idea.full_name != self.repo.full_name for idea in self.integration_ideas):
            raise ValueError("idea de integración de otro repositorio")
        if self.repo.archived and self.integration_ideas:
            raise ValueError("un repositorio archivado no debe incluir ideas")
        return self
