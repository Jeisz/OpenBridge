// Session-memory cache: no credentials or API records are persisted in storage.
export function createCatalogCache(client,{ttl=120_000,now=Date.now}={}){
 const entries=new Map(),pending=new Map();
 const detailKey=(name,categories)=>JSON.stringify(['detail',name,categories]);
 function read(key){return entries.get(key)?.value;}
 function consume(promise,signal){
  if(!signal)return promise;
  signal.throwIfAborted();
  return new Promise((resolve,reject)=>{
   const abort=()=>reject(signal.reason??new DOMException('Aborted','AbortError'));
   signal.addEventListener('abort',abort,{once:true});
   promise.then(value=>{if(!signal.aborted)resolve(value);},error=>{if(!signal.aborted)reject(error);}).finally(()=>signal.removeEventListener('abort',abort));
  });
 }
 function load(key,fetcher,signal,force){
  signal?.throwIfAborted();
  const cached=entries.get(key);
  if(!force&&cached&&now()-cached.at<ttl)return Promise.resolve(cached.value);
  if(!pending.has(key)){
   // Consumers cancel independently; a shared request may finish into cache.
   const request=Promise.resolve().then(fetcher).then(value=>{
    entries.delete(key);entries.set(key,{value,at:now()});
    if(entries.size>100)entries.delete(entries.keys().next().value);
    return value;
   }).finally(()=>pending.delete(key));
   pending.set(key,request);
  }
  return consume(pending.get(key),signal);
 }
 return {
  peekList:()=>read('list'),
  peekDetail:(name,categories)=>read(detailKey(name,categories)),
  list:(signal,{force=false}={})=>load('list',()=>client.list(),signal,force),
  detail:(name,categories,signal,{force=false}={})=>load(detailKey(name,categories),()=>client.detail(name,categories),signal,force),
 };
}
