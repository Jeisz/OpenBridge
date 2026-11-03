import test from 'node:test';
import assert from 'node:assert/strict';
import {filterCatalog} from '../src/features/catalog/filterCatalog.mjs';
const tools=[
 {id:'a',name:'Analítica',description:'Métricas',categories:[{name:'Analítica'},{name:'Backend'}],language:'Python',license:'MIT',stars:20000,dataSource:'github_snapshot',archived:false,disabled:false},
 {id:'b',name:'Motor',description:'Busqueda',category:'Búsqueda',language:'Rust',license:'Apache-2.0',stars:50000,dataSource:'github_snapshot',archived:true,disabled:false},
];
test('catalog search ignores accents/case and matches descriptions',()=>{
 assert.deepEqual(filterCatalog(tools,{search:'ANALITICA'}).map(t=>t.id),['a']);
 assert.deepEqual(filterCatalog(tools,{search:'metricas'}).map(t=>t.id),['a']);
});
test('catalog combines filters and includes secondary category assignments',()=>{
 assert.deepEqual(filterCatalog(tools,{category:'Backend',language:'Python',license:'MIT',stars:'20000',maintenance:'active'}).map(t=>t.id),['a']);
 assert.equal(filterCatalog(tools,{language:'Rust',license:'MIT'}).length,0);
 assert.deepEqual(filterCatalog(tools,{maintenance:'archived'}).map(t=>t.id),['b']);
 assert.deepEqual(filterCatalog(tools),tools);
});

test('repository states distinguish archived, disabled and both',()=>{
 const base={name:'Tool',description:'',stars:0,dataSource:'api',archived:false,disabled:false};
 const records=[{...base,id:'normal'},{...base,id:'archived',archived:true},{...base,id:'disabled',disabled:true},{...base,id:'both',archived:true,disabled:true}];
 const ids=state=>filterCatalog(records,{maintenance:state}).map(t=>t.id);
 assert.deepEqual(ids('archived'),['archived','both']);
 assert.deepEqual(ids('disabled'),['disabled','both']);
 assert.deepEqual(ids('active'),['normal']);
 assert.equal(ids('').length,4);
});
