# Abstención del asistente: decisión y evidencia

**Decisión (7-nov-2026):** antes de elegir una herramienta, el paso que arma el
mapa juzga si el mejor candidato **hace** lo que pide la necesidad
(`fit: serves`) o solo se relaciona con ella (`only_related`). Con
`only_related`, el código deja la caja sin herramienta y la necesidad pasa a las
limitaciones, aunque el modelo haya escrito un nombre.

## Por qué

La búsqueda mide parecido de texto: un repo puede superar el umbral sin
resolver la necesidad (una librería que se conecta a una base de datos no es la
base de datos). Con el texto de búsqueda actual, el umbral deja pasar 11 de 15
consultas nuevas sin respuesta (`SEARCH_DECISION.md`): el freno tiene que estar
en el paso que elige. La regla es general: no nombra repos ni categorías y
sigue valiendo si el catálogo crece.

## Cómo se midió

- Gemini 3.5 Flash-Lite, 3 corridas por caso, el mismo código salvo el cambio.
- Criterio fijado antes de medir:
  - Validación (10 casos): la peor corrida nueva de abstención supera a la mejor
    de la línea base; "eligió un aceptable", punta a punta y status no bajan de
    la peor corrida de la línea base.
  - Casos reservados (12, escritos antes del cambio y corridos una sola vez con
    la versión elegida): abstención media por encima de la mejor corrida de la
    línea base; como máximo 3 fallos en "eligió un aceptable" y punta a punta.
- Máximo 2 intentos; el primero cumplió.

## Resultados (rango entre las 3 corridas)

| | Validación: antes → después | Reservados: antes → después |
|---|---|---|
| Se abstuvo (donde no había herramienta) | 42–54 % → 64–73 % | 56–78 % → 78–89 % |
| Eligió un aceptable | 86–100 % → 88–100 % | 100 % → 100 % |
| Punta a punta | 60–78 % → 78–89 % | 100 % → 100 % |
| Status correcto | 70–80 % → 80–90 % | 67–83 % → 83–92 % |
| Textos del modelo que hablan del catálogo | 4–7 → 3–8 | 10–14 → 3–6 |

## Límites

- 10 y 12 casos: los números indican una dirección, no son estadística firme.
- Siguen fallando necesidades parecidas a algo del catálogo pero no cubiertas:
  base de datos relacional (elige librerías de acceso a datos), embudos de
  conversión y chat entre personas.
- La regla "no afirmar qué tiene el catálogo" mejora en un conjunto de casos y
  no en el otro.
- El paso de entender no detecta algunas necesidades (por ejemplo, permisos por
  sucursal): ahí el usuario no ve ni la limitación. Esta métrica no lo mide.
- El juicio va antes del nombre del repo en el esquema; se supone que el modelo
  escribe los campos en ese orden. No se verificó en el texto crudo.

Reportes en `results/`: `assistant-2026-11-06-2359-validation-gemini.md` y
`assistant-2026-11-07-0711-validation-gemini.md` (validación),
`assistant-2026-11-07-0653-holdout-gemini.md` y
`assistant-2026-11-07-0730-holdout-gemini.md` (reservados).
