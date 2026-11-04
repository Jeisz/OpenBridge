import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('../src/useCatalogBounce.js',import.meta.url),'utf8').replace(/import .*?;\n/,'').replace('export function','function');
function run(hz,tail){
 let now=0,id=0,offset=0,peak=0,queue=new Map(),events={};
 const shell={closest:()=>null,getBoundingClientRect:()=>({top:500+offset}),style:{setProperty:(_,v)=>{offset=parseFloat(v);peak=Math.max(peak,offset)},removeProperty:()=>{offset=0}},dataset:{},removeAttribute:()=>{}};
 const noop=()=>{};const window={scrollY:0,innerHeight:900,addEventListener:(k,v)=>events[k]=v,removeEventListener:noop};
 const context={performance:{now:()=>now},useEffect:fn=>fn(),window,document:{querySelector:()=>shell,hidden:false,addEventListener:noop,removeEventListener:noop},matchMedia:()=>({matches:true,addEventListener:noop,removeEventListener:noop}),requestAnimationFrame:fn=>{queue.set(++id,fn);return id},cancelAnimationFrame:i=>queue.delete(i)};
 vm.createContext(context);vm.runInContext(source+';useCatalogBounce(false);',context);
 events.wheel({deltaY:-100,deltaMode:0,target:{closest:()=>null}});
 let lastInput=0,lastVisible=0,settled=0;
 for(let i=0;i<hz*4;i++){
  now+=1000/hz;
  if(tail&&now<600){events.wheel({deltaY:-15*Math.exp(-now/250),deltaMode:0,target:{closest:()=>null}});lastInput=now;}
  const batch=[...queue.values()];queue.clear();batch.forEach(fn=>fn(now));
  if(Math.abs(offset)>.5)lastVisible=now;
  if(!queue.size&&!settled)settled=now;
  if(now>=800)return {hz,tail,peak:+peak.toFixed(2),lastInput:Math.round(lastInput),visibleUntil:Math.round(lastVisible),settled:Math.round(settled)};
 }
}

test('bounce settles promptly and does not stretch time at low frame rates',()=>{
 for(const hz of [60,30,15]){
  const result=run(hz,false);
  assert.ok(result.settled<=450,JSON.stringify(result));
  assert.ok(result.peak>0&&result.peak<=22);
 }
});
test('wheel inertia at the top does not prolong or restart the bounce',()=>{
 const baseline=run(60,false),tail=run(60,true);
 assert.equal(tail.settled,baseline.settled);
 assert.equal(tail.visibleUntil,baseline.visibleUntil);
});
