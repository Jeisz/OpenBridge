import {reloadHome} from '../../reloadHome.mjs';
import {interfaceErrors,errorActions} from '../../errorPresentation.mjs';
import React,{memo,useState,useMemo,useRef,useLayoutEffect,useEffect} from 'react';
import {CatalogPagination} from './CatalogPagination';
import {paginateCatalog} from './pagination.mjs';
import {scrollToCatalogPage} from './scrollToCatalogPage.mjs';
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
 const filterKey=JSON.stringify([state.search,state.category,state.language,state.license,state.maintenance,state.stars]);
 const [selection,setSelection]=useState({key:filterKey,page:1});
 if(selection.key!==filterKey)setSelection({key:filterKey,page:1});
 const pagination=useMemo(()=>paginateCatalog(filtered,selection.key===filterKey?selection.page:1),[filtered,selection,filterKey]);
 const displayed=useAnimatedCatalog(pagination.items);
 const gridRef=useRef(null),pendingPage=useRef(false),pageScroll=useRef(()=>{});
 useEffect(()=>()=>pageScroll.current(),[]);
 const changePage=page=>{
  if(page===pagination.page)return;
  pendingPage.current=true;
  setSelection({key:filterKey,page});
  const grid=gridRef.current;
  if(grid){
   const header=document.querySelector('header')?.getBoundingClientRect().height??64;
   const top=window.scrollY+grid.getBoundingClientRect().top-header-20;
   pageScroll.current();
   pageScroll.current=scrollToCatalogPage(Math.max(0,top));
  }
 };
 useLayoutEffect(()=>{
  if(!pendingPage.current||displayed!==pagination.items)return;
  pendingPage.current=false;
  gridRef.current?.focus({preventScroll:true});
 },[displayed,pagination.items]);
 usePageReveal([phase,filters,...displayed.map(t=>t.id)].join('|'));
 return ( <div className="catalog-shell"><div className="wrap">
 <section className="catalog" id="catalogo"><div className="section-top"><div><RevealHeading text="Explora más de 1000+ herramientas Open Source"/></div></div>
 <CatalogFilters state={state} count={filtered.length}/>
 {status==='loading'&&<CatalogSkeleton/>}
 {status==='error'&&<div className="catalog-error" role="alert"><img className="catalog-error-face" src="/assets/catalog-error.png" width="320" height="320" alt="" aria-hidden="true"/><p>{interfaceErrors.catalog}</p><button className="ui-button ui-button--secondary" onClick={retry}>{errorActions.retry}</button></div>}
 {status!=='loading'&&<div ref={gridRef} className="grid catalog-results" tabIndex={-1} aria-label={`Herramientas, página ${pagination.page} de ${pagination.pages}`}>{displayed.map(tool=><ToolCard key={tool.id} tool={tool} onOpen={onOpen}/>)}</div>}
 {status==='ready'&&filtered.length===0&&displayed.length===0&&<div className="empty"><Search size={30}/><h3>No encontramos coincidencias</h3><button onClick={clear} className="ui-button ui-button--primary">Ver todas las herramientas</button></div>}
 {status==='ready'&&filtered.length>0&&<>
  <p className="sr-only" role="status">Página {pagination.page} de {pagination.pages}. {pagination.items.length} herramientas de {filtered.length}.</p>
  <CatalogPagination page={pagination.page} pages={pagination.pages} onChange={changePage}/>
 </>}
 </section><footer className="catalog-footer"><a className="brand" href="/" onClick={reloadHome}><img className="openbridge-logo" src="/assets/brands/openbridge.svg" alt="OpenBridge"/></a></footer></div></div>);
});
