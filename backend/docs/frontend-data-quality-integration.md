# Data Quality & Mantenimiento: Contrato HTTP para el Frontend

Guía técnica de consumo de los campos operativos `is_maintained`, `open_issues_count` y `disabled` desde el frontend (Next.js). Todo lo descrito en este documento fue verificado contra la API real en la rama `feat/data-quality-maintenance`. No contiene endpoints ni campos simulados o inventados: cada ruta corresponde a `backend/app/api/router.py` y `backend/app/api/routes/repos.py`.

Documentos relacionados:
- `shared/contracts/repo.py` — Contrato canónico `Repo v1.2`.
- `shared/contracts/repo_detail.py` — Contrato canónico `RepoDetail`.
- `ingestion/docs/ADR-005_campos_operativos_y_mantenimiento.md` — Decisión de arquitectura sobre campos operativos.

---

## 1. Estado y Reglas de los Campos Operativos

| Campo | Tipo | Origen | Significado | Tratamiento de `null` en Frontend |
|---|---|---|---|---|
| `is_maintained` | `boolean \| null` | Calculado en FastAPI (`CASE WHEN` SQL / fallback servicio) | `true`: no archivado y push en los últimos 180 días.<br>`false`: archivado o push anterior a 180 días.<br>`null`: fecha ausente o sin dato. | Mostrar badge «Mantenido» (`true`), «Inactivo / Obsoleto» (`false`) o «Sin evaluar» (`null`). **No asumir false**. |
| `open_issues_count` | `integer \| null` | Extraído de GitHub (`public.catalog_repositories`) | Conteo total de issues abiertas + PRs abiertas en GitHub. | Mostrar conteo numérico si es entero $\ge 0$. Si es `null`, mostrar «—» o «Sin dato». **No convertir a 0**. |
| `disabled` | `boolean \| null` | Extraído de GitHub (`public.catalog_repositories`) | Indica si GitHub deshabilitó administrativamente el repositorio (no clonable/bloqueado). | Si es `true`, alertar «Repositorio deshabilitado». Si es `null` o `false`, comportamiento normal. |

> [!IMPORTANT]
> `is_maintained` **no es una columna física en Supabase**. Se calcula dinámicamente en tiempo de consulta mediante SQL (`CASE WHEN ... END`) y en el servicio backend, garantizando que el estado refleje siempre la ventana móvil de los últimos 180 días respecto a `NOW()`.

---

## 2. URL Base y Puertos

| Entorno | URL base | Notas |
|---|---|---|
| Local (Backend FastAPI) | `http://127.0.0.1:8000` | Ejecución: `uvicorn backend.app.main:app --port 8000` |
| Swagger UI / OpenAPI | `http://127.0.0.1:8000/docs` | Esquema OpenAPI en `/openapi.json` |
| Local (Frontend Next.js) | `http://127.0.0.1:4173` | Puerto estándar acordado (`next dev --port 4173`) |
| Producción / Despliegue | **No configurada** | No existe URL pública activa aún. |

*Nota sobre rutas:* La API no utiliza prefijo `/api`. Rutas como `/api/repos` devuelven `404 Not Found`.

---

## 3. Endpoints Disponibles

### 3.1 `GET /health`
Liveness check del servicio backend.
- **Respuesta (200 OK)**:
```json
{
  "status": "ok"
}
```

### 3.2 `GET /repos`
Listado paginado de herramientas del catálogo.
- **Respuesta (200 OK)**: Array JSON plano de objetos `Repo` (sin envoltorio `data` ni `items`).
- **Paginación**: Se entrega en las cabeceras HTTP de respuesta:
  - `X-Total-Count`: Total de repositorios que cumplen el filtro.
  - `X-Total-Pages`: Total de páginas calculadas.
  - `X-Page`: Página solicitada.
  - `X-Page-Size`: Elementos por página.
- **Filtros admitidos (query params)**:
  - `q`: Búsqueda textual por nombre, descripción o resumen IA.
  - `category`: Identificador de categoría (puede repetirse).
  - `language`: Lenguaje de programación.
  - `license`: SPDX ID de licencia.
  - `maintenance`: `active` (no archivado y no deshabilitado) o `inactive`.
  - `min_stars`: Entero mínimo de estrellas.
  - `page`: Número de página ($\ge 1$).
  - `page_size`: Tamaño de página (1–100, default: 20).

### 3.3 `GET /repos/{owner}/{name}`
Ficha técnica completa de una herramienta.
- **Respuesta (200 OK)**: Objeto `RepoDetail`:
```json
{
  "repo": { ... },
  "integration_ideas": [ ... ]
}
```

---

## 4. Ejemplos de Respuesta JSON Reales

### 4.1 Elemento de listado (`GET /repos`)
```json
[
  {
    "github_id": 2218615,
    "full_name": "keycloak/keycloak",
    "name": "keycloak",
    "description": "Open Source Identity and Access Management For Modern Applications and Services",
    "homepage": "https://www.keycloak.org",
    "language": "Java",
    "license_spdx_id": "Apache-2.0",
    "stargazers_count": 26400,
    "forks_count": 6800,
    "pushed_at": "2026-10-22T22:19:40Z",
    "archived": false,
    "disabled": false,
    "open_issues_count": 1284,
    "is_maintained": true,
    "health_score": null,
    "summary_es": "Servidor de gestión de identidades y accesos para aplicaciones modernas con soporte OpenID Connect y SAML.",
    "use_cases": [
      "Autenticación centralizada (SSO)",
      "Gestión de usuarios y federación de identidades"
    ],
    "categories": [
      {
        "category_id": "auth",
        "assigned_by": "llm"
      },
      {
        "category_id": "seguridad",
        "assigned_by": "rule"
      }
    ]
  }
]
```

