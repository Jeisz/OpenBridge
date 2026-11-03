import test from 'node:test';
import assert from 'node:assert/strict';
import {adaptApiRepo,createCatalogHttp} from '../src/data/catalogHttp.mjs';
const repo={full_name:'keycloak/keycloak',github_id:1,description:'Descripción del servidor',summary_es:null,stargazers_count:42,pushed_at:'2026-01-01T00:00:00Z',archived:false,categories:[{category_id:'auth'}],homepage:null};
test('HTTP records preserve server fields without local mock statistics',()=>{
 const {tool,profile}=adaptApiRepo(repo,[{id:'auth',name:'Autenticación'}]);
 assert.equal(tool.id,'keycloak');assert.equal(tool.stars,42);assert.equal(tool.healthScore,null);assert.equal(tool.maintained,null);assert.equal(tool.dataSource,'api');assert.equal(tool.description,profile.summary);assert.deepEqual(profile.ideas,[]);
});
test('HTTP list/detail use the same source and propagate cancellation',async()=>{
 const signal=new AbortController().signal,paths=[];
 const client=createCatalogHttp({baseUrl:'http://localhost:8000/',fetchImpl:async(url,options)=>{
  assert.equal(options.signal,signal);paths.push(url.pathname);
  return {ok:true,json:async()=>url.pathname.endsWith('categories')?[{id:'auth',name:'Autenticación'}]:url.pathname.endsWith('/repos')?[repo]:{repo,integration_ideas:[]}};
 }});
 const list=await client.list(signal);const detail=await client.detail(repo.full_name,list.categories,signal);
 assert.deepEqual(list.tools[0],detail.tool);assert.ok(paths.includes('/repos/keycloak/keycloak'));assert.ok(!paths.includes('/categories'));
});
test('HTTP errors and malformed data do not fall back to mocks',async()=>{
 const client=createCatalogHttp({baseUrl:'http://localhost/',fetchImpl:async()=>({ok:false,status:500})});
 await assert.rejects(client.list(),/cargar/);
 assert.throws(()=>adaptApiRepo({...repo,stargazers_count:'42'},[]),/inválida/);
});
test('detail carries ideas in one request and rejects cross-repository data',async()=>{
 const idea={id:'test',full_name:repo.full_name,title:'Prueba',summary:'Resumen',integration_type:'sdk',difficulty:'low',compatible_stack:['JavaScript'],dependencies:[],triggers:[],snippet:null,docs_url:'https://www.keycloak.org/docs/',generated_by:'human'};
 let calls=0;
 const client=createCatalogHttp({baseUrl:'http://localhost/',fetchImpl:async()=>{calls++;return {ok:true,json:async()=>({repo,integration_ideas:[idea]})};}});
 const record=await client.detail(repo.full_name,[]);
 assert.equal(calls,1);assert.equal(record.profile.ideas[0].title,'Prueba');
 idea.full_name='other/repo';await assert.rejects(client.detail(repo.full_name,[]),/inválida/);
});

test('all pages are collected before filtering, including secondary categories',async()=>{
 const calls=[];
 const client=createCatalogHttp({baseUrl:'http://localhost/',fetchImpl:async url=>{
  assert.equal(url.searchParams.get('page_size'),'100');
  const page=Number(url.searchParams.get('page'));calls.push(page);
  return {ok:true,headers:new Headers({'X-Total-Pages':'2','X-Total-Count':'2','X-Page':String(page),'X-Page-Size':'1'}),json:async()=>[{...repo,full_name:`owner/repo${page}`,github_id:page}]};
 }});
 const result=await client.list();assert.deepEqual(calls,[1,2]);assert.equal(result.tools.length,2);
});
test('a failed later page never returns a partial catalog and preserves error code',async()=>{
 const client=createCatalogHttp({baseUrl:'http://localhost/',fetchImpl:async url=>Number(url.searchParams.get('page'))===1?{ok:true,headers:new Headers({'X-Total-Pages':'2','X-Total-Count':'2','X-Page':'1','X-Page-Size':'1'}),json:async()=>[repo]}:{ok:false,status:503,json:async()=>({error:{code:'catalog_unavailable',message:'private server detail'}})}});
 await assert.rejects(client.list(),{status:503,code:'catalog_unavailable'});
});
test('empty catalog and cancelled loading preserve their states',async()=>{
 const client=createCatalogHttp({baseUrl:'http://localhost/',fetchImpl:async()=>({ok:true,headers:new Headers({'X-Total-Pages':'0','X-Total-Count':'0','X-Page':'1','X-Page-Size':'20'}),json:async()=>[]})});
 assert.equal((await client.list()).tools.length,0);
 const controller=new AbortController();controller.abort();await assert.rejects(client.list(controller.signal),{name:'AbortError'});
});
test('Repo v1.2 booleans and nulls come from API rather than presentation defaults',()=>{
 for(const value of [true,false,null]){
  const {tool}=adaptApiRepo({...repo,disabled:value,is_maintained:value},[]);
  assert.equal(tool.disabled,value);assert.equal(tool.maintained,value);
 }
});
test('canonical detail links resolve without a loaded catalog',async()=>{
 const {detailTarget}=await import('../src/data/detailTarget.mjs');
 assert.equal(detailTarget('owner/new-repo',[]).fullName,'owner/new-repo');
 assert.equal(detailTarget('keycloak',[]).fullName,'keycloak/keycloak');
 assert.equal(detailTarget('unknown-id',[]).fullName,null);
});
