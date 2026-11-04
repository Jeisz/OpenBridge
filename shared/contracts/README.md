# shared/contracts/ — Contratos entre partes

Forma de los datos que una parte produce y otra consume. Los cambios se hacen
por Pull Request, avisando al equipo ([`CONTRIBUTING.md`](../../CONTRIBUTING.md), regla 3).

| Archivo | Contrato | Escribe → lee | Estado |
|---|---|---|---|
| `repo.py` | Repo: una herramienta del catálogo y sus categorías | Ingesta + IA → IA, API, frontend | v1.2 · acordado (29-oct-2026) |
| `categories.json` | Lista de categorías | Equipo → IA, frontend | v1 · 18 categorías, acordado con frontend (30-oct-2026) |
| `integration_idea.py` | Idea de integración de una herramienta | IA → frontend | v1.1 · acordado (24-oct-2026) |
| `repo_detail.py` | Ficha de un repositorio: el repo y sus ideas | API → frontend | v1 · propuesto (29-oct-2026) |
| `assistant.py` | Pregunta, respuesta y errores del asistente | Frontend ↔ IA | v1.1 · acordado (24-oct-2026) |

## Uso desde Python

Requiere Pydantic 2.x (convención del equipo). Se importa desde la raíz del repo:

```python
from shared.contracts.repo import Repo

repo = Repo.model_validate(fila)   # dict; por ejemplo, una fila de v_repos_for_ai
```

- Los scripts y tests se ejecutan con `python -m …` desde la raíz; desde una
  subcarpeta o un notebook en otra carpeta, `shared` no se puede importar.
- Con Docker, el contexto de construcción tiene que incluir `shared/`.

## Desde otros lenguajes

Los `.py` son la referencia legible de cada contrato. `categories.json` se
puede leer directamente.

## `categories.json`

Cada categoría tiene cuatro campos, cada uno pensado para un lector:

- `id`: fijo. Es lo que se guarda en la base y lo que usan los filtros; cambiarlo obliga a migrar los datos guardados.
- `name`: lo que ve el usuario. Puede cambiar sin afectar a nada más.
- `description`: qué es la categoría, en positivo. Entra en el texto con el que se busca cada repo, así que no lleva negaciones ni nombres de herramientas.
- `llm_notes`: ejemplos y fronteras para que el LLM clasifique (`No incluye: … (id)`). No entra en la búsqueda.

Un repo que no encaja en ninguna queda con la lista de categorías vacía; no hay una categoría "Otros".

## `repo_detail.py`

Cuerpo de `GET /repos/{full_name}`: `{"repo": …, "integration_ideas": […]}`.
Compone dos contratos ya acordados, sin campos nuevos:

- `repo`: un `Repo` v1.2 completo, con `readme_text` y `topics`.
- `integration_ideas`: 0–3 `IntegrationIdea` v1.1. Cero ideas es válido
  (repo archivado, sin README o sin ideas revisadas).
- Las ideas tienen el mismo `full_name` que el repo; un repo archivado no
  lleva ideas.

El listado (`GET /repos`) no usa este contrato: entrega `Repo` sin
`readme_text` ni `topics`, y la paginación va en cabeceras (`X-Total-Count`,
`X-Total-Pages`, `X-Page`, `X-Page-Size`), así que el cuerpo es el array.

## Pruebas

```bash
python -m pytest tests/contracts -v
```

Ejemplos válidos de cada contrato y casos que deben rechazarse.