### 4.2 Ficha de detalle (`GET /repos/keycloak/keycloak`)
```json
{
  "repo": {
    "github_id": 2218615,
    "full_name": "keycloak/keycloak",
    "name": "keycloak",
    "description": "Open Source Identity and Access Management For Modern Applications and Services",
    "homepage": "https://www.keycloak.org",
    "topics": ["sso", "identity-management", "oidc", "saml"],
    "language": "Java",
    "license_spdx_id": "Apache-2.0",
    "stargazers_count": 26400,
    "forks_count": 6800,
    "pushed_at": "2026-10-22T22:19:40Z",
    "archived": false,
    "disabled": false,
    "open_issues_count": 1284,
    "html_url": "https://github.com/keycloak/keycloak",
    "is_maintained": true,
    "health_score": null,
    "readme_text": "# Keycloak\n\nKeycloak is an Open Source Identity and Access Management solution...",
    "summary_es": "Servidor de gestión de identidades y accesos para aplicaciones modernas con soporte OpenID Connect y SAML.",
    "use_cases": [
      "Autenticación centralizada (SSO)",
      "Gestión de usuarios y federación de identidades"
    ],
    "categories": [
      {
        "category_id": "auth",
        "assigned_by": "llm"
      }
    ]
  },
  "integration_ideas": [
    {
      "id": "idea-keycloak-1",
      "full_name": "keycloak/keycloak",
      "title": "SSO Empresarial con Keycloak y FastAPI",
      "integration_type": "rest_api",
      "summary": "Proteger rutas FastAPI validando tokens JWT emitidos por Keycloak mediante OIDC.",
      "compatible_stack": ["FastAPI", "Python", "Next.js"],
      "dependencies": ["python-jose", "httpx"],
      "difficulty": "medium",
      "triggers": ["login_usuario"],
      "docs_url": "https://www.keycloak.org/documentation"
    }
  ]
}
```

---

## 5. Configuración CORS y Variables de Entorno

### Backend (`.env`)
```bash
# Orígenes autorizados para el frontend Next.js (separados por coma)
CORS_ORIGINS="http://127.0.0.1:4173,http://localhost:4173"

# URL de solo lectura a PostgreSQL / Supabase
DATABASE_URL="postgresql+psycopg://api_reader:secret@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
```

### Cabeceras CORS expuestas al cliente
```http
Access-Control-Allow-Origin: http://127.0.0.1:4173
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Accept, Content-Type
Access-Control-Expose-Headers: X-Total-Count, X-Total-Pages, X-Page, X-Page-Size
Access-Control-Max-Age: 600
```

### Frontend Next.js (`.env.local`)
```bash
# URL del catálogo FastAPI
NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
```

---

## 6. Ejemplo de Consumo en Next.js (React)

```typescript
// frontend/src/services/catalogService.ts

export interface CatalogRepo {
  github_id: number;
  full_name: string;
  name: string | null;
  description: string | null;
  homepage: string | null;
  language: string | null;
  license_spdx_id: string | null;
  stargazers_count: number;
  forks_count: number | null;
  pushed_at: string;
  archived: boolean;
  disabled: boolean | null;
  open_issues_count: number | null;
  is_maintained: boolean | null;
  health_score: number | null;
  summary_es: string | null;
  use_cases: string[];
  categories: Array<{ category_id: string; assigned_by: string }>;
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  totalPages: number;
  page: number;
  pageSize: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchRepositories(page = 1, pageSize = 20): Promise<PaginatedResult<CatalogRepo>> {
  const response = await fetch(`${API_BASE}/repos?page=${page}&page_size=${pageSize}`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Error consultando catálogo: HTTP ${response.status}`);
  }

  const data: CatalogRepo[] = await response.json();
  const total = parseInt(response.headers.get("X-Total-Count") || "0", 10);
  const totalPages = parseInt(response.headers.get("X-Total-Pages") || "1", 10);

  return {
    data,
    total,
    totalPages,
    page,
    pageSize,
  };
}
```

### Renderizado del estado de mantenimiento en componente UI:
```tsx
// frontend/src/components/MaintenanceBadge.tsx

interface Props {
  isMaintained: boolean | null;
  disabled: boolean | null;
  archived: boolean;
}

export function MaintenanceBadge({ isMaintained, disabled, archived }: Props) {
  if (disabled) {
    return <span className="badge badge-danger">Deshabilitado en GitHub</span>;
  }
  if (archived) {
    return <span className="badge badge-secondary">Archivado</span>;
  }
  if (isMaintained === true) {
    return <span className="badge badge-success">Activo (Mantenido)</span>;
  }
  if (isMaintained === false) {
    return <span className="badge badge-warning">Sin actividad reciente (&gt;180d)</span>;
  }
  return <span className="badge badge-muted">Actividad desconocida</span>;
}
```
