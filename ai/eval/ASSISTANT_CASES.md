# Casos de prueba del asistente

Pedidos de negocio fijos con lo que el asistente **debería** responder. Sirven
para elegir el modelo de lenguaje y para medir el asistente cada vez que cambia.
Se escriben antes de mirar lo que responde el asistente o la búsqueda.

Archivos: `assistant_cases.json` (los casos), `assistant_cases_validation.json` (casos de
validación, ver abajo) y `assistant_cases.py` (esquema y carga).
Tests: `ai/tests/test_assistant_cases.py`, sin base de datos ni modelo.

## Qué tiene un caso

| Campo | Qué es |
|---|---|
| `query` | El pedido, tal como lo escribiría un usuario (20–2000 caracteres, como en el contrato) |
| `expected_status` | `ok`, `needs_clarification` o `no_evidence` |
| `needs` | Necesidades que el asistente debería detectar, cada una con sus repos aceptables |
| `quick_set` | Marca los 5 casos que se usan para comparar modelos rápido |
| `note` | Qué prueba el caso |

Dos capas:

1. **Necesidades esperadas:** ids de `shared/contracts/categories.json`. Dependen
   solo del pedido, no del catálogo.
2. **Repos aceptables por necesidad:** dependen del catálogo actual. Una lista
   **vacía** significa que el catálogo no cubre esa necesidad: la respuesta
   debería mencionarlo en `limitations`, sin caja para ella.

## Reglas para escribirlos

- **Necesidad esperada** = la que el pedido dice, con esas u otras palabras.
  Lo que tiene cualquier software (pantallas, servidor) es la caja "tu app".
  Lo deseable pero no pedido puede ir en `assumptions` y no se evalúa como
  necesidad. Si el asistente detecta necesidades de más, no resta.
- **Repo aceptable** = su descripción, topics o README muestran esa necesidad
  como propósito principal. De 0 a 3 por necesidad, con la evidencia en `note`.
- Los repos aceptables se eligen **leyendo los datos del catálogo, no con la
  búsqueda**: si se copian sus resultados, la evaluación compara la búsqueda
  consigo misma.
- Licencia `NOASSERTION` (GitHub no la identificó): el repo es aceptable solo si
  su README muestra una licencia abierta, citada en `note`. Nunca un repo archivado.
- `expected_status` sigue una regla, y el esquema la comprueba:
  sin necesidades → `needs_clarification`; con necesidades pero ninguna con
  repos → `no_evidence`; al menos una con repos → `ok`.

## Qué hay (versión 1, 18 casos)

| Grupo | Casos | Qué prueba |
|---|---|---|
| Negocios | 6 | Pedidos de 3–4 necesidades, con y sin limitaciones |
| Textos de la pantalla del asistente | 8 | Los ejemplos que ve el usuario; tres pares de versión corta y larga del mismo pedido |
| Una sola necesidad | 2 | Mapa pequeño (`ok`) y sin evidencia (`no_evidence`) |
| Vagos | 2 | Sin necesidades → preguntas (`needs_clarification`) |

Resultado esperado: 12 `ok`, 4 `no_evidence`, 2 `needs_clarification`.

En los pares corto/largo, las necesidades del pedido largo contienen las del
corto: el asistente debería responder de forma coherente a los dos.

## Casos de validación (10 casos)

Los 18 casos de arriba se usan para mirar fallos y ajustar los prompts: mejorar en ellos no
prueba que una regla nueva sirva. Para eso hay un archivo aparte,
`assistant_cases_validation.json`, con el mismo esquema y estas reglas:

- Se escriben **antes** de cambiar el prompt, desde las políticas generales, en negocios
  distintos a los de la base.
- **No se usan para afinar el prompt.** Si se ajusta mirándolos, dejan de medir lo que el
  asistente hace con pedidos nuevos, y hacen falta otros.
- Primero se mide sin el cambio (línea base), con criterios de éxito escritos antes de ver
  los números; después, una sola ronda con el cambio.
- No comparten ids ni pedidos con la base (lo comprueba un test).

Los 5 primeros prueban que la aplicación que el usuario describe no se convierta en una
necesidad de frontend o backend, y que el asistente no proponga un candidato que solo se
parece a lo pedido. Los 5 siguientes prueban las limitaciones: necesidades sin herramientas
(que deben aparecer una sola vez) y tecnologías que el usuario nombra y no están entre los
candidatos (el asistente no puede afirmar qué hay en el catálogo completo).

```bash
python -m ai.eval.run_understand_eval gemini --cases validation
python -m ai.eval.run_assistant_eval gemini --cases validation
```

## Qué no se mide aquí

Los textos (título, resumen, roles, razones) y las conexiones: hay muchas
respuestas buenas distintas. Lo verificable es el `status`, qué necesidades
detectó y si cada repo elegido está entre los aceptables. De los textos solo se
cuentan, de forma automática, dos cosas: las necesidades sin herramienta que se
repiten en las limitaciones y los textos del modelo que hablan del catálogo. El
resto de la calidad del texto se revisa a mano.

## Cuando cambie el catálogo

`catalog_taken_at` guarda la fecha del snapshot (`ai/data/catalog/meta.json`)
con el que se escribieron los casos. Si el snapshot cambia, un test falla a
propósito. Entonces:

1. Revisar las necesidades con lista vacía: puede haber repos nuevos que las cubran.
2. Agregar repos aceptables solo con evidencia, con su `note`.
3. Actualizar `catalog_taken_at` y subir `version`.

Las necesidades esperadas (capa 1) no cambian con el catálogo.

## Cómo validarlos

```bash
python -m pytest ai/tests/test_assistant_cases.py -v
```
