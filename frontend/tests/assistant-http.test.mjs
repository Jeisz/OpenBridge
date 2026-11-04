import test from 'node:test';
import assert from 'node:assert/strict';
import {createHttpAssistantProvider} from '../src/data/assistantHttp.mjs';
import {createCatalogHttp} from '../src/data/catalogHttp.mjs';

test('known codes choose local messages without remote text or status pairing',async()=>{
 for(const code of ['invalid_query','invalid_response','provider_unavailable','timeout']){
  const provider=createHttpAssistantProvider({baseUrl:'https://ai.example/',fetchImpl:async()=>({ok:false,status:500,json:async()=>({error:{code}})})});
  await assert.rejects(provider.ask({query:'Una aplicación para mi equipo'}),error=>error.code===code&&error.message.length>0);
 }
});
test('unknown codes and non-JSON failures never expose server diagnostics',async()=>{
 for(const json of [async()=>({error:{code:'unknown',message:'private diagnostics'}}),async()=>({error:{code:'toString'}}),async()=>{throw new SyntaxError('private diagnostics');}]){
  const provider=createHttpAssistantProvider({baseUrl:'https://ai.example/',fetchImpl:async()=>({ok:false,status:503,json})});
  await assert.rejects(provider.ask({query:'Una aplicación para mi equipo'}),error=>error.code==='technical_error'&&!error.message.includes('private'));
 }
});
test('assistant failure on its own origin leaves catalog list and detail usable',async()=>{
 const urls=[];
 const repo={full_name:'example/tool',github_id:987,stargazers_count:3,pushed_at:'2026-01-01T00:00:00Z',archived:false,categories:[]};
 const fetchImpl=async url=>{
  urls.push(String(url));
  if(url.hostname==='ai.example')return {ok:false,status:503,json:async()=>({error:{code:'provider_unavailable'}})};
  assert.equal(url.hostname,'catalog.example');
  return {ok:true,json:async()=>url.pathname.endsWith('/repos')?[repo]:{repo,integration_ideas:[]}};
 };
 const catalog=createCatalogHttp({baseUrl:'https://catalog.example/',fetchImpl});
 const assistant=createHttpAssistantProvider({baseUrl:'https://ai.example/',fetchImpl});
 const before=await catalog.list();
 await assert.rejects(assistant.ask({query:'Una aplicación para mi equipo'}),{code:'provider_unavailable'});
 const detail=await catalog.detail(repo.full_name,before.categories);
 assert.equal(detail.tool.full_name,repo.full_name);
 assert.deepEqual((await catalog.list()).tools,before.tools);
 assert.ok(urls.includes('https://ai.example/assistant'));
 assert.ok(urls.includes('https://catalog.example/repos/example/tool'));
});
