import test from 'node:test';
import assert from 'node:assert/strict';
import {createSessionPaletteResolver,fallbackPalettes} from '../src/sessionPalette.mjs';
import {resolveBrand,brandRegistry} from '../src/brandIdentity.js';
test('ten palettes persist per repository across remounts and reloads',()=>{
 const values=new Map(),storage=()=>({getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v)});
 const pick=createSessionPaletteResolver({storage,random:()=>0.3});
 const first=pick('owner/tool');assert.equal(pick('owner/tool'),first);
 assert.deepEqual(createSessionPaletteResolver({storage,random:()=>0.9})('owner/tool'),first);
 assert.notEqual(createSessionPaletteResolver({random:()=>0.9})('owner/tool').id,first.id);
 assert.equal(fallbackPalettes.length,10);
});
test('blocked storage keeps an in-memory session identity',()=>{
 let n=0;const pick=createSessionPaletteResolver({storage:()=>{throw Error('blocked');},random:()=>++n/10});
 assert.equal(pick('a/tool'),pick('a/tool'));assert.notEqual(pick('a/tool'),pick('b/tool'));
});
test('brand palette wins even with missing artwork; unknown repos share fallback across views',()=>{
 const pick=createSessionPaletteResolver({random:()=>0.5});
 const tool={name:'API',id:'1',full_name:'unknown/tool'};
 assert.deepEqual(resolveBrand(tool,{},new Set(),pick).palette,resolveBrand({...tool,id:'2',full_name:' Unknown/Tool '},{},new Set(),pick).palette);
 const known={name:'Lago',full_name:'getlago/lago'};
 const identity=resolveBrand(known,brandRegistry,new Set([brandRegistry[known.full_name].logo]),pick);
 assert.deepEqual(identity.palette,brandRegistry[known.full_name].palette);assert.equal(identity.logo,null);
});
test('all fallback backgrounds and tags support white text at 4.5:1',()=>{
 const luminance=hex=>{const c=hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722;};
 for(const p of fallbackPalettes)for(const key of ['start','end','tag'])assert.ok(1.05/(luminance(p[key])+.05)>=4.5,`${p.id} ${key}`);
});
