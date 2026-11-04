import React from 'react';

export function IntegrationIdeasSkeleton(){
 return <section className="detail-integrations integration-skeleton" aria-busy="true" aria-label="Cargando ideas de integración" role="status">
  <h2 aria-hidden="true">Ideas de integración</h2>
  <div className="integration-skeleton-surface" aria-hidden="true">
   <div className="integration-skeleton-heading"><i/><span/><span/></div>
   <div className="integration-skeleton-lines"><i/><i/></div>
   <div className="integration-skeleton-columns"><div><i/><i/><i/></div><div/></div>
  </div>
 </section>;
}
