import {ChevronLeft,ChevronRight} from 'lucide-react';
import {pageNumbers} from './pagination.mjs';

export function CatalogPagination({page,pages,onChange}){
 if(pages<=1)return null;
 return <nav className="catalog-pagination" aria-label="Páginas del catálogo">
  <button type="button" className="ui-button ui-button--secondary ui-button--compact" disabled={page===1} onClick={()=>onChange(page-1)} aria-label="Página anterior"><ChevronLeft aria-hidden="true"/><span className="pagination-direction-label">Anterior</span></button>
  <div className="catalog-page-numbers">{pageNumbers(page,pages).map(number=>typeof number==='number'?<button key={number} type="button" className={`ui-button ui-button--compact ui-button--icon ui-button--${number===page?'primary':'tertiary'}`} aria-label={`Página ${number}`} aria-current={number===page?'page':undefined} onClick={()=>onChange(number)}>{number}</button>:<span key={number} aria-hidden="true" className="catalog-page-gap">…</span>)}</div>
  <button type="button" className="ui-button ui-button--secondary ui-button--compact" disabled={page===pages} onClick={()=>onChange(page+1)} aria-label="Página siguiente"><span className="pagination-direction-label">Siguiente</span><ChevronRight aria-hidden="true"/></button>
 </nav>;
}
