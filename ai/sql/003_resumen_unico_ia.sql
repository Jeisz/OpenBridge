-- Resumen único de la IA (Repo v1.2): summary_es hasta 250 caracteres; sin about_es ni features.
-- La aplica el administrador después de 001 y 002. Solo cambia ai.ai_repo_enrichment.
-- Idempotente: se puede ejecutar más de una vez sin error.

begin;

-- La restricción se reemplaza con nombre explícito (el mismo que PostgreSQL le dio en 001).
alter table ai.ai_repo_enrichment
    drop constraint if exists ai_repo_enrichment_summary_es_check;
alter table ai.ai_repo_enrichment
    add constraint ai_repo_enrichment_summary_es_check
    check (char_length(summary_es) <= 250);

-- Al quitar cada columna, PostgreSQL quita también su restricción.
alter table ai.ai_repo_enrichment
    drop column if exists about_es,
    drop column if exists features;

commit;
