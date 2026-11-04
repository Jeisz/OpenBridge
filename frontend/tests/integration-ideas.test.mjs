import test from 'node:test';
import assert from 'node:assert/strict';
import {integrationIdeaRecords,toIntegrationIdea,integrationIdeasForTool,pendingIntegrationIdeas} from '../src/data/integrationIdeas.mjs';
import {catalogRecords,catalogRepos,toTool,toolCategoryNames} from '../src/data/catalog.mjs';

test('integration fixtures match the proposed shape and refer to catalog tools',()=>{
 assert.equal(integrationIdeaRecords.length,18);
 assert.equal(new Set(integrationIdeaRecords.map(i=>i.id)).size,18);
 for(const idea of integrationIdeaRecords){
  assert.ok(catalogRecords.some(tool=>tool.full_name===idea.full_name));
  assert.ok(['rest_api','docker','sdk','webhook'].includes(idea.integration_type));
  assert.ok(['low','medium','high'].includes(idea.difficulty));
  assert.ok(idea.title.length<=120&&idea.summary.length<=300);
  assert.ok(idea.compatible_stack.length>0);for(const text of idea.compatible_stack)assert.ok(text.trim()===text&&text.length>0&&Array.from(text).length<=40);for(const text of idea.dependencies)assert.ok(text.trim()===text&&text.length>0&&Array.from(text).length<=80);assert.ok(Array.isArray(idea.dependencies)&&Array.isArray(idea.triggers));
  assert.ok(new URL(idea.docs_url));assert.equal(idea.generated_by,'human');assert.equal(idea.reviewed_at,null);
  if(idea.snippet)assert.ok(idea.snippet_language&&idea.docs_url.includes('keycloak.org/securing-apps/'));else assert.equal(idea.snippet_language,null);
 }
});
test('adapter preserves lists, optional snippets and honest review labels',()=>{
 const raw=integrationIdeaRecords.find(idea=>!idea.snippet);const draft=toIntegrationIdea(raw);
 assert.deepEqual(draft.stack,raw.compatible_stack);assert.equal(draft.snippet,null);assert.match(draft.reviewLabel,/Borrador editorial/);
 const ai=toIntegrationIdea({...raw,generated_by:'llm',snippet:'console.log(1)',snippet_language:'javascript'});
 assert.match(ai.reviewLabel,/Sugerida por IA/);assert.equal(ai.snippetLanguage,'javascript');
 assert.equal(toIntegrationIdea({...raw,reviewed_at:'2026-10-22T12:00:00Z'}).reviewLabel,'Revisada');
});
test('pending types stay out of active ideas and archived tools have none',()=>{
 assert.equal(Object.values(pendingIntegrationIdeas).flat().length,0);
 const tool=catalogRecords.find(t=>t.full_name==='keycloak/keycloak');
 assert.equal(integrationIdeasForTool(tool).length,2);assert.deepEqual(integrationIdeasForTool({...tool,archived:true}),[]);
 assert.deepEqual(integrationIdeasForTool({full_name:'missing/repo'}),[]);
});
test('push label is based on pushed_at and filters can use secondary categories',()=>{
 const raw={...catalogRepos[0],pushed_at:'2026-10-22T12:00:00Z',categories:[{category_id:'auth',assigned_by:'human'},{category_id:'database',assigned_by:'rule'}]};
 const tool=toTool(raw,{lastCommitAt:'2025-01-01T12:00:00Z'});
 assert.match(tool.activity,/22.*oct.*2026/);assert.deepEqual(toolCategoryNames(tool),['Autenticación','Bases de datos']);
});
