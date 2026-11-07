# Búsqueda del asistente: decisiones y evidencia

**Decisión (6-nov-2026):** la búsqueda usa **EmbeddingGemma-300m**, y el texto de
cada repo suma el **resumen y los casos de uso que genera la IA**, sin las
categorías. Umbral de "sin evidencia": **0,23**. La elección del modelo (3-nov) y
el umbral anterior (0,19, con el texto sin datos de la IA) siguen abajo como
historia.

Medido con el golden set `catalog` v2 (100 consultas) sobre el snapshot del
catálogo real del 2026-10-29. Cómo repetir la medición: [`README.md`](README.md).

## Resultados en el catálogo real

100 consultas (60 con respuesta y 40 sin respuesta) · 100 repos, todavía sin
categorías ni resumen en español · CPU. Lo único que cambia entre las dos
columnas es el modelo.

| | EmbeddingGemma-300m | Qwen3-Embedding-0.6B |
|---|---|---|
| hit@3 | 48/60 (80 %) | 45/60 (75 %) |
| MRR@3 | 0,71 | 0,68 |
| recall@3 | 69 % | 61 % |
| hit@5 | 53/60 (88 %) | 52/60 (87 %) |
| 1.er resultado, consultas con respuesta resueltas | 0,196 – 0,533 | 0,451 – 0,759 |
| 1.er resultado, consultas sin respuesta | 0,090 – 0,342 | 0,413 – 0,661 |
| Vectores de 100 repos | 9 s | 41 s |
| Consulta | 0,07 s | 0,33 s |

**El problema principal es el texto de los repos, no el modelo.** De las 12
consultas que EmbeddingGemma no resuelve, 7 tampoco las resuelve Qwen3: cuando
dos modelos distintos fallan en lo mismo, la causa está en lo que los dos leen.

| Causa | Ejemplo |
|---|---|
| Descripción vaga | "Procesar eventos en tiempo real": flink queda 14.º; su descripción es solo "Apache Flink" |
| Español frente a inglés | "Analítica de ventas de productos": grafana queda 6.º aunque tiene el topic `dashboard` |
| La consulta agrega algo que ningún repo dice | "Almacenamiento de datos geoespaciales": ClickHouse queda 13.º; ningún repo declara datos geoespaciales |
| Un repo parecido tapa al correcto | "Despliegue continuo en clústeres de contenedores": kubernetes sale 1.º y argo-cd 6.º |

Las tres primeras son las que debería mejorar un texto con categorías y un
resumen en español para cada repo.

**Con 5 candidatos por necesidad en vez de 3**, la búsqueda acierta en 53 de 60
consultas en lugar de 48. Más candidatos dan más aciertos, a cambio de más tokens
para el modelo de lenguaje.

Detalle por consulta en `results/search-catalog-embeddinggemma-300m.md` y
`results/search-catalog-qwen3-embedding-0.6b.md`.

## Modelo de embeddings: EmbeddingGemma-300m

Se eligió con los 20 repos de ejemplo (golden set `sample`) y se confirmó en el
catálogo real (tabla de arriba).

Comparación original, golden set `sample` (20 repos, con categorías):

| | EmbeddingGemma-300m | Qwen3-Embedding-0.6B |
|---|---|---|
| hit@3 | 14/14 | 14/14 |
| MRR@3 | 0,83 | 0,92 |
| recall@3 | 93 % | 89 % |
| 1.er resultado, consultas con respuesta | 0,207 – 0,558 | 0,485 – 0,687 |
| 1.er resultado, consultas sin respuesta | 0,117 – 0,208 | 0,439 – 0,554 |
| Vectores de 20 repos | 4–5,5 s | 11–15 s |
| Consulta | 0,06–0,09 s | 0,20–0,69 s |
| RAM aproximada | ~1,2 GB (estimada por el tamaño de los pesos) | ~2,4 GB |
| Instalación | Cuenta de Hugging Face, aceptar la licencia Gemma y token de lectura | Libre (Apache 2.0) |

Los dos modelos se midieron el 27-oct con las mismas condiciones. El reporte
guardado de EmbeddingGemma (`results/search-embeddinggemma-300m.md`) se
regeneró después, con las categorías actualizadas de los datos de ejemplo, y da
MRR 0,79; el de Qwen3 conserva la medición del 27-oct. La conclusión no cambia.

- Separa mejor lo que el catálogo no tiene. En el catálogo real sus dos grupos de
  puntajes se tocan (ver "Umbral"); los de Qwen3 se mezclan casi por completo.
