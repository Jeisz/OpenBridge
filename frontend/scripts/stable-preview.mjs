import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, statSync, renameSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync, spawn } from 'node:child_process';

// Keep runtime dependencies and compiled assets outside cloud-managed Documents.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const key = createHash('sha256').update(root).digest('hex').slice(0, 12);
const runtime = path.join(tmpdir(), `openbridge-preview-${key}`);
mkdirSync(runtime, { recursive: true });
function copyTree(source, destination) {
  if (statSync(source).isDirectory()) {
    mkdirSync(destination, { recursive: true });
    for (const name of readdirSync(source)) copyTree(path.join(source, name), path.join(destination, name));
  } else {
    let bytes;
    // Cloud-backed files can hydrate between reads. Retry without publishing
    // partial content, while retaining all existing validation guards.
    for(let attempt=0;attempt<5;attempt++){
      const first=readFileSync(source);
      const second=readFileSync(source);
      const validSvg=!source.endsWith('.svg')||first.toString('utf8').trimEnd().endsWith('</svg>');
      if(first.length&&validSvg&&first.equals(second)){bytes=first;break;}
      if(attempt<4)Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,250);
    }
    if(!bytes)throw new Error(`Lectura inestable o incompleta: ${source}. Se conserva la compilación anterior.`);
    writeFileSync(destination, bytes);
  }
}
for (const name of ['package.json', 'package-lock.json', 'next.config.mjs', 'postcss.config.mjs', '.openai', 'worker', 'scripts', 'src', 'public']) {
  copyTree(path.join(root, name), path.join(runtime, name));
}
copyTree(path.join(root, '../shared/contracts/categories.json'), path.join(runtime, 'categories.contract.json'));
function run(command, args) {
  const result = spawnSync(command, args, { cwd: runtime, stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status || 1);
}
const lockHash = createHash('sha256').update(readFileSync(path.join(runtime, 'package-lock.json'))).digest('hex');
const stamp = path.join(runtime, '.installed-lock');
if (!existsSync(stamp) || readFileSync(stamp, 'utf8') !== lockHash || !existsSync(path.join(runtime, 'node_modules/next/dist/bin/next'))) {
  run('npm', ['ci', '--no-audit', '--no-fund']);
  writeFileSync(stamp, lockHash);
}
run('npm', ['run', 'build']);
const published = path.join(runtime, 'published');
const previous = path.join(runtime, 'previous');
rmSync(previous, { recursive: true, force: true });
if (existsSync(published)) renameSync(published, previous);
renameSync(path.join(runtime, 'dist/client'), published);
console.log(`Vista previa compilada: ${runtime}`);
if (process.argv.includes('--build-only')) process.exit(0);
const server = spawn(process.execPath, [path.join(runtime,'scripts/serve-preview.mjs'),published], {cwd:runtime,stdio:'inherit'});
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.kill(signal));
server.on('exit', code => process.exit(code || 0));
