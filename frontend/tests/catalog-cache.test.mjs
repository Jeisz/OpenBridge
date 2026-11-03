import test from 'node:test';
import assert from 'node:assert/strict';
import {createCatalogCache} from '../src/data/catalogCache.mjs';

test('fresh catalog and details are reused; stale data stays available during refresh',async()=>{
 let time=0,calls=0;const cache=createCatalogCache({list:async()=>({version:++calls}),detail:async name=>({name,version:++calls})},{now:()=>time});
 const first=await cache.list();assert.equal(await cache.list(),first);assert.equal(calls,1);
 const detail=await cache.detail('a/b',[]);assert.equal(await cache.detail('a/b',[]),detail);
 time=120001;assert.equal(cache.peekList(),first);await cache.list();assert.equal(calls,3);
});
test('concurrent loads share a request; cancelling one consumer does not cancel another',async()=>{
 let done,calls=0;const cache=createCatalogCache({list:()=>{calls++;return new Promise(resolve=>done=resolve);}});
 const controller=new AbortController();const a=cache.list(controller.signal),b=cache.list();
 controller.abort();await assert.rejects(a,{name:'AbortError'});done({tools:[]});await b;assert.equal(calls,1);
});
test('failed refresh keeps cached content and can be retried',async()=>{
 let fail=false;const cache=createCatalogCache({list:async()=>{if(fail)throw Error('offline');return {tools:[1]};}});
 const initial=await cache.list();fail=true;await assert.rejects(cache.list(undefined,{force:true}));assert.equal(cache.peekList(),initial);
 fail=false;await cache.list(undefined,{force:true});
});
test('forced refresh shares pending work and cannot race a newer response',async()=>{
 let done,calls=0;const cache=createCatalogCache({list:()=>{calls++;return new Promise(resolve=>done=resolve);}});
 const a=cache.list(),b=cache.list(undefined,{force:true});await Promise.resolve();done({version:1});
 assert.equal(await a,await b);assert.equal(calls,1);assert.deepEqual(cache.peekList(),{version:1});
});
test('detail cache isolates repositories and category mappings',async()=>{
 let calls=0;const cache=createCatalogCache({detail:async()=>++calls});
 await cache.detail('a/b',[]);await cache.detail('a/c',[]);await cache.detail('a/b',[{id:'x',name:'X'}]);assert.equal(calls,3);
});
