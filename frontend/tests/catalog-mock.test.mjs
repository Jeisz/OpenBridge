import test from 'node:test';
import assert from 'node:assert/strict';
import {profiles} from '../src/toolProfiles.js';
import {mockCatalog,catalogRepos,toTool,toCardDetail} from '../src/data/catalog.mjs';

test('catalog mock has unique IDs and usable card metrics',async()=>{
 const {items,total}=await mockCatalog.list();
 assert.equal(total,20);assert.equal(new Set(items.map(x=>x.id)).size,total);
 for(const item of items){assert.ok(item.name&&item.description&&item.category);assert.ok(item.healthScore===null||Number.isFinite(item.healthScore)&&item.healthScore>=0&&item.healthScore<=100);assert.ok(item.stars>=0);assert.equal(item.dataSource,item.repo?'github_snapshot':'mock');assert.ok(Number.isFinite(Date.parse(item.syncedAt)));assert.equal(item.full_name,item.repo);}
});
test('detail matches list, missing IDs return null, and responses cannot mutate fixtures',async()=>{
 const {items}=await mockCatalog.list();const item=await mockCatalog.getById(items[0].id);assert.deepEqual(item,items[0]);item.name='Changed';assert.notEqual((await mockCatalog.getById(item.id)).name,'Changed');assert.equal(await mockCatalog.getById('missing'),null);
 const fallback=await mockCatalog.getById('herramienta-de-ejemplo');assert.equal(fallback.repo,null);assert.equal(fallback.stars,0);
});

test('detail profiles use contract prose and no editorial features',async()=>{
 const {items}=await mockCatalog.list();
 for(const tool of items){const repo=catalogRepos.find(repo=>repo.full_name===tool.full_name);assert.equal(profiles[tool.id]?.summary,repo?.summary_es||repo?.description||null);assert.ok(!('features' in profiles[tool.id]));assert.equal(profiles[tool.id]?.homepage,repo?.homepage||null);assert.ok(Array.isArray(profiles[tool.id]?.ideas));}
 for(const id of ['react','nextjs','fastapi','nestjs','django','valkey','rabbitmq','prometheus','grafana','traefik'])assert.ok(items.some(tool=>tool.id===id));
});

test('real catalog metrics match their captured GitHub source without invented health or releases',async()=>{
 const {default:snapshot}=await import('../src/mocks/github-snapshot.json',{with:{type:'json'}});
 const {items}=await mockCatalog.list();
 assert.equal(items.filter(item=>item.dataSource==='github_snapshot').length,19);
 for(const [index,item] of items.entries()){
  if(!item.repo)continue;
  const source=Object.values(snapshot.data).find(repo=>repo?.nameWithOwner===item.full_name);
  assert.equal(item.stars,source.stargazerCount);assert.equal(item.openIssues,source.issues.totalCount+source.pullRequests.totalCount);assert.equal(item.openPullRequests,source.pullRequests.totalCount);
  assert.equal(item.version,source.latestRelease?.tagName??null);assert.equal(item.archived,source.isArchived);assert.equal(item.syncedAt,snapshot.captured_at);
  assert.equal(item.healthScore,null);assert.equal(item.maintained,null);
  assert.equal(item.lastCommitAt,source.defaultBranchRef?.target?.committedDate??null);
 }
});


test('contract fixtures use numeric GitHub IDs and keep presentation outside the payload',()=>{
 assert.equal(catalogRepos.length,19);
 for(const repo of catalogRepos){
  assert.ok(Number.isInteger(repo.github_id)&&repo.github_id>0);
  assert.ok(repo.full_name.includes('/'));assert.ok(repo.stargazers_count>=0);
  assert.ok(!('stars' in repo)&&!('id' in repo)&&!('name' in repo)&&!('color' in repo));
  assert.equal(toTool(repo).stars,repo.stargazers_count);
  assert.equal(toCardDetail(repo).healthScore,repo.health_score);
 }
});
test('adapter handles nullable data, multiple categories and unknown repos without fake metrics',()=>{
 const repo={...catalogRepos[0],full_name:'example/tool',github_id:123,summary_es:null,description:null,language:null,license_spdx_id:null,health_score:null,open_issues_count:null,categories:[]};
 const tool=toTool(repo);assert.equal(tool.id,'123');assert.equal(tool.name,'tool');assert.equal(tool.category,'Sin categoría');assert.equal(tool.maintained,null);assert.equal(tool.description,'Sin descripción disponible.');assert.equal(tool.license,'Revisar licencia');assert.equal(toCardDetail(repo).openIssues,null);
 const multi=toTool({...repo,categories:[{category_id:'auth',assigned_by:'human'},{category_id:'database',assigned_by:'rule'}]});
 assert.equal(multi.category,'Autenticación');assert.equal(multi.categories.length,2);assert.equal(multi.categories[1].name,'Bases de datos');
 assert.equal(toTool({...repo,summary_es:'Resumen',description:'Original'}).description,'Resumen');
});
