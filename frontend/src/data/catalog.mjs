import fixtures from '../mocks/catalog.fixtures.json' with {type:'json'};
import presentation from '../mocks/catalog-presentation.json' with {type:'json'};
import categoryList from '../generated/categories.json' with {type:'json'};
import defaultCard from '../mocks/catalog-default.fixture.json' with {type:'json'};
export const catalogRepos=fixtures;
export const catalogCategories=categoryList.categories.map(category=>({...category,name:category.id==='dev-tools'?'Desarrollo':category.name}));
export function populatedCategories(categories,tools){
 const used=new Set(tools.flatMap(tool=>(tool.categories??[]).map(category=>category.id)));
 return categories.filter(category=>used.has(category.id));
}
const categoryNames=new Map(catalogCategories.map(c=>[c.id,c.name]));
const dateLabel=value=>value?new Intl.DateTimeFormat('es-CL',{day:'numeric',month:'short',year:'numeric',timeZone:'America/Punta_Arenas'}).format(new Date(value)):'Sin datos';
// Translate the contract once; presentation metadata is local, never API payload.
export function toTool(repo,local=presentation[repo.full_name]??{}){
 const categories=(repo.categories??[]).map(({category_id})=>({id:category_id,name:categoryNames.get(category_id)??category_id}));
 return {id:local.id??String(repo.github_id),githubId:repo.github_id,name:local.name??repo.full_name.split('/').at(-1),full_name:repo.full_name,repo:repo.full_name,
 category:categories[0]?.name??'Sin categoría',categories,description:repo.summary_es??repo.description??'Sin descripción disponible.',
 license_spdx_id:repo.license_spdx_id,language:repo.language??'Sin datos',license:!repo.license_spdx_id||repo.license_spdx_id==='NOASSERTION'?'Revisar licencia':repo.license_spdx_id,
 stars:repo.stargazers_count,activity:dateLabel(repo.pushed_at),maintained:local.maintained??null,archived:repo.archived,disabled:local.disabled??false,dataSource:local.dataSource,syncedAt:local.syncedAt};
}
export function toCardDetail(repo,local=presentation[repo.full_name]??{}){
 return {healthScore:repo.health_score??null,openIssues:repo.open_issues_count??null,tag:local.tag,version:local.version??null,docs:local.docs??repo.homepage,
 releasePublishedAt:local.releasePublishedAt??null,releaseUrl:local.releaseUrl??null,lastCommitAt:local.lastCommitAt??null,openPullRequests:local.openPullRequests??null};
}
export const catalogRecords=fixtures.map(repo=>({...toTool(repo),...toCardDetail(repo)}));
// Fictional visual demo is not a Repo and stays outside the contract fixtures.
catalogRecords.splice(9,0,structuredClone(defaultCard));
export const mockCatalog={
 async list(){return {items:structuredClone(catalogRecords),total:catalogRecords.length};},
 async getById(id){return structuredClone(catalogRecords.find(record=>record.id===id)??null);}
};
export const githubSnapshotAt=Object.values(presentation).find(record=>record.dataSource==='github_snapshot')?.syncedAt??null;
export function snapshotDate(value){return value?new Intl.DateTimeFormat('es-CL',{dateStyle:'medium',timeStyle:'short',timeZone:'America/Punta_Arenas'}).format(new Date(value)):'';}
export function repositoryStatus(tool){return ['github_snapshot','api'].includes(tool.dataSource)?(tool.disabled?'Deshabilitado':tool.archived?'Archivado':'No archivado'):'Por confirmar';}

export function toolCategoryNames(tool){return tool.categories?.length?tool.categories.map(category=>category.name):[tool.category];}
