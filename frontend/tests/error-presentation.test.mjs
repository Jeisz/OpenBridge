import test from 'node:test';
import assert from 'node:assert/strict';
import {assistantErrors,getAssistantError,queryErrorCode} from '../src/errorPresentation.mjs';
import {createHttpAssistantProvider} from '../src/data/assistantHttp.mjs';
import {createCatalogHttp} from '../src/data/catalogHttp.mjs';
test('validation boundaries distinguish empty, short and long text',()=>{
 assert.equal(queryErrorCode('  '),'empty_query');assert.equal(queryErrorCode('a'.repeat(19)),'short_query');assert.equal(queryErrorCode('a'.repeat(20)),null);assert.equal(queryErrorCode('a'.repeat(2000)),null);assert.equal(queryErrorCode('a'.repeat(2001)),'long_query');
});
test('all errors have local copy and validation has no retry',()=>{
 assert.equal(Object.keys(assistantErrors).length,11);
 for(const [code,value] of Object.entries(assistantErrors)){assert.ok(value.title&&value.description);assert.equal(value.retry,!['empty_query','short_query','long_query','invalid_query'].includes(code));}
 assert.equal(getAssistantError('unknown'),assistantErrors.technical_error);
});
test('transport failure, invalid JSON and abort remain distinct',async()=>{
 const ask=fetchImpl=>createHttpAssistantProvider({baseUrl:'https://ai.example/',fetchImpl}).ask({query:'Una aplicación para usuarios'});
 await assert.rejects(ask(async()=>{throw new TypeError('secret');}),{code:'connection_error'});
 await assert.rejects(ask(async()=>({ok:true,json:async()=>{throw new SyntaxError();}})),{code:'invalid_response'});
 await assert.rejects(ask(async()=>{throw new DOMException('Cancelado','AbortError');}),{name:'AbortError'});
});
test('catalog preserves HTTP status for missing detail',async()=>{
 const client=createCatalogHttp({baseUrl:'https://catalog.example/',fetchImpl:async()=>({ok:false,status:404})});
 await assert.rejects(client.detail('owner/repo',[]),{status:404});
});

 test('normal requests warn only after sixty seconds and time out later',async()=>{
 const {assistantRequestTiming}=await import('../src/data/assistantRequest.mjs');
 const {assistantScenarioOptions}=await import('../src/mocks/assistant-scenarios.mjs');
 assert.equal(assistantRequestTiming.slowMs,60000);assert.equal(assistantRequestTiming.timeoutMs,90000);
 for(const scenario of ['ok','slow','timeout'])assert.equal(assistantScenarioOptions(scenario,[]).slowMs,60000);
 });
