import test from 'node:test';
import assert from 'node:assert/strict';
import {requestAssistant} from '../src/data/assistantRequest.mjs';
import {AssistantError,mockAssistant,validateAssistantResponse,validateAssistantCatalog} from '../src/data/assistant.mjs';
import {catalogRecords} from '../src/data/catalog.mjs';
import {resolveProposalExample} from '../src/data/proposal.mjs';
import {assistantScenarioOptions} from '../src/mocks/assistant-scenarios.mjs';
const request={query:'Una plataforma de reservas para un estudio de yoga'};
const valid=()=>mockAssistant.ask(request,{delay:0});
const quick={slowMs:100,timeoutMs:500,delay:0};

test('request boundary sends only query and validates the whole response',async()=>{
 const response=await valid();let received;
 const result=await requestAssistant({...request,history:['not sent']},{...quick,provider:{ask:async(payload)=>{received=payload;return response;}}});
 assert.deepEqual(received,request);assert.equal(result.status,'ok');
 const invalid={...response,components:'invalid'};
 await assert.rejects(requestAssistant(request,{...quick,provider:{ask:async()=>invalid}}),{name:'AssistantError',code:'invalid_response'});
});

test('malformed nested fields produce controlled validation errors, never incidental crashes',async()=>{
 const base=await valid();
 const mutations=[r=>r.id=' ',r=>r.generated_at=123,r=>r.generated_at='not-a-date',r=>r.components=[null],r=>r.components[0].label=' ',r=>r.components[0].rationale=[],r=>r.components[0].full_name='missing-owner',r=>r.assumptions=[3],r=>r.clarification_questions=null,r=>r.summary=' '];
 for(const mutate of mutations){const response=structuredClone(base);mutate(response);assert.throws(()=>validateAssistantResponse(response),e=>e instanceof AssistantError&&e.code==='invalid_response');}
 for(const response of [null,[],true,'unexpected'])assert.throws(()=>validateAssistantResponse(response),{name:'AssistantError'});
 assert.throws(()=>validateAssistantResponse({id:'empty-optional-text',status:'no_evidence',title:' ',summary:' ',generated_at:base.generated_at}),{code:'invalid_response'});
});

test('deadline aborts transport and rejects even a provider that ignores cancellation',async()=>{
 let providerSignal;
 await assert.rejects(requestAssistant(request,{slowMs:1,timeoutMs:5,provider:{ask:async(_,options)=>{providerSignal=options.signal;return new Promise(()=>{});}}}),{name:'AssistantError',code:'timeout'});
 assert.equal(providerSignal.aborted,true);
});

test('slow feedback occurs during wait and is cleaned up after completion',async()=>{
 const response=await valid();let slow=0;
 const result=await requestAssistant(request,{slowMs:1,timeoutMs:500,onSlow:()=>slow++,provider:{ask:()=>new Promise(resolve=>setTimeout(()=>resolve(response),15))}});
 assert.equal(result.status,'ok');assert.equal(slow,1);
 slow=0;await requestAssistant(request,{...quick,slowMs:5,onSlow:()=>slow++});await new Promise(resolve=>setTimeout(resolve,12));assert.equal(slow,0);
});

test('external cancellation wins over a late success and cleans slow feedback',async()=>{
 const response=await valid();const controller=new AbortController();let release,slow=0;
 const pending=requestAssistant(request,{signal:controller.signal,slowMs:5,timeoutMs:500,onSlow:()=>slow++,provider:{ask:()=>new Promise(resolve=>{release=resolve;})}});
 await Promise.resolve();controller.abort();release(response);
 await assert.rejects(pending,{name:'AbortError'});await new Promise(resolve=>setTimeout(resolve,12));assert.equal(slow,0);
 const already=new AbortController();already.abort();await assert.rejects(requestAssistant(request,{signal:already.signal}),{name:'AbortError'});
});

test('unknown, archived or disabled repositories never enter the accepted proposal',async()=>{
 const response=await valid();
 for(const flag of ['archived','disabled']){
  const catalog=structuredClone(catalogRecords);catalog.find(t=>t.full_name==='keycloak/keycloak')[flag]=true;
  assert.throws(()=>validateAssistantCatalog(response,catalog),{code:'unavailable_tool'});
 }
 await assert.rejects(requestAssistant(request,{...quick,scenario:'unknown_tool'}),{code:'unavailable_tool'});
 await assert.rejects(requestAssistant(request,{...assistantScenarioOptions('archived_tool',catalogRecords),...quick}),{code:'unavailable_tool'});
 assert.equal(catalogRecords.find(t=>t.full_name==='keycloak/keycloak').archived,false);
 const appPart=structuredClone(response);appPart.components[0].full_name=null;assert.equal(validateAssistantCatalog(appPart,catalogRecords),appPart);
});

test('retry can recover with the same prompt; clarification is another independent request',async()=>{
 await assert.rejects(requestAssistant(request,{...quick,scenario:'error_once',attempt:1}),{code:'technical_error'});
 assert.equal((await requestAssistant(request,{...quick,scenario:'error_once',attempt:2})).status,'ok');
 const question=await requestAssistant(request,{...quick,scenario:'clarification_then_ok',attempt:1});assert.equal(question.status,'needs_clarification');
 assert.equal((await requestAssistant({...request,query:request.query+'. Tendrá alumnos y profesores, y se alojará en infraestructura propia.'},{...quick,scenario:'clarification_then_ok',attempt:2})).status,'ok');
});

test('one tool, six tools, long content and missing integrations remain usable',async()=>{
 for(const scenario of ['one_tool','ok_extended','long_content','without_integrations']){
  const response=await requestAssistant(request,{...quick,scenario});
  assert.ok(response.components.length>=1&&response.components.length<=6);
  if(scenario==='one_tool')assert.equal(response.components.length,1);
  if(scenario==='long_content'){assert.equal(response.components.length,6);assert.ok(response.components[0].label.length>80);assert.ok(response.components[0].rationale.length>500);}
  if(scenario!=='ok_extended')assert.equal(resolveProposalExample(response),null);
 }
});

test('unexpected provider aborts/errors become recoverable failures instead of stuck loading',async()=>{
 for(const error of [new DOMException('provider aborted','AbortError'),new Error('internal details')]){
  await assert.rejects(requestAssistant(request,{...quick,provider:{ask:async()=>{throw error;}}}),e=>e.code==='technical_error'&&!e.message.includes('internal details'));
 }
});

test('unverified SPDX licenses cannot be recommended, including adapted records',async()=>{
 const response=await valid();const catalog=structuredClone(catalogRecords);
 catalog.find(t=>t.full_name==='postgres/postgres').license_spdx_id='NOASSERTION';
 assert.throws(()=>validateAssistantCatalog(response,catalog),{code:'unverified_license'});
 assert.equal(validateAssistantCatalog(response,catalogRecords),response);
});
