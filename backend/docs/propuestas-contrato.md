# Propuestas de contrato pendientes de aprobación

Cierre de Fase 2 del backend de catálogo. Recoge las dos decisiones que no puede
tomar esta rama porque afectan a `shared/contracts/`, y el plan para publicar.

**Nada de `shared/` se modificó en contenido.** Lo único preparado es la
sincronización de `shared/contracts/repo.py` con la versión aprobada de `main`
(mismo blob, cero cambios de texto).

## 1. Estado verificado

| Comprobación | Resultado |
| --- | --- |
| Blob de `shared/contracts/repo.py` en el árbol y en el índice | `66b92f8` |
| Blob de `equipo/main:shared/contracts/repo.py` | `66b92f8` (idéntico) |
| `git diff --cached equipo/main -- shared/contracts/repo.py` | vacío |
| `git diff HEAD -- shared/contracts/repo.py` | `+5 −3` (v1.0 → v1.2) |
| Contratos en `equipo/main:shared/contracts/` | `README.md`, `assistant.py`, `categories.json`, `integration_idea.py`, `repo.py` |
| `repo_detail.py` | existe **commiteado en la rama `backend`**; **no está en `main`** |

### Qué aporta la sincronización de `Repo` v1.2 (29-oct-2026)

Sólo texto y dos campos, sin cambios de forma en lo que ya se publicaba:

```diff
-v1.0 · acordado con la ingesta (20-oct-2026). Nombres de la vista v_repos_for_ai (GitHub).
+v1.2 · acordado en el Sprint Demo (29-oct-2026). Nombres de la vista v_repos_for_ai (GitHub).
     archived: bool                            # True → no recomendar nunca
+    disabled: bool | None = None              # GitHub lo deshabilitó (no se puede clonar); None = sin dato
+    is_maintained: bool | None = None         # no archivado y push en los últimos 180 días; None = sin dato
-    description: str                                 # definición positiva para búsqueda
-    llm_notes: str                                   # ejemplos y fronteras para el LLM
+    description: str                                 # qué es, en positivo; entra al embedding
+    llm_notes: str                                   # ejemplos y fronteras; solo para el LLM
```

Consecuencia ya medida: fijada a v1.0 la rama da `74 passed, 4 failed`; con v1.2,
`78 passed`. El rol de la API no cambia: `disabled` se publica tal cual viene de
la columna y `is_maintained` viaja en `null` porque no existe la columna
(ver [`acceso-base-datos.md`](acceso-base-datos.md)).

## 2. Propuesta A — formalizar `RepoDetail` en `shared/contracts/`

### Situación

`shared/contracts/repo_detail.py` está commiteado en la rama pero su docstring
dice *«Propuesta local»*, y `main` no lo publica. La API ya lo consume
(`backend/app/api/schemas.py` hereda de él) y el frontend ya valida esa forma a
mano en `frontend/src/data/catalogHttp.mjs`, así que `{repo, integration_ideas}`
está de facto en el frontend **sin contrato ratificado**.

### Qué contiene hoy

```python
"""Respuesta HTTP de ficha. Propuesta local: compone contratos existentes."""
from pydantic import BaseModel, Field, model_validator
from shared.contracts.repo import Repo
from shared.contracts.integration_idea import IntegrationIdea


class RepoDetail(BaseModel):
    repo: Repo
    integration_ideas: list[IntegrationIdea] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def check_ideas(self):
        if any(idea.full_name != self.repo.full_name for idea in self.integration_ideas):
            raise ValueError("idea de integración de otro repositorio")
        if self.repo.archived and self.integration_ideas:
            raise ValueError("un repositorio archivado no debe incluir ideas")
        return self
```

### Texto propuesto (misma semántica, cabecera de contrato)

```python
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
```

Reglas que quedarían fijadas y que hoy sólo existen en el frontend y en los
tests del backend: como mucho **tres** ideas, todas del **mismo** repositorio y
**ninguna** si el repositorio está archivado.

