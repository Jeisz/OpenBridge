-- Filas de la IA cuyo github_id ya no está en el catálogo (public.v_repos_for_ai).
-- Solo las muestra; borrarlas es una decisión aparte (un repo puede volver al catálogo).
-- Se puede correr con el usuario escritor. Sin filas = sin huérfanos.

select 'ai_repo_enrichment' as tabla, e.github_id, count(*) as filas
from ai.ai_repo_enrichment e
where not exists (select 1 from public.v_repos_for_ai v where v.github_id = e.github_id)
group by e.github_id

union all
select 'ai_repo_categories', c.github_id, count(*)
from ai.ai_repo_categories c
where not exists (select 1 from public.v_repos_for_ai v where v.github_id = c.github_id)
group by c.github_id

union all
select 'ai_integration_ideas', i.github_id, count(*)
from ai.ai_integration_ideas i
where not exists (select 1 from public.v_repos_for_ai v where v.github_id = i.github_id)
group by i.github_id

union all
select 'ai_embeddings', m.github_id, count(*)
from ai.ai_embeddings m
where not exists (select 1 from public.v_repos_for_ai v where v.github_id = m.github_id)
group by m.github_id

order by tabla, github_id;
