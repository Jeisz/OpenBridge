import test from 'node:test';
import assert from 'node:assert/strict';
import {catalogCategories,populatedCategories,toTool} from '../src/data/catalog.mjs';
test('development uses the shared ID with a short presentation label',()=>{
 assert.equal(catalogCategories.find(c=>c.id==='dev-tools').name,'Desarrollo');
 assert.equal(catalogCategories.some(c=>c.id==='devtools'),false);
 assert.equal(toTool({full_name:'test/tool',github_id:1,categories:[{category_id:'dev-tools'}]}).category,'Desarrollo');
});
test('filters include secondary categories and omit empty and uncategorized entries',()=>{
 const tools=[{categories:[{id:'auth'},{id:'backend'}]},{categories:[]}];
 assert.deepEqual(populatedCategories(catalogCategories,tools).map(c=>c.id),['auth','backend']);
 assert.deepEqual(populatedCategories(catalogCategories,[]),[]);
});
