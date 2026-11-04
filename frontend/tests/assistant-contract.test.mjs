import test from 'node:test';
import assert from 'node:assert/strict';
import {mockAssistant,validateAssistantQuery,validateAssistantResponse,resolveComponentTool} from '../src/data/assistant.mjs';
import {catalogRecords} from '../src/data/catalog.mjs';

test('query follows the 20–2000 character request contract',()=>{
 for(const query of ['', ' '.repeat(30),'x'.repeat(19),'x'.repeat(2001)])assert.ok(validateAssistantQuery(query));
 for(const query of ['x'.repeat(20),'x'.repeat(2000),'á'.repeat(20),'🧩'.repeat(20)])assert.equal(validateAssistantQuery(query),'');
});
test('all three response mocks validate and catalog references resolve',async()=>{
 for(const scenario of ['ok','needs_clarification','no_evidence']){
  const response=await mockAssistant.ask({query:'Una plataforma de reservas de clases'},{scenario,delay:0});
  assert.equal(response.status,scenario);assert.ok(response.generated_at);
  for(const component of response.components)if(component.full_name)assert.ok(resolveComponentTool(component,catalogRecords));else assert.equal(resolveComponentTool(component,catalogRecords),null);
 }
});
test('malformed component responses are rejected without introducing a technical status',async()=>{
 const response=await mockAssistant.ask({query:'Una plataforma de reservas de clases'},{delay:0});
 for(const mutate of [r=>r.components.push(r.components[0]),r=>r.components=[],r=>r.status='error']){
  const bad=structuredClone(response);mutate(bad);assert.throws(()=>validateAssistantResponse(bad));
 }
 const questions=structuredClone(response);questions.status='needs_clarification';questions.clarification_questions=[];assert.throws(()=>validateAssistantResponse(questions));
 assert.equal(resolveComponentTool({full_name:'unknown/repo'},catalogRecords),null);
});
test('default lists, isolated responses, cancellation and technical errors',async()=>{
 const minimal=validateAssistantResponse({id:'minimal',status:'no_evidence',summary:'No hay evidencia en el catálogo.',generated_at:'2026-10-20T12:00:00Z'});assert.deepEqual(minimal.components,[]);
 const request={query:'Una plataforma de reservas de clases'};
 const first=await mockAssistant.ask(request,{delay:0});const snapshot=structuredClone(first);first.components[0].label='changed';
 const second=await mockAssistant.ask(request,{delay:0});assert.deepEqual(second,snapshot);
 await assert.rejects(mockAssistant.ask(request,{scenario:'error',delay:0}));
 const controller=new AbortController();const pending=mockAssistant.ask(request,{signal:controller.signal,delay:1000});controller.abort();await assert.rejects(pending,{name:'AbortError'});
});

test('all recommended components remain available, with optional catalog links',async()=>{
 const response=await mockAssistant.ask({query:'Una plataforma de reservas de clases'},{delay:0});
 assert.equal(response.connections.length,5);
 assert.deepEqual(response.components.map(c=>c.label),['Keycloak','Next.js','FastAPI','PostgreSQL','Valkey','Prometheus']);
 assert.equal(response.components.filter(c=>resolveComponentTool(c,catalogRecords)).length,6);
 assert.equal(response.components.filter(c=>c.full_name===null).length,0);
});

test('extended layout scenario respects six-component limit and resolves every tool',async()=>{
 const response=await mockAssistant.ask({query:'Una plataforma de reservas de clases'},{scenario:'ok_extended',delay:0});
 assert.equal(response.status,'ok');assert.equal(response.components.length,6);
 assert.ok(response.components.every(c=>resolveComponentTool(c,catalogRecords)));
 const tooMany=structuredClone(response);tooMany.components.push({...tooMany.components[0],key:'c7'});assert.throws(()=>validateAssistantResponse(tooMany));
});

test('query limits count Unicode code points, including astral characters',()=>{
 assert.equal(validateAssistantQuery('😀'.repeat(2000)),'');
 assert.notEqual(validateAssistantQuery('😀'.repeat(2001)),'');
});