### Por qué no lleva `extra="forbid"`

La API publica `CatalogRepo`, un superconjunto de `Repo` (propuesta B). Si el
contrato prohibiera campos extra, cualquier `RepoDetail.model_validate()` de una
respuesta real fallaría. El contrato describe el **mínimo** que pueden esperar
los consumidores; los extras son aditivos y opcionales para ellos.

### Cambios de soporte que acompañan al PR de contratos

1. Fila nueva en la tabla de `shared/contracts/README.md`, después de
   `integration_idea.py`:

   ```
   | `repo_detail.py` | Ficha de un repositorio: el repo y sus ideas | API → frontend | v1 · acordado (29-oct-2026) |
   ```

2. Ejemplos en `tests/contracts/test_contract_examples.py`: una ficha válida y
   tres rechazos (cuatro ideas, idea de otro repositorio, ideas en archivado).
   Ese archivo ya está modificado en el árbol de trabajo; los ejemplos nuevos se
   suman a ese cambio, no lo sustituyen.
3. No hace falta tocar `repo.py` ni `integration_idea.py`.

### Si no se ratifica

`RepoDetail` pasaría a `backend/app/api/schemas.py` como modelo propio de la API
y `shared/contracts/repo_detail.py` se retiraría con su import. La forma de la
respuesta no cambia; se pierde que Frontend e IA compartan la definición.

## 3. Propuesta B — decidir `name`, `html_url` y `forks_count`

### Qué son y de dónde salen

| Campo | Columna | Viaja en | ¿Obligatorio en `Repo`? | Estado del dato |
| --- | --- | --- | --- | --- |
| `name` | `catalog_repositories.name` | listado y ficha | no | poblado |
| `html_url` | `catalog_repositories.html_url` | listado y ficha | no | **NULL en 95 de 100 filas** |
| `forks_count` | `catalog_repositories.forks_count` | listado y ficha | no | poblado |

Los tres los inyecta `backend/app/api/schemas.py` (`CatalogRepo`, subclase de
`Repo`) y los rellena `backend/app/services/catalog.py` a partir de
`backend/app/repositories/repos.py`.

### Quién los lee (verificado en este cierre)

- **`frontend/`: nadie.** `git grep -E 'repo\.(name|html_url|forks_count)' --
  frontend` no devuelve nada. El nombre visible se deriva del contrato
  (`frontend/src/data/catalog.mjs:16` y `catalogHttp.mjs:10` hacen
  `repo.full_name.split('/').at(-1)`) y el enlace a GitHub se arma con
  `` `https://github.com/${tool.repo}` `` (`ToolCard.jsx:55` y
  `ToolDetail.jsx:42`), donde `tool.repo` es el `full_name`.
- **`pm/`, `ai/`, `ingestion/`: nadie.** La búsqueda de `html_url|forks_count`
  en esas carpetas no devuelve resultados.
- **`backend/`: 4 pruebas y 3 módulos.** `test_contract_compat.py:54`,
  `test_contract_conformance.py:22`, `test_repo_detail.py:25` y
  `test_repository_sql.py:85`.

### Opciones y consecuencias

| Opción | Qué implica | Coste |
| --- | --- | --- |
| **A. Añadirlos a `Repo` (v1.3)** | Contrato gana tres campos opcionales; hay que definir bien `html_url` con 95 % de NULL y poblarlo en la ingesta | PR de contratos + aviso a IA e ingesta; sin beneficio mientras nadie los lea |
| **B. Retirarlos de la respuesta** | Cumple §3 al pie de la letra: el listado pasa de **19 a 16** claves y la ficha de **21 a 18** | Tocar `schemas.py`, `services/catalog.py` (dos dicts), `repositories/repos.py` (dos `SELECT`) y 4 pruebas; ningún consumidor se entera |
| **C. Dejarlos, documentados (actual)** | Extensión local explícita: la API publica el contrato **más** tres columnas de la tabla base | Ninguno; riesgo de que alguien asuma que están en el contrato |

