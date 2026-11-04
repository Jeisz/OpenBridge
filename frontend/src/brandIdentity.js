import {useSyncExternalStore} from 'react';
import brandIdentities from './data/brand-identities.json' with {type:'json'};

import {sessionPalette} from './sessionPalette.mjs';

export const defaultBrand=brandIdentities.fallback;
export const brandRegistry=brandIdentities.identities;
export function brandKey(fullName){return typeof fullName==='string'?fullName.trim().toLowerCase():'';}
const failed=new Set(),listeners=new Set();
const subscribe=listener=>{listeners.add(listener);return()=>listeners.delete(listener);};
const snapshot=()=>failed.size;
export function markBrandFailed(url){if(!url||failed.has(url))return;failed.add(url);listeners.forEach(listener=>listener());}
export function brandInitials(name){const words=name.trim().split(/\s+/u).filter(Boolean);return words.slice(0,2).map(word=>Array.from(word)[0]).join('').toLocaleUpperCase('es');}
export function resolveBrand(tool,identities=brandRegistry,errors=failed,paletteFor=()=>null){
 const asset=identities[brandKey(tool.full_name)]||{},fallback=!asset.logo||errors.has(asset.logo);
 const watermark=asset.watermark||asset.logo;
 return {logo:fallback?null:asset.logo,watermark:fallback||errors.has('watermark:'+watermark)?null:watermark,
  fallback,initials:brandInitials(tool.name),wordmark:!fallback&&!!asset.wordmark,
  palette:asset.palette||paletteFor(brandKey(tool.full_name)||String(tool.id||''))||defaultBrand};
}
const clientSnapshot=()=>true,serverSnapshot=()=>false;
export function useBrandIdentity(tool){
 useSyncExternalStore(subscribe,snapshot,snapshot);
 const client=useSyncExternalStore(subscribe,clientSnapshot,serverSnapshot);
 return resolveBrand(tool,brandRegistry,failed,client?sessionPalette:undefined);
}
