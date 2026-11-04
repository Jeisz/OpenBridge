import test from 'node:test';
import assert from 'node:assert/strict';
import {fitDescription} from '../src/features/catalog/fitDescription.mjs';
test('keeps short copy intact without a continuation',()=>{
 assert.deepEqual(fitDescription('Texto breve',(text,more)=>text.length+(more?10:0)<=30),{text:'Texto breve',clipped:false});
});
test('reserves room for inline continuation within the available lines',()=>{
 const fits=(text,more)=>Array.from(text).length+(more?10:0)<=60;
 const result=fitDescription('Una descripción extensa con palabras y acentos que necesita truncarse dentro de tres líneas.',fits);
 assert.equal(result.clipped,true);assert.ok(fits(result.text,true));assert.ok(result.text.length>30);
});
