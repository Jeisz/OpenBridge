"use client";
import {useTypingProbe} from './debug/useTypingProbe';
import {App} from './App';
import {CatalogProvider} from './data/CatalogProvider';
// Keep the existing browser-only animation boot and hash routes intact.
if(typeof window!=='undefined'){
 window.history.scrollRestoration='manual';
 if(!location.hash.startsWith('#herramienta/'))history.replaceState(history.state,'',`${location.pathname}${location.search}#asistente`);
 window.scrollTo({top:0,left:0,behavior:'instant'});
}
export default function ClientApp(){useTypingProbe();return <div id="root" data-reveal-boot=""><CatalogProvider><App/></CatalogProvider></div>;}
