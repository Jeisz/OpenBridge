-- Tablas de la IA de OpenBridge (v0).
-- Las aplica el administrador; el usuario escritor de la IA solo lee y escribe filas.
-- Idempotente: se puede ejecutar más de una vez sin error.
-- Las reglas finas (longitud de cada elemento, categoría válida) las valida el contrato en Python;
-- aquí solo las que protegen la forma básica de los datos.

begin;

create extension if not exists vector with schema extensions;
create schema if not exists ai;

-- 1 fila por repositorio: textos que genera el LLM.
create table if not exists ai.ai_repo_enrichment (
    github_id     bigint primary key,
    summary_es    text check (char_length(summary_es) <= 400),
    about_es      text check (char_length(about_es) <= 600),
    features      text[] not null default '{}' check (cardinality(features) <= 4),
    use_cases     text[] not null default '{}' check (cardinality(use_cases) <= 4),
    ai_input_hash text not null,
    processed_at  timestamptz not null default now()
);

-- 1 fila por categoría asignada (máx. 3 por repositorio; rank 1 = principal).
create table if not exists ai.ai_repo_categories (
    github_id   bigint   not null,
    category_id text     not null,
    assigned_by text     not null check (assigned_by in ('rule', 'llm', 'human')),
    rank        smallint not null check (rank between 1 and 3),
    primary key (github_id, category_id),
    unique (github_id, rank)
);

-- 1 fila por idea de integración (contrato IntegrationIdea v1.1, con github_id en vez de full_name).
create table if not exists ai.ai_integration_ideas (
    id               text primary key,
    github_id        bigint not null,
    title            text not null check (char_length(title) <= 120),
    integration_type text not null check (integration_type in ('rest_api', 'docker', 'sdk', 'webhook')),
    summary          text not null check (char_length(summary) <= 300),
    compatible_stack text[] not null check (cardinality(compatible_stack) >= 1),
    dependencies     text[] not null default '{}',
    difficulty       text not null check (difficulty in ('low', 'medium', 'high')),
    triggers         text[] not null default '{}',
    snippet          text,
    snippet_language text,
    docs_url         text not null,
    generated_by     text not null check (generated_by in ('llm', 'human')),
    reviewed_at      timestamptz,
    based_on_hash    text not null,
    check (snippet is null or snippet_language is not null)
);
create index if not exists ai_integration_ideas_github_id_idx
    on ai.ai_integration_ideas (github_id);

-- 1 fila por repositorio: vector de búsqueda (EmbeddingGemma-300m, 768 dimensiones). Interna de la IA.
create table if not exists ai.ai_embeddings (
    github_id     bigint primary key,
    embedding     extensions.vector(768) not null,
    model         text not null,
    ai_input_hash text not null
);

commit;
