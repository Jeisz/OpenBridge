-- Lectura de los vectores de búsqueda para el lector de la IA (el servicio los carga al arrancar).
-- La aplica el administrador después de 004.
-- Idempotente: se puede ejecutar más de una vez sin error.

begin;

grant select on ai.ai_embeddings to openbridge_ai_reader;

commit;
