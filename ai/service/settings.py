"""Variables del servicio del asistente, leídas del entorno al arrancar."""

import os
from dataclasses import dataclass

# Orígenes del frontend en local (puerto 4173, con localhost o con 127.0.0.1).
DEFAULT_CORS_ORIGINS = ("http://localhost:4173", "http://127.0.0.1:4173")

# De dónde lee el catálogo al arrancar: lo publicado en la base (lo mismo que muestra la ficha)
# o los archivos de ai/data/catalog/ (la vuelta atrás). Solo lo lee el servicio: las
# evaluaciones usan siempre los archivos.
CATALOG_SOURCES = ("database", "files")


@dataclass(frozen=True)
class Settings:
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS
    catalog_source: str = "database"

    @classmethod
    def from_env(cls) -> "Settings":
        """AI_CORS_ORIGINS: orígenes separados por comas; sin definir, los de local.
        AI_CATALOG_SOURCE: database (por defecto) o files. Otro valor es un error al arrancar.
        """
        source = os.environ.get("AI_CATALOG_SOURCE") or "database"
        if source not in CATALOG_SOURCES:
            raise ValueError(f"AI_CATALOG_SOURCE={source!r}; opciones: {', '.join(CATALOG_SOURCES)}")
        raw = os.environ.get("AI_CORS_ORIGINS")
        origins = (DEFAULT_CORS_ORIGINS if raw is None
                   else tuple(o.strip() for o in raw.split(",") if o.strip()))
        return cls(cors_origins=origins, catalog_source=source)
