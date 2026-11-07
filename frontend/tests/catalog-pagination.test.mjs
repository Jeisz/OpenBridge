import test from 'node:test';
import assert from 'node:assert/strict';
import {paginateCatalog,pageNumbers} from '../src/features/catalog/pagination.mjs';
const items=Array.from({length:100},(_,id)=>({id}));
test('24 items per page without duplicates or omissions',()=>{
 const pages=Array.from({length:5},(_,i)=>paginateCatalog(items,i+1));
 assert.deepEqual(pages.map(p=>p.items.length),[24,24,24,24,4]);
 assert.deepEqual(pages.flatMap(p=>p.items),items);
});
test('filters reducing results clamp the page, including empty results',()=>{
 assert.equal(paginateCatalog(items.slice(0,9),5).page,1);
 assert.deepEqual(paginateCatalog([],5),{page:1,pages:1,items:[]});
});
test('large catalogs keep navigation compact and current page visible',()=>{
 assert.deepEqual(pageNumbers(50,100),[1,'gap-49',49,50,51,'gap-100',100]);
 assert.deepEqual(pageNumbers(1,2),[1,2]);
});
