import {toTool,toCardDetail,catalogCategories} from './catalog.mjs';
import {toIntegrationIdea} from './integrationIdeas.mjs';
import presentation from '../mocks/catalog-presentation.json' with {type:'json'};

export function adaptApiRepo(repo,categories){
 if(!repo||typeof repo.full_name!=='string'||!Number.isInteger(repo.github_id)||!Number.isFinite(repo.stargazers_count)||typeof repo.archived!=='boolean'||!Number.isFinite(Date.parse(repo.pushed_at))||!Array.isArray(repo.categories))throw new Error('Respuesta del catálogo inválida');
 if(repo.summary_es!=null&&(typeof repo.summary_es!=='string'||Array.from(repo.summary_es).length>250))throw new Error('Resumen del catálogo inválido');
 const local=presentation[repo.full_name]??{};
 // Solo identidad de presentación; nunca mezclar estadísticas ni estados mock.
 const identity={id:local.id??String(repo.github_id),name:local.name??repo.full_name.split('/').at(-1)};
 const tool={...toTool(repo,identity),...toCardDetail(repo,identity),dataSource:'api',disabled:repo.disabled??null,maintained:repo.is_maintained??null};
 const names=new Map(categories.map(c=>[c.id,c.name]));
 tool.categories=repo.categories.map(c=>({id:c.category_id,name:names.get(c.category_id)??c.category_id}));
 tool.category=tool.categories[0]?.name??'Sin categoría';
 tool.description=repo.summary_es||repo.description||'';
 return {tool,profile:{summary:tool.description||null,homepage:repo.homepage||null,ideas:[]}};
}
export class CatalogHttpError extends Error{
 constructor(status,code){super('No se pudieron cargar los datos');this.name='CatalogHttpError';this.status=status;this.code=code;}
}
export function createCatalogHttp({baseUrl,fetchImpl=globalThis.fetch}){
 const base=baseUrl.endsWith('/')?baseUrl:baseUrl+'/';
 async function get(path,signal){
  const response=await fetchImpl(new URL(path,base),{signal});
  if(!response.ok){
   let code;try{const body=await response.json();if(['repo_not_found','invalid_request','catalog_unavailable'].includes(body?.error?.code))code=body.error.code;}catch{}
   throw new CatalogHttpError(response.status,code);
  }
  return response;
 }
 const path=name=>'repos/'+name.split('/').map(encodeURIComponent).join('/');
 return {
  async list(signal){
   // Load the complete catalog before publishing state: local filters must not
   // silently search only the first server page. A failed page fails the load.
   const repos=[];let pages=1,total=null;
   for(let page=1;page<=pages;page++){
    signal?.throwIfAborted();
    const response=await get(`repos?page=${page}&page_size=100`,signal);
    const batch=await response.json();
    if(!Array.isArray(batch))throw new Error('Respuesta del catálogo inválida');
    const read=name=>response.headers?.get(name)??null;
    const values=['X-Total-Pages','X-Total-Count','X-Page','X-Page-Size'].map(read);
    if(values.some(value=>value!==null)){
     if(values.some(value=>value===null||!/^\d+$/.test(value)))throw new Error('Paginación inválida');
     const [count,size,current,perPage]=values.map(Number);
     if(!values.every(value=>Number.isSafeInteger(Number(value)))||current!==page||perPage<1||count!==Math.ceil(size/perPage)||batch.length!==Math.min(perPage,Math.max(0,size-(page-1)*perPage)))throw new Error('Paginación inválida');
     if(page>1&&(count!==pages||size!==total))throw new Error('El catálogo cambió durante la carga');
     pages=count;total=size;
    }else if(page>1)throw new Error('Paginación inválida');
    repos.push(...batch);
   }
   if(total!==null&&repos.length!==total)throw new Error('Catálogo incompleto');
   const categories=catalogCategories;
   if(!Array.isArray(repos)||!Array.isArray(categories)||!categories.every(c=>typeof c.id==='string'&&typeof c.name==='string'))throw new Error('Respuesta del catálogo inválida');
   const records=repos.map(repo=>adaptApiRepo(repo,categories));
   if(new Set(records.map(r=>r.tool.id)).size!==records.length)throw new Error('Identificadores repetidos');
   return {tools:records.map(r=>r.tool),profiles:Object.fromEntries(records.map(r=>[r.tool.id,r.profile])),categories};
  },
  async detail(name,categories,signal){
   const response=await get(path(name),signal);
   const payload=await response.json();
   if(!payload||payload.repo?.full_name!==name||!Array.isArray(payload.integration_ideas)||payload.integration_ideas.length>3)throw new Error('Ficha inválida');
   const record=adaptApiRepo(payload.repo,categories);
   if(record.tool.archived&&payload.integration_ideas.length)throw new Error('Ficha inválida');
   const ideas=payload.integration_ideas.map(idea=>{
    if(!idea||idea.full_name!==name||typeof idea.id!=='string'||typeof idea.title!=='string'||typeof idea.summary!=='string'||!['rest_api','docker','sdk','webhook'].includes(idea.integration_type)||!['low','medium','high'].includes(idea.difficulty)||!Array.isArray(idea.compatible_stack)||!idea.compatible_stack.every(v=>typeof v==='string')||!['dependencies','triggers'].every(k=>idea[k]===undefined||(Array.isArray(idea[k])&&idea[k].every(v=>typeof v==='string')))||typeof idea.docs_url!=='string'||!/^https?:\/\//.test(idea.docs_url)||(idea.snippet!=null&&typeof idea.snippet!=='string')||(idea.snippet&&typeof idea.snippet_language!=='string'))throw new Error('Idea de integración inválida');
    return toIntegrationIdea(idea);
   });
   return {...record,profile:{...record.profile,ideas}};
  }
 };
}
