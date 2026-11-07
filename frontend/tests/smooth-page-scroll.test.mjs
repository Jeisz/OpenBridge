import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

function setup(){
 const listeners=new Map(),frames=new Map();let id=0;
 class Element{closest(){return null;}}
 const body=new Element();
 const context={Element,innerHeight:800,scrollY:0,getComputedStyle:()=>({overflowY:'visible'}),document:{body,documentElement:{scrollHeight:3000}},matchMedia:()=>({matches:false,addEventListener(){},removeEventListener(){}}),useEffect:fn=>fn(),requestAnimationFrame:fn=>{frames.set(++id,fn);return id;},cancelAnimationFrame:i=>frames.delete(i)};
 context.window={addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener(){},scrollTo:({top})=>{context.scrollY=top;listeners.get('scroll')?.();}};
 vm.runInNewContext(readFileSync(new URL('../src/useSmoothPageScroll.js',import.meta.url),'utf8').replace("import {useEffect} from 'react';",'').replace('export function','function')+'\nuseSmoothPageScroll(false);',context);
 return {context,frames,wheel(delta){let prevented=false;listeners.get('wheel')({target:body,deltaY:delta,deltaX:0,deltaMode:0,cancelable:true,preventDefault(){prevented=true;}});return prevented;},tick(now){const pending=[...frames.values()];frames.clear();pending.forEach(fn=>fn(now));}};
}
test('owns the gesture at the top so reversing downward stays smooth',()=>{
 const app=setup();
 assert.equal(app.wheel(-100),true,'outward wheel must not hand the gesture back to native scrolling');
 assert.equal(app.wheel(120),true);
 app.tick(16);
 assert.ok(app.context.scrollY>0&&app.context.scrollY<120);
 assert.ok(app.frames.size>0,'deceleration continues after the first frame');
});
test('reaches the top and smoothly reverses again',()=>{
 const app=setup();app.context.scrollY=100;
 app.wheel(-200);for(let i=1;i<80;i++)app.tick(i*16);
 assert.equal(app.context.scrollY,0);
 assert.equal(app.wheel(-20),true);
 app.wheel(100);app.tick(1300);
 assert.ok(app.context.scrollY>0&&app.context.scrollY<100);
});
