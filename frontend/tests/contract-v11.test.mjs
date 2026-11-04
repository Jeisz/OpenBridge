import test from 'node:test';
import assert from 'node:assert/strict';
import fixtures from '../src/mocks/assistant.fixtures.json' with {type:'json'};
import {validateAssistantResponse} from '../src/data/assistant.mjs';
import {resolveProposalConnections} from '../src/data/proposal.mjs';
import {createHttpAssistantProvider} from '../src/data/assistantHttp.mjs';

test('v1.1 rejects dangling/self connections and invalid fields before display',()=>{
 for(const mutate of [r=>r.connections=null,r=>r.connections[0].to_key='missing',r=>r.connections[0].to_key=r.connections[0].from_key,r=>r.connections[0].protocol=null,r=>r.title=' ',r=>r.components[0].role=' ',r=>r.generated_at='2026-10-24T12:00:00']){
  const r=structuredClone(fixtures.ok);mutate(r);assert.throws(()=>validateAssistantResponse(r),{code:'invalid_response'});
 }
 const r=structuredClone(fixtures.no_evidence);delete r.summary;assert.throws(()=>validateAssistantResponse(r),{code:'invalid_response'});
});
test('connections belong to response even with an unknown id; missing connections are optional',()=>{
 const raw={...fixtures.ok,id:'live-response',title:'  Mi stack  '};const result=validateAssistantResponse(raw);
 assert.equal(result.title,'Mi stack');assert.equal(raw.title,'  Mi stack  ');
 assert.match(resolveProposalConnections(result)[0].title,/Next.js → Keycloak · OIDC/);
 const {connections,...without}=raw;assert.deepEqual(validateAssistantResponse(without).connections,[]);
 assert.deepEqual(resolveProposalConnections(validateAssistantResponse(without)),[]);
});
test('HTTP transport sends one prompt, propagates signal, and sanitizes all v1.1 errors',async()=>{
 const signal=new AbortController().signal;
 const provider=createHttpAssistantProvider({baseUrl:'http://localhost:8001',fetchImpl:async(url,options)=>{
  assert.equal(String(url),'http://localhost:8001/assistant');assert.equal(options.method,'POST');assert.equal(options.signal,signal);assert.deepEqual(JSON.parse(options.body),{query:'Una API para varias organizaciones'});
  return {ok:true,json:async()=>fixtures.ok};
 }});
 assert.equal((await provider.ask({query:'Una API para varias organizaciones',history:['not sent']},{signal})).status,'ok');
 for(const [status,code] of [[422,'invalid_query'],[502,'invalid_response'],[503,'provider_unavailable'],[504,'timeout']]){
  const p=createHttpAssistantProvider({baseUrl:'http://localhost:8001',fetchImpl:async()=>({ok:false,status,json:async()=>({error:{code,message:'secret provider diagnostics'}})})});
  await assert.rejects(p.ask({query:'test'}),e=>e.code===code&&!e.message.includes('secret'));
 }
});
