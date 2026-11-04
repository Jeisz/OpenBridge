# Diagnóstico de latencia · paso generar

Generado con `python -m ai.eval.diagnose_latency` el 2026-11-03 a las 02:14. Caso `tienda-ropa`; necesidades: search, payments, automation, analytics. Misma petición y esquema cerrado del pedido para todas las variantes; 1 llamada en frío + 1 en caliente; streaming.

Medianas en caliente. Primer texto y total en segundos; escritura en caracteres visibles por segundo desde el primer texto.

| Variante | Frío: primer texto / total | Primer texto | Total | Tokens salida | Caracteres | Car/token | Escritura | JSON válido | Errores |
|---|---|---|---|---|---|---|---|---|---|
| claude-compat-sin-pensar | 3.7 / 7.6 | 1.2 | 5.3 | 1053.0 | 2689.0 | 2.6 | 659.4 | 1/1 | 0/2 |

## Errores

(ninguno)