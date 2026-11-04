# Diagnóstico de latencia · paso generar

Generado con `python -m ai.eval.diagnose_latency` el 2026-11-03 a las 02:15. Caso `academia-online`; necesidades: auth, storage, payments, ai. Misma petición y esquema cerrado del pedido para todas las variantes; 1 llamada en frío + 1 en caliente; streaming.

Medianas en caliente. Primer texto y total en segundos; escritura en caracteres visibles por segundo desde el primer texto.

| Variante | Frío: primer texto / total | Primer texto | Total | Tokens salida | Caracteres | Car/token | Escritura | JSON válido | Errores |
|---|---|---|---|---|---|---|---|---|---|
| claude-compat-sin-pensar | 3.0 / 6.0 | 1.8 | 4.7 | 662.0 | 1757.0 | 2.7 | 611.4 | 1/1 | 0/2 |

## Errores

(ninguno)