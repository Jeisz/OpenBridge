-- Lector de la API del catálogo: solo lectura de lo que consulta backend/app/repositories/repos.py.
-- La aplica el administrador. Sin contraseña en este archivo: se asigna con \password openbridge_api_reader.
-- Permisos por tabla, no por columna: las columnas que se agreguen después también se pueden leer.
-- Si se borra y se vuelve a crear la vista o una tabla, sus permisos se pierden: ejecutar este archivo otra vez.
-- Idempotente: se puede ejecutar más de una vez sin error.

begin;

do $$
begin
    if not exists (select from pg_roles where rolname = 'openbridge_api_reader') then
        create role openbridge_api_reader login;
    end if;
end
$$;

-- Catálogo: la ficha lee la vista; el listado y parte de la ficha leen la tabla base.
grant usage on schema public to openbridge_api_reader;
grant select on public.v_repos_for_ai, public.catalog_repositories to openbridge_api_reader;

-- La tabla base tiene seguridad por filas: sin una política, el lector no ve ninguna fila.
-- Esta política solo permite leer; insertar, actualizar y borrar siguen sin permiso.
drop policy if exists openbridge_api_repositories_select on public.catalog_repositories;
create policy openbridge_api_repositories_select on public.catalog_repositories
    for select
    to openbridge_api_reader
    using (true);

-- Resultados de la IA que muestra la API.
grant usage on schema ai to openbridge_api_reader;
grant select on ai.ai_repo_enrichment, ai.ai_repo_categories, ai.ai_integration_ideas
    to openbridge_api_reader;

-- La API no lee los vectores de búsqueda.
revoke select on ai.ai_embeddings from openbridge_api_reader;

commit;
