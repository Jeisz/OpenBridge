# Espacio de trabajo del asistente — primera iteración local

## Alcance
Consultas independientes. El input conserva la idea; no se añade memoria conversacional ni persistencia tras recargar. Mantener diseño, efectos y API actuales.

## Pasos
1. Conservar el prompt enviado en éxito, error y cancelación. Mantener resultado anterior durante una petición nueva.
2. Input fijo abajo al iniciar una consulta válida. Reservar espacio según su altura, limitar texto largo y mantener Detener.
3. Alternar catálogo/asistente desde el navbar. Mantener componentes montados para conservar filtros, respuesta y borrador; guardar scroll de cada vista.
4. Mantener la consulta al abrir una ficha. Mostrar supuestos/limitaciones sin acordeones también en respuestas sin evidencia.
5. Validar navegación, cancelación, nueva consulta, filtros, móvil y compilación.

## Iteraciones posteriores
- Pulir transición al modo flotante y ajuste al teclado móvil real.
- Revisar resultados extensos y posición de lectura al reemplazar una propuesta.
- Diseño de conexiones pendiente de selección/implementación; no alterar el contrato.
