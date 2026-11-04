-- Usuario escritor de la IA: lee la vista del catálogo y escribe filas en el esquema ai.
-- No crea ni modifica tablas: eso lo hace el administrador con 001_tablas_ia.sql.
-- Sin contraseña en este archivo: el administrador la asigna después con \password openbridge_ai_writer.
-- Idempotente: se puede ejecutar más de una vez sin error.

begin;

do $$
begin
    if not exists (select from pg_roles where rolname = 'openbridge_ai_writer') then
        create role openbridge_ai_writer login;
    end if;
end
$$;

-- Leer el catálogo solo a través de la vista (no la tabla base).
grant usage on schema public to openbridge_ai_writer;
grant select on public.v_repos_for_ai to openbridge_ai_writer;

-- Filas en las tablas de la IA: leer, insertar, actualizar y borrar. Sin TRUNCATE ni DDL.
grant usage on schema ai to openbridge_ai_writer;
grant select, insert, update, delete on all tables in schema ai to openbridge_ai_writer;

-- Tablas que el administrador cree más adelante en ai reciben los mismos permisos.
alter default privileges for role postgres in schema ai
    grant select, insert, update, delete on tables to openbridge_ai_writer;

-- Tipo y operadores de pgvector (por ejemplo <=>), instalados en el esquema extensions.
grant usage on schema extensions to openbridge_ai_writer;

-- Para que el código escriba <=> sin el prefijo extensions.
alter role openbridge_ai_writer set search_path = "$user", public, extensions;

commit;
