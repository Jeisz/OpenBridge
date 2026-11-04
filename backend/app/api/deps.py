"""Dependencias de FastAPI: el estado vive en `app.state`, no en globales."""
from fastapi import Depends, Request

from backend.app.core.config import Settings
from backend.app.db.session import get_engine
from backend.app.repositories.repos import RepoRepository
from backend.app.services.catalog import CatalogService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_repository(engine=Depends(get_engine)) -> RepoRepository:
    return RepoRepository(engine)


def get_catalog_service(
    settings: Settings = Depends(get_settings),
    repository: RepoRepository = Depends(get_repository),
) -> CatalogService:
    return CatalogService(
        repository,
        default_page_size=settings.default_page_size,
        max_page_size=settings.max_page_size,
    )
