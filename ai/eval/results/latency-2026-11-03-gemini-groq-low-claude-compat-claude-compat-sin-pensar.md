# Diagnóstico de latencia · paso generar

Generado con `python -m ai.eval.diagnose_latency` el 2026-11-03 a las 01:35. Caso `pantalla-rag-corto`; necesidades: ai, auth. Misma petición y mismo esquema fijo para todas las variantes; 1 llamada en frío + 3 en caliente; streaming.

Medianas en caliente. Primer texto y total en segundos; escritura en caracteres visibles por segundo desde el primer texto.

| Variante | Frío: primer texto / total | Primer texto | Total | Tokens salida | Caracteres | Car/token | Escritura | JSON válido | Errores |
|---|---|---|---|---|---|---|---|---|---|
| gemini | 1.3 / 3.4 | 1.4 | 2.0 | 204.0 | 932.0 | 4.6 | 1600.9 | 3/3 | 0/4 |
| groq-low | 1.6 / 1.6 | 1.8 | 1.8 | 369.0 | 1190.0 | 3.2 | 809907.6 | 3/3 | 0/4 |
| claude-compat | 4.9 / 7.5 | 7.3 | 9.2 | 1696.0 | 1448.0 | 0.9 | 631.7 | 3/3 | 0/4 |
| claude-compat-sin-pensar | 1.6 / 3.9 | 1.2 | 4.4 | 620.0 | 1681.0 | 2.7 | 654.1 | 3/3 | 0/4 |

## Errores

(ninguno)