- Unas 3 a 4 veces más rápido y con la mitad de RAM, lo que importa para desplegar.
- Mejor recall en los dos golden sets.
- Costo: cada máquina que lo descargue necesita el token (ver `ai/README.md`).
- Reversible: Qwen3 sigue en el registro (`AI_EMBEDDING_MODEL=qwen3`); cambiar de
  modelo obliga a recalibrar el umbral.

## Umbral de "sin evidencia": 0,19

> Reemplazado el 6-nov por 0,23 al cambiar el texto de los repos (ver "Texto de los repos con los datos de la IA").

`min_score` del modelo en `ai/embeddings.py`.

- Si el 1.er resultado de una necesidad puntúa menos de 0,19, el catálogo no
  tiene una herramienta para ella. Un puntaje igual a 0,19 pasa.
- Se aplica **sin filtros**: si una necesidad tiene evidencia pero nada cumple
  los filtros del usuario (por ejemplo, la licencia), la respuesta es una
  limitación ("existe, pero no con esa licencia"), no "sin evidencia".

**Regla para elegir el corte** (la aplica `suggest_min_score` en `metrics.py`, y
el reporte muestra el valor sugerido):

1. Solo cuentan las consultas con respuesta que la búsqueda resuelve (alguna
   herramienta correcta en el top-3). Las demás son fallos de búsqueda: un umbral
   no puede arreglarlas.
2. Si esas consultas y las sin respuesta se separan, el corte es el menor valor
   de dos decimales por encima de la mejor sin respuesta.
3. Si se solapan, el corte es la peor de esas válidas, redondeada hacia abajo.
4. El corte va cerca de las consultas sin respuesta a propósito: bloquear una
   necesidad válida no tiene arreglo (el modelo de lenguaje nunca ve esa
   herramienta); una sin respuesta que pasa todavía puede descartarla.

**La condición del punto 1 se agregó después de ver los resultados** de la
primera medición (12 consultas): sin ella, una consulta en la que la búsqueda ya
había fallado bajaba el corte y dejaba pasar consultas sin respuesta.

**Resultado con 0,19:** 0 de 48 consultas resueltas bloqueadas; 18 de 40 sin
respuesta pasan. Con el valor anterior (0,20) quedaba bloqueada "almacenamiento
temporal en memoria" (redis, 0,196), una consulta que escribe el asistente a
partir de un texto de ejemplo de la pantalla.

### Hallazgo: con el texto actual, el umbral solo frena lo que está lejos

Los puntajes de las consultas con respuesta (0,196 – 0,533) y sin respuesta
(0,090 – 0,342) se mezclan. El umbral frena pedidos sin nada parecido en el
catálogo ("contabilidad y nómina de empleados"), pero no los que *suenan*
parecido a un repo que no los resuelve:

| Consulta sin respuesta | 1.er resultado | Por qué se parece |
|---|---|---|
| "gestión de permisos de acceso" (y otras 9 de identidad, roles y permisos) | vault, 0,23 – 0,34 | "privileged access management" (guarda secretos, no maneja usuarios) |
| "gestión de base de datos relacional" | sqlmodel, 0,30 | "SQL databases in Python" (habla con la base, no es la base) |
| "videollamadas desde el navegador" | playwright, 0,26 | Nombra navegadores (sirve para probar páginas) |
| "edición sencilla de contenidos periodísticos" | astro, 0,22 | "content-driven websites" (construye el sitio, no el editor) |

El umbral mide cuánto se parecen las palabras, no si el repo resuelve la
necesidad.

