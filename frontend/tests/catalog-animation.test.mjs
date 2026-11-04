import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

// Exercise the actual transition hook with two repositories sharing a name.
function transition(reduced=false){
 const effects=[],timers=[];
 const cards=['owner-a/cli','owner-b/cli'].map(id=>({
  dataset:{toolId:id},style:{setProperty(){}},inert:false,
  getAttribute:()=> 'cli',getBoundingClientRect:()=>({top:100,bottom:400,left:0}),getAnimations:()=>[]
 }));
 let committed;
 const grid={children:cards,dataset:{}};
 const context={useRef:value=>({current:value}),useState:value=>[value,next=>{committed=next;}],useLayoutEffect:fn=>effects.push(fn),
  document:{querySelector:()=>grid,querySelectorAll:()=>[]},matchMedia:()=>({matches:reduced,addEventListener(){},removeEventListener(){}}),
  getComputedStyle:()=>({gridTemplateColumns:'300px 300px 300px'}),innerHeight:800,
  setTimeout:fn=>{timers.push(fn);return 1;},clearTimeout(){}};
 vm.createContext(context);
 const source=readFileSync(new URL('../src/useAnimatedCatalog.js',import.meta.url),'utf8').replace(/^import .*\n/,'').replace('export function','function');
 vm.runInContext(source+'\nthis.run=useAnimatedCatalog;',context);
 const tools=[{id:'owner-b/cli',name:'cli'}];
 context.run(tools);effects[0]();
 return {cards,timers,tools,get committed(){return committed;}};
}
test('filtering one of two identically named repos exits only the removed identity',()=>{
 const result=transition();
 assert.equal(result.cards[0].dataset.exiting,'true');
 assert.equal(result.cards[1].dataset.exiting,undefined);
 result.timers.forEach(fn=>fn());
 assert.equal(result.committed,result.tools);
});
test('reduced motion commits the filtered identities without waiting',()=>{
 const result=transition(true);
 assert.equal(result.committed,result.tools);
 assert.equal(result.timers.length,0);
});
