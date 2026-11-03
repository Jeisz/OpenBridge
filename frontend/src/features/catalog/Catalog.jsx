import {interfaceErrors,errorActions} from '../../errorPresentation.mjs';
import React,{memo} from 'react';
import {useCatalogData} from '../../data/CatalogProvider';
import {Search} from 'lucide-react';
import {RevealHeading,usePageReveal} from '../../PageReveal';
import {useAnimatedCatalog} from '../../useAnimatedCatalog';
import {CatalogSkeleton} from './CatalogSkeleton';
import {ToolCard} from './ToolCard';
import {CatalogFilters} from './CatalogFilters';
import {useCatalogFilters} from './useCatalogFilters';
export const Catalog=memo(function Catalog({onOpen,phase}){
 const {status,retry}=useCatalogData();
 const state=useCatalogFilters();
 const {filtered,filters,clear}=state;
 const displayed=useAnimatedCatalog(filtered);
 usePageReveal([phase,filters,...displayed.map(t=>t.id)].join('|'));
 return ( <div className="catalog-shell"><div className="wrap">
 <section className="catalog" id="catalogo"><div className="section-top"><div><RevealHeading text="Explora más de 1000+ herramientas Open Source"/></div></div>
 <CatalogFilters state={state} count={filtered.length}/>
 {status==='loading'&&<CatalogSkeleton/>}
 {status==='error'&&<div role="alert"><p>{interfaceErrors.catalog}</p><button className="ui-button ui-button--secondary" onClick={retry}>{errorActions.retry}</button></div>}
 {status!=='loading'&&<div className="grid">{displayed.map(tool=><ToolCard key={tool.id} tool={tool} onOpen={onOpen}/>)}</div>}
 {status==='ready'&&filtered.length===0&&displayed.length===0&&<div className="empty"><Search size={30}/><h3>No encontramos coincidencias</h3><button onClick={clear} className="primary ui-wash">Ver todas las herramientas</button></div>}
 </section><footer className="catalog-footer"><a className="brand" href="#"><img className="openbridge-logo" src="/assets/brands/openbridge.svg" alt="OpenBridge"/></a></footer></div></div>);
});
