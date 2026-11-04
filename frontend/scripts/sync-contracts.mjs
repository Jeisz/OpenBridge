import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url));
// Stable preview uses a snapshot of the same contract, never an edited copy.
const snapshot=path.join(root,'categories.contract.json');
const source=existsSync(snapshot)?snapshot:path.resolve(root,'../shared/contracts/categories.json');
const bytes=readFileSync(source),data=JSON.parse(bytes);
if(!Array.isArray(data.categories)||new Set(data.categories.map(c=>c.id)).size!==data.categories.length||!data.categories.every(c=>/^[a-z][a-z0-9-]*$/.test(c.id)&&typeof c.name==='string'&&typeof c.description==='string'))throw new Error('Contrato de categorías inválido');
mkdirSync(path.join(root,'src/generated'),{recursive:true});
writeFileSync(path.join(root,'src/generated/categories.json'),bytes);
