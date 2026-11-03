import React from 'react';

export function CatalogSkeleton(){
 return <div className="catalog-skeleton" role="status" aria-label="Cargando herramientas">
  <div className="grid" aria-hidden="true">{Array.from({length:6},(_,index)=><div className="catalog-skeleton-card" key={index}>
   <div className="catalog-skeleton-intro">
    <div className="catalog-skeleton-title"><i/><span/></div>
    <div className="catalog-skeleton-tags"><span/><span/></div>
    <div className="catalog-skeleton-description"><span/><span/><span/></div>
   </div>
   <div className="catalog-skeleton-details">
    <span className="catalog-skeleton-health"/>
    {Array.from({length:4},(_,row)=><div className="catalog-skeleton-row" key={row}><span/><span/></div>)}
   </div>
   <div className="catalog-skeleton-actions"><span/><span/></div>
  </div>)}</div>
 </div>;
}
