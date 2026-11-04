import test from 'node:test';
import assert from 'node:assert/strict';
import {observeProposalHeight} from '../src/features/assistant/observeProposalHeight.mjs';

test('inner accordion frames follow directly; discrete tab changes retain the outer transition', () => {
 let height=400, animations=[], resize, disconnected=false;
 const listeners=new Map();
 const content={getBoundingClientRect:()=>({height}),getAnimations:()=>animations,
  addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:name=>listeners.delete(name)};
 const surface={style:{}};
 class Observer {constructor(fn){resize=fn;}observe(){}disconnect(){disconnected=true;}}
 const cleanup=observeProposalHeight(content,surface,Observer);
 assert.equal(surface.style.height,'400px');
 animations=[{transitionProperty:'grid-template-rows',playState:'running'}];
 for (const frame of [410.2,425.8,440]) {
  height=frame;resize();
  assert.equal(surface.style.height,`${Math.ceil(frame)}px`);
  assert.equal(surface.style.transitionProperty,'none');
 }
 animations=[];listeners.get('transitionend')();
 assert.equal(surface.style.transitionProperty,'');
 height=600;resize();
 assert.equal(surface.style.height,'600px');
 assert.equal(surface.style.transitionProperty,'');
 cleanup();assert.equal(disconnected,true);assert.equal(listeners.size,0);
});

test('cancelled disclosures and reduced-motion changes leave no disabled outer transition', () => {
 let animations=[{transitionProperty:'grid-template-rows',pending:true}];
 const listeners=new Map(),surface={style:{}};
 const content={getBoundingClientRect:()=>({height:200}),getAnimations:()=>animations,
  addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:name=>listeners.delete(name)};
 class Observer {observe(){}disconnect(){}}
 const cleanup=observeProposalHeight(content,surface,Observer);
 assert.equal(surface.style.transitionProperty,'none');
 animations=[];listeners.get('transitioncancel')();
 assert.equal(surface.style.transitionProperty,'');
 cleanup();
});