Subir el umbral no es la solución. Para que ninguna de estas consultas pase,
tendría que estar por encima de 0,342 (vault para "gestión de permisos de
acceso"). Con ese valor quedarían bloqueadas 25 de las 48 consultas que hoy la
búsqueda resuelve bien, por ejemplo "almacenamiento temporal en memoria" (redis,
0,196): el asistente respondería "el catálogo no tiene esto" en más de la mitad
de los pedidos que sí tienen herramienta.

Para estas consultas, el freno tiene que venir del paso que elige entre los
candidatos (descartar los que no cumplen la necesidad) y de un texto de los repos
más preciso, que separe los dos grupos.

## Texto de los repos con los datos de la IA (6-nov-2026)

El texto de muchos repos era vago o solo en inglés ("Apache Flink"): 7 de los 12
fallos de búsqueda venían del texto, no del modelo. Con las categorías, el resumen
y los casos de uso que genera la IA, se midió cada paso con el mismo golden set.
El criterio se fijó antes: un paso entra si el hit@3 sube 2 o más (o queda igual
y sube el MRR) y las consultas sin respuesta que pasan su umbral no aumentan en
más de 2.

| Texto | hit@3 | MRR | hit@5 | Sin respuesta que pasan | Umbral sugerido |
|---|---|---|---|---|---|
| Sin datos de la IA (antes) | 48/60 | 0,71 | 53 | 18/40 | 0,19 |
| + categorías | 50/60 | 0,76 | 57 | 37/40 | 0,15 |
| + resumen | 53/60 | 0,76 | 56 | 32/40 | 0,17 |
| + casos de uso | 53/60 | 0,81 | 56 | 22/40 | 0,24 |
| **Resumen + casos de uso, sin categorías** | **52/60** | **0,78** | **54** | **20/40** | **0,23** |

- **Las categorías acercan consultas sin respuesta.** Su descripción es genérica:
  la de autenticación dice "inicio de sesión", así que la consulta "login" (el
  catálogo no tiene una herramienta de login) encontraba a vault. El resumen y los
  casos de uso describen lo que hace *ese* repo y separan mejor.
- **La variante sin categorías se agregó después de ver las cuatro primeras**, con
  su hipótesis y su criterio escritos antes de correrla (hit@3 ≥ 50 y sin respuesta
  que pasan ≤ 20). Cumple justo en el límite. Como se eligió con el mismo golden
  set, conviene validarla con casos nuevos.
- "Procesar eventos en tiempo real": flink pasa del puesto 14 al 1.
- Las categorías siguen en la ficha y en los filtros; solo salen del texto de
  búsqueda.

**Efecto en el asistente** (10 casos de validación × 2 corridas, frente a la
validación del 4-nov con umbral 0,19): elige una herramienta aceptable en el 88 %
de las necesidades que la tienen (antes 67 %) y acierta de punta a punta en el
79 % (antes 62 %), pero se abstiene en el 50 % de las que no la tienen (antes
68 %). Las abstenciones perdidas son alertmanager para comunicación y vault para
autenticación: parecidos, no útiles. Reportes: `results/assistant-2026-11-04-1505-validation-gemini.md`
y `results/assistant-2026-11-06-1111-validation-gemini.md`.

## Validación con consultas nuevas (7-nov-2026)

35 consultas escritas después de elegir la variante (`search_queries_catalog_validation.json`:
20 con respuesta y 15 sin respuesta). Criterio fijado antes: volver al texto anterior solo
si le gana por 2 o más en hit@3, o si la variante actual deja pasar 3 o más consultas sin
respuesta de más.

| Texto | hit@3 | MRR | Sin respuesta que pasan (umbral) |
|---|---|---|---|
| Sin datos de la IA | 20/20 | 0,93 | 9/15 (0,19) |
| Resumen + casos de uso (actual) | 19/20 | 0,90 | 11/15 (0,23) |

- Se mantiene la variante actual: las diferencias quedan dentro del margen fijado.
- La ventaja medida con el golden set con que se eligió (+4 en hit@3) no se repite con
  consultas nuevas.
- El umbral 0,23 no bloquea ninguna consulta resuelta, pero deja pasar 11 de 15 sin
  respuesta: frente a herramientas parecidas que no sirven, el freno tiene que estar en el
  paso que elige entre los candidatos.

Reportes: `results/search-catalog-validation-embeddinggemma-300m.md` y
`results/search-catalog-validation-embeddinggemma-300m-texto-base.md`.

## Límites

- **Los números indican una dirección, no son precisos:** 60 consultas con
  respuesta y 40 sin respuesta en un catálogo de 100 repos.
- **Las necesidades con variante pesan el doble** en hit@3, MRR y recall, porque
  tienen dos consultas con los mismos aceptables.
- **Las consultas escritas por el paso de entender** salieron de un modelo y un
  prompt concretos (3-nov). Si el asistente cambia cómo las escribe, hay que
  volver a medir; el golden set sigue sirviendo para comparar la búsqueda.
- **Un golden set vale para una versión del catálogo.** Con más repos pueden
  aparecer herramientas válidas que no están en las listas, y alguna consulta sin
  respuesta puede dejar de serlo.
- **Los tiempos varían entre corridas** según la carga de la máquina; se comparan
  en proporción. La RAM de EmbeddingGemma es una estimación.
