import React from 'react';
import {toolCategoryNames} from '../../data/catalog.mjs';
import {CardDescription} from './CardDescription';
import {useCatalogData} from '../../data/CatalogProvider';
import {useBrandIdentity,markBrandFailed} from '../../brandIdentity';
import {useCardTilt} from '../../useCardTilt';
import {UserRound,Star,GitCommitHorizontal,Scale,Activity,ArrowRight,ArrowUpRight} from 'lucide-react';
export function ToolCard({ tool, onOpen }) {
 const {profiles}=useCatalogData();
 const tiltRef = useCardTilt();
 const description=profiles[tool.id]?.summary;
 const identity=useBrandIdentity(tool);
 const logo=identity.logo;
 const categoryNames=toolCategoryNames(tool);
 const extraCategories=categoryNames.slice(2);
 const detail = tool;
 const hasHealth=Number.isFinite(detail.healthScore);
 const healthTone = !hasHealth?'unknown':detail.healthScore >= 80 ? 'good' : detail.healthScore >= 60 ? 'moderate' : 'low';
 const healthLabel = {good:'Salud alta',moderate:'Salud media',low:'Salud baja'}[healthTone];
 const brand = identity.palette;
 const postgres = tool.name === 'PostgreSQL';
 const metrics = [
  ['Estrellas', tool.stars.toLocaleString('es-CL'), Star],
  ['Último push', tool.activity, GitCommitHorizontal],
  ['Licencia', tool.license, Scale],
  ['Mantenedor activo', tool.maintained === true ? 'Sí' : tool.maintained === false ? 'No' : 'Por confirmar', UserRound]
 ];
 return <article data-tool-id={tool.id} onClick={e=>{if(!e.target.closest('a,button,summary,details')&&!window.getSelection()?.toString())onOpen(tool.id,e.currentTarget.querySelector('.detail-link'));}} ref={tiltRef} className="tool-card" aria-label={tool.name} style={{
  '--brand-start': brand.start, '--brand-end': brand.end, '--brand-tag': brand.tag
 }}>
  <div className="card-surface">
  <div className="tool-card-intro">
   {identity.watermark && (postgres ? <div className="card-watermark" aria-hidden="true"><img src={identity.watermark} onError={()=>markBrandFailed('watermark:'+identity.watermark)} alt=""/></div> : <img className="brand-watermark" src={identity.watermark} onError={()=>markBrandFailed('watermark:'+identity.watermark)} alt="" aria-hidden="true"/>)}
   <div className="tool-card-title">
    {identity.fallback ? <span className="brand-initials" aria-hidden="true">{identity.initials}</span> : postgres ? <div className="tool-logo"><img src={logo} onError={()=>markBrandFailed(logo)} alt=""/></div> : <img className={identity.wordmark ? 'brand-logo brand-wordmark' : 'brand-logo'} src={logo} onError={()=>markBrandFailed(logo)} alt=""/>}
    <h3 className={identity.wordmark ? 'sr-only' : undefined}>{tool.name}</h3>
   </div>
   <div className="tool-tags">
    {categoryNames.slice(0,2).map(category=><span key={category}>{category}</span>)}
    {extraCategories.length>0&&<span className="category-overflow" aria-label={`${extraCategories.length} categorías más: ${extraCategories.join(", ")}`} title={extraCategories.join(", ")}>+{extraCategories.length}</span>}

   </div>
   {description&&<CardDescription description={description} tool={tool} onOpen={onOpen}/>}
  </div>
  <div className="tool-card-details">
   <div className="card-tech-summary">
   <span className={"health-score health-score--"+healthTone} role="img" aria-label={hasHealth?`Salud del repositorio: ${detail.healthScore} de 100`:'Salud sin evaluar'}>
    <Activity size={20} strokeWidth={1.75} className="health-icon" aria-hidden="true"/>
    <strong aria-hidden="true">{hasHealth?<>{detail.healthScore}<span>/100</span></>:<span>Sin evaluar</span>}</strong>
   </span>
   <span className="language-tag" title="Lenguaje principal del repositorio">{tool.language}</span>
   </div>
   <dl className="tool-metrics">{metrics.map(([label,value,Icon],index)=><React.Fragment key={label}>
    {index > 0 && <div className="metric-divider" aria-hidden="true"><img src="/assets/cards/divider.svg" alt=""/></div>}
    <div className="tool-metric"><dt><Icon size={14} strokeWidth={1.75} aria-hidden="true"/><span>{label}</span></dt><dd>{value}</dd></div>
   </React.Fragment>)}</dl>
   <div className="tool-actions">
    <a className="detail-link ui-button ui-button--secondary ui-button--compact" href={'#herramienta/'+tool.id} onClick={e=>{if(!e.metaKey&&!e.ctrlKey&&!e.shiftKey&&!e.altKey){e.preventDefault();onOpen(tool.id,e.currentTarget);}}} aria-label={'Ver detalle de '+tool.name}>Ver detalle <ArrowRight size={14}/></a>
    {tool.repo ? <a className="ui-button ui-button--tertiary ui-button--compact" href={'https://github.com/'+tool.repo} target="_blank" rel="noopener noreferrer" aria-label={'Ver repositorio de '+tool.name+' (otra pestaña)'}>Repositorio <ArrowUpRight size={16} aria-hidden="true"/></a> : <button type="button" className="example-repository ui-button ui-button--tertiary ui-button--compact" disabled aria-disabled="true" aria-label="Repositorio no disponible para Default">Repositorio <ArrowUpRight size={16} aria-hidden="true"/></button>}
   </div>
  </div>
  <div className="card-glare" aria-hidden="true"/>
  </div>
 </article>;
}
