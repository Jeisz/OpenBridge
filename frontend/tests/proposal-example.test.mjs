import test from 'node:test';
import assert from 'node:assert/strict';
import {mockAssistant} from '../src/data/assistant.mjs';
import {resolveProposalExample} from '../src/data/proposal.mjs';

test('integration guidance only belongs to its exact demo tools and response',async()=>{
 for(const scenario of ['ok','ok_extended']){
  const response=await mockAssistant.ask({query:'Una plataforma de reservas de clases'},{scenario,delay:0});
  const example=resolveProposalExample(response);
  assert.equal(example.layers.length,response.components.length);
  assert.equal(resolveProposalExample({...response,id:'actual-response'}),null);
  const changed=structuredClone(response);changed.components[0].full_name='different/tool';assert.equal(resolveProposalExample(changed),null);
  example.layers[0].label='changed';assert.notEqual(resolveProposalExample(response).layers[0].label,'changed');
 }
 assert.equal(resolveProposalExample(null),null);
 for(const scenario of ['needs_clarification','no_evidence'])assert.equal(resolveProposalExample(await mockAssistant.ask({query:'Una plataforma de reservas de clases'},{scenario,delay:0})),null);
});
