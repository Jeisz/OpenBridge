"""Variables del servicio del asistente, leídas del entorno al arrancar."""

import os
from dataclasses import dataclass

# Orígenes del frontend en local (puerto 4173, con localhost o con 127.0.0.1).
DEFAULT_CORS_ORIGINS = ("http://localhost:4173", "http://127.0.0.1:4173")


@dataclass(frozen=True)
class Settings:
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS

    @classmethod
    def from_env(cls) -> "Settings":
        """AI_CORS_ORIGINS: orígenes separados por comas; sin definir, los de local."""
        raw = os.environ.get("AI_CORS_ORIGINS")
        if raw is None:
            return cls()
        return cls(cors_origins=tuple(o.strip() for o in raw.split(",") if o.strip()))
