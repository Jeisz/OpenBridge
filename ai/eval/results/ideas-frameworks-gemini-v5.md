# Ideas de integración: validación

Corridas: ideas-frameworks-gemini-v5-r1.json, ideas-frameworks-gemini-v5-r2.json. Referencia: `ai/eval/ideas_reference_frameworks.json` (3 repos).

## Criterios

| Criterio | Corrida 1 | Corrida 2 |
|---|---|---|
| Requeridas encontradas (≥ 3) | 1/3 ❌ | 1/3 ❌ |
| Repos que debían quedar sin ideas | 0/0 ✅ | 0/0 ✅ |
| Repos por encima de su tope | 0 ✅ | 0 ✅ |
| Ideas prohibidas | 0 ✅ | 0 ✅ |

**Estabilidad** (mismos tipos en todas las corridas, ≥ 3): 3/3 ✅

### Corrida 1

- Ideas: 1 (con snippet: 0)
- Descartadas por el código: ninguna

### Corrida 2

- Ideas: 1 (con snippet: 0)
- Descartadas por el código: ninguna

## Por repo (revisión manual)

Para cada idea: ¿el tipo y el resumen son coherentes con la cita? ¿Los disparadores aportan o son relleno? ¿El enlace lleva a la sección correcta?

### Kludex/starlette

Requeridas: sdk · Admisibles: — · Prohibidas: rest_api
Nota: Framework ASGI para construir servicios web propios.

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### pallets/flask

Requeridas: sdk · Admisibles: — · Prohibidas: rest_api
Nota: Framework web para construir aplicaciones propias.

**Corrida 1**
- Sin ideas

**Corrida 2**
- Sin ideas

### fastapi/sqlmodel

Requeridas: sdk · Admisibles: — · Prohibidas: rest_api
Nota: Librería de acceso a bases SQL; menciona FastAPI, pero no expone una API.

**Corrida 1**
- **[sdk · medium] Usar SQLModel para interactuar con bases de datos relacionales en Python**
  - Resumen: Conecta tu aplicación de Python con bases de datos SQL usando clases y modelos basados en tipado para definir tablas y realizar operaciones CRUD sin duplicar código con Pydantic y SQLAlchemy.
  - Cita: «SQLModel is a library for interacting with SQL databases from Python code, with Python objects.»
  - Stack: Python, SQLAlchemy, Pydantic, FastAPI · Dependencias: sqlmodel · Disparadores: Inicio de la aplicación, Consulta de datos en la base de datos
  - Snippet (—): `—`
  - Documentación: https://sqlmodel.tiangolo.com/

**Corrida 2**
- **[sdk · medium] Usar SQLModel para interactuar con bases de datos SQL**
  - Resumen: Conecta tu aplicación Python a una base de datos SQL usando modelos basados en anotaciones de tipos, Pydantic y SQLAlchemy para definir tablas y consultar datos.
  - Cita: «SQLModel is a library for interacting with SQL databases from Python code, with Python objects.»
  - Stack: Python, SQLAlchemy, Pydantic, FastAPI · Dependencias: Python, Base de datos SQL · Disparadores: Inicio de la aplicación, Consulta de datos del usuario
  - Snippet (—): `—`
  - Documentación: https://sqlmodel.tiangolo.com/
