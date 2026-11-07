-- Ideas de integración: conteos para verificar una escritura.
-- Solo lee. Se puede correr con el usuario escritor de la IA.

-- 1. Ideas por tipo, origen y estado de revisión.
select integration_type, generated_by, reviewed_at is not null as revisada, count(*) as ideas
from ai.ai_integration_ideas
group by 1, 2, 3
order by 1, 2, 3;

-- 2. Totales: repos con ideas e ideas.
select count(distinct github_id) as repos_con_ideas, count(*) as ideas
from ai.ai_integration_ideas;

-- 3. Repos con más de 3 ideas. Debe quedar vacío.
select github_id, count(*) as ideas
from ai.ai_integration_ideas
group by github_id
having count(*) > 3;

-- 4. Repos con un tipo repetido. Debe quedar vacío.
select github_id, integration_type, count(*) as ideas
from ai.ai_integration_ideas
group by github_id, integration_type
having count(*) > 1;

-- 5. Datos de ejemplo que hayan quedado. Debe quedar vacío.
select id from ai.ai_integration_ideas where based_on_hash = 'seed-ejemplo';
