# Diagnóstico de latencia · paso generar

Generado con `python -m ai.eval.diagnose_latency` el 2026-11-03 a las 01:15. Caso `pantalla-rag-corto`; necesidades: ai, auth. Misma petición y mismo esquema fijo para todas las variantes; 1 llamada en frío + 2 en caliente; streaming.

Medianas en caliente. Primer texto y total en segundos; escritura en caracteres visibles por segundo desde el primer texto.

| Variante | Frío: primer texto / total | Primer texto | Total | Tokens salida | Caracteres | Car/token | Escritura | JSON válido | Errores |
|---|---|---|---|---|---|---|---|---|---|
| ollama | 25.4 / 37.1 | 2.3 | 13.9 | 582.5 | 2443.5 | 4.2 | 208.6 | 2/2 | 0/3 |

## Errores

(ninguno)