### Recomendación

**C para Fase 2**, y decidir A o B en Fase 3 con Fabián. Motivo: cero
consumidores, cero riesgo para publicar y la decisión no debe bloquear el PR. Lo
que no era aceptable —y ya está corregido— es publicarlos sin documentar.

Si se elige **B**, `test_contract_compat.py:54` cambia de sentido: hoy afirma
`extras == {"name", "html_url", "forks_count"}` y debería afirmar que no hay
extras. Si se elige **A**, esa misma prueba pasa a comprobar que los extras son
subconjunto de `Repo`.

## 4. Plan de publicación por PR

**Paso 0 · Estado de la rama (hecho).** `shared/contracts/repo.py` queda
preparado en el índice con el blob de `main` (`66b92f8`); el resto de cambios
locales sigue intacto; sin commit y sin push.

**Paso 1 · PR de contratos contra `equipo/main`** (lo abre quien tenga permiso,
avisando a Frontend e IA según la regla 3 de `CONTRIBUTING.md`):

- añadir `shared/contracts/repo_detail.py` con el texto de la propuesta A;
- añadir la fila del contrato a `shared/contracts/README.md`;
- añadir los ejemplos válidos y de rechazo en `tests/contracts/test_contract_examples.py`;
- `repo.py` **no** se toca: `main` ya tiene v1.2.

**Paso 2 · Sincronizar la rama.** `git fetch equipo; git rebase equipo/main` (o
merge). Al traer `main`, `shared/contracts/repo.py` deja de aparecer como cambio
porque es exactamente el mismo blob, y `repo_detail.py` deja de ser una
introducción no ratificada.

**Paso 3 · Commit del backend** (cuando se autorice), sólo estos archivos:

```
backend/app/api/schemas.py
backend/tests/test_contract_compat.py
backend/tests/test_contract_conformance.py   (nuevo en la rama)
backend/tests/test_frontend_contract.py      (nuevo en la rama)
backend/tests/test_repos_list.py
backend/README.md
backend/docs/acceso-base-datos.md
backend/docs/propuestas-contrato.md          (nuevo)
```

Nada de `frontend/`, `ingestion/`, `ai/`, `shared/` ni `supabase/`.

**Paso 4 · Verificar sobre la rama rebasada.**

```bash
python -m pytest backend/tests -q     # 78 passed
python -m pytest tests/contracts -q   # 33 passed
```

**Paso 5 · PR `backend` → `equipo/main`.** Revisores: Fabián (forma de las
respuestas que consume), Jeison (contratos compartidos) y equipo de datos
(`is_maintained`, `health_score`).

### Pendientes que este trabajo no cierra

| Pendiente | Estado |
| --- | --- |
| Conexión real a Supabase | **Pendiente**: sin credenciales válidas para el rol de lectura (la contraseña del pooler no autentica) y el rol sólo tiene `SELECT` sobre `v_repos_for_ai`; `/repos` responde 503 `catalog_unavailable`. Nada de lo verificado depende de la base: es `TestClient` con repositorio falso |
| `docs/backend/IMPLEMENTACION_BACKEND.md` y `docs/backend/DECISIONES_TECNICAS.md` | Sin seguimiento en Git; alguien debe decidir si se mueven a `backend/docs/` o se descartan. **No se borraron** |
| `is_maintained` / `health_score` | Siguen en `null`: no hay columna ni fórmula (ver [`acceso-base-datos.md`](acceso-base-datos.md)) |

## 5. Restricciones respetadas

- No se tocó `frontend/`, `ingestion/` ni `ai/`: sólo se leyeron para verificar
  qué campos consumen.
- No hubo DDL, ni escritura en Supabase, ni uso de credenciales administrativas.
- No se borró ningún archivo sin seguimiento.
- No hay commit, merge ni push.
- El único cambio en `shared/` es la **preparación en el índice** de
  `repo.py`, con el contenido idéntico a `main` (blob verificado).



