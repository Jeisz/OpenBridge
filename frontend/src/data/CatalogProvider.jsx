import {errorPreview,sixToolPreview} from '../mocks/errorPreview.mjs';
import {createContext,useContext,useEffect,useMemo,useState} from 'react';
import {tools as mockTools} from '../tools';
import {profiles as mockProfiles} from '../toolProfiles';
import {catalogCategories} from './catalog.mjs';
import {createCatalogCache} from './catalogCache.mjs';
import {createCatalogHttp} from './catalogHttp.mjs';

const baseUrl=process.env.NEXT_PUBLIC_CATALOG_API_BASE_URL||process.env.NEXT_PUBLIC_API_BASE_URL||'';
const http=baseUrl&&!sixToolPreview()?createCatalogCache(createCatalogHttp({baseUrl})):null;
const initial={tools:http?[]:mockTools,profiles:http?{}:mockProfiles,categories:catalogCategories,status:http?'loading':'ready',error:null};
const Context=createContext({...initial,http,baseUrl});
export function CatalogProvider({children}){
 const [data,setData]=useState(()=>http?.peekList()?{...http.peekList(),status:'ready',error:null}:initial),[attempt,setAttempt]=useState(0);
 useEffect(()=>{
  if(errorPreview('license')){setData({tools:mockTools.map(tool=>tool.full_name==='keycloak/keycloak'?{...tool,license_spdx_id:'NOASSERTION'}:tool),profiles:mockProfiles,categories:catalogCategories,status:'ready',error:null});return;}
  if(errorPreview('catalog')){setData(d=>({...d,status:'error',tools:[]}));return;}
  if(!http)return;
  const controller=new AbortController();
  setData(d=>({...d,status:d.status==='ready'||d.tools.length?'ready':'loading',error:null}));
  const refresh=(force=false)=>http.list(controller.signal,{force}).then(result=>{if(!controller.signal.aborted)setData({...result,status:'ready'});}).catch(error=>{if(!controller.signal.aborted)setData(d=>({...d,status:'error',error:{status:error.status??null,code:error.code??null}}));});
  refresh(attempt>0);
  const revisit=()=>{if(!document.hidden)refresh();};
  window.addEventListener('focus',revisit);
  document.addEventListener('visibilitychange',revisit);
  return()=>{controller.abort();window.removeEventListener('focus',revisit);document.removeEventListener('visibilitychange',revisit);};
 },[attempt]);
 const value=useMemo(()=>({...data,http,baseUrl,retry:()=>setAttempt(n=>n+1)}),[data]);
 return <Context.Provider value={value}>{children}</Context.Provider>;
}
export const useCatalogData=()=>useContext(Context);
