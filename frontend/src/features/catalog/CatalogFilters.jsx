import React from 'react';
import {populatedCategories} from '../../data/catalog.mjs';
import {Search,SlidersHorizontal,X} from 'lucide-react';
import {useCatalogData} from '../../data/CatalogProvider';

export function CatalogFilters({state,count}){
 const {tools,categories:catalogCategories}=useCatalogData();
 const categories=['Todas',...populatedCategories(catalogCategories,tools).map(category=>category.name)];
 const {search,setSearch,category,setCategory,filters,setFilters,language,setLanguage,license,setLicense,maintenance,setMaintenance,stars,setStars,active,clear}=state;
 return <> <div className="search-row"><div className="search-box"><Search size={19}/><label htmlFor="search" className="sr-only">Buscar herramientas</label><input id="search" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar herramientas por nombre o descripción…"/>{search&&<button className="icon-button ui-wash" aria-label="Borrar búsqueda" onClick={()=>setSearch('')}><X size={16}/></button>}</div><button className={'filter-button ui-wash '+(filters?'selected':'')} aria-expanded={filters} aria-controls="filters" onClick={()=>setFilters(!filters)}><SlidersHorizontal size={16}/> Filtros {active>0&&<span className="badge">{active}</span>}</button></div>
 <div className="categories" aria-label="Categorías">{categories.map(c=><button key={c} aria-pressed={category===c} className={'category-chip'+(category===c?' active':'')} onClick={e=>{const chip=e.currentTarget,rect=chip.getBoundingClientRect(),radius=Math.hypot(rect.width,rect.height)/2+1;chip.style.setProperty('--chip-radius',radius+'px');if(!matchMedia('(prefers-reduced-motion: reduce)').matches)chip.animate([{clipPath:'circle(0px at 50% 50%)'},{clipPath:`circle(${radius}px at 50% 50%)`}],{pseudoElement:'::before',duration:280,easing:'cubic-bezier(.22,1,.36,1)'});setCategory(c);}}>{c}</button>)}</div>
 {filters && (
  <div className="filters" id="filters">
   <label>Lenguaje
    <select value={language} onChange={e => setLanguage(e.target.value)}>
     <option value="">Todos</option>
     {Array.from(new Set(tools.map(tool => tool.language))).map(value => <option key={value} value={value}>{value}</option>)}
    </select>
   </label>
   <label>Licencia
    <select value={license} onChange={e => setLicense(e.target.value)}>
     <option value="">Todos</option>
     {Array.from(new Set(tools.map(tool => tool.license))).map(value => <option key={value} value={value}>{value}</option>)}
    </select>
   </label>
   <label>Estado del repositorio
    <select value={maintenance} onChange={e => setMaintenance(e.target.value)}>
     <option value="">Todos</option><option value="archived">Archivados</option><option value="disabled">Deshabilitados</option>
    </select>
   </label>
   <label>Estrellas mínimas
    <select value={stars} onChange={e => setStars(e.target.value)}>
     <option value="">Sin mínimo</option><option value="10000">10.000</option><option value="20000">20.000</option><option value="50000">50.000</option>
    </select>
   </label>
  </div>
 )}
 <div className="results-meta"><span className="sr-only" aria-live="polite">{count} {count===1?'herramienta':'herramientas'}{category!=='Todas'?' en '+category:''}</span>{(active>0||search||category!=='Todas')&&<button className="ui-wash" onClick={clear}>Limpiar filtros <X size={13}/></button>}</div>
</>;
}
