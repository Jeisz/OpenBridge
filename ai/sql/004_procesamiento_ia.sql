-- Registro de procesamiento de la IA, y lectura de lo publicado para el lector de la IA.
-- La aplica el administrador después de 001, 002 y 003.
-- Idempotente: se puede ejecutar más de una vez sin error.

begin;

-- 1 fila por repositorio y tipo de dato: con qué entrada y con qué reglas se generó lo publicado.
-- Existe aunque el resultado sea vacío (un repo sin ideas), para no confundirlo con "nunca procesado".
-- Así la base sola dice si los datos de la IA siguen al día con el catálogo.
create table if not exists ai.ai_processing (
    github_id      bigint      not null,
    kind           text        not null check (kind in ('enrichment', 'ideas', 'embedding')),
    full_name      text        not null,                -- nombre del repo al generar (las ideas lo llevan en sus enlaces)
    ai_input_hash  text        not null,                -- huella de lo que leyó el modelo
    provider       text        not null,                -- proveedor del modelo
    model          text        not null,
    prompt_version text,                                -- versión de las reglas; null si no aplica
    skipped        text,                                -- motivo si no se llamó al modelo
    processed_at   timestamptz not null default now(),
    primary key (github_id, kind)
);

-- Escritor de la IA: filas de la tabla nueva, igual que en las demás tablas de ai.
grant select, insert, update, delete on ai.ai_processing to openbridge_ai_writer;

-- Lector de la IA (ya lee public.v_repos_for_ai): además, lo publicado que usa el asistente
-- y el registro de procesamiento. Sin ideas (el asistente no las usa) ni escritura.
grant usage on schema ai to openbridge_ai_reader;
grant select on ai.ai_repo_enrichment, ai.ai_repo_categories, ai.ai_processing
    to openbridge_ai_reader;

commit;
