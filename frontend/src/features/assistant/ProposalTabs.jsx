import {useId,useRef,useState} from 'react';
import {ArrowRight,ArrowUpRight,Box,TriangleAlert,Layers3,Workflow} from 'lucide-react';
import {useCatalogData} from '../../data/CatalogProvider';
import {resolveComponentTool,recommendationLicenseWarning} from '../../data/assistant.mjs';
import {BrandIcon} from '../../AssistantBrandIcon';
import {useBrandIdentity} from '../../brandIdentity';

function ToolRecommendation({component}){
 const [expanded,setExpanded]=useState(false);
 const rationaleId=useId();
 const {tools}=useCatalogData();
 const tool=resolveComponentTool(component,tools);
 const identity=useBrandIdentity(tool??{name:component.label});
 const licenseWarning=recommendationLicenseWarning(tool);
 return <li className="proposal-tool" style={{'--proposal-brand':identity.palette.start,'--proposal-brand-end':identity.palette.end}}>
  {identity.watermark&&<img className="proposal-watermark" src={identity.watermark} alt="" aria-hidden="true"/>}
  <div className="proposal-tool-heading"><span className="proposal-brand" aria-hidden="true">{tool?<BrandIcon tool={tool}/>:<Box/>}</span><div><h3>{component.label}</h3><p>{component.role}</p></div></div>
  {licenseWarning&&<span className="proposal-license-warning"><TriangleAlert size={14} aria-hidden="true"/>{licenseWarning}</span>}
  <div className={'proposal-rationale'+(expanded?' is-expanded':'')} id={rationaleId}><p>{component.rationale}</p></div>
  <div className="proposal-tool-actions">
   {component.rationale&&<button type="button" className="proposal-reason-toggle" aria-expanded={expanded} aria-controls={rationaleId} onClick={()=>setExpanded(value=>!value)}>{expanded?'Ver menos':'Ver motivo'}</button>}
   {tool&&<a className="ui-wash" href={'#herramienta/'+tool.id}>Ver ficha <ArrowUpRight size={14} aria-hidden="true"/></a>}
  </div>
 </li>;
}
function Endpoint({component}){
 const {tools}=useCatalogData();
 const tool=resolveComponentTool(component,tools);
 return <span className="proposal-endpoint"><span className="proposal-brand" aria-hidden="true">{tool?<BrandIcon tool={tool}/>:<Box/>}</span><span>{component.label}</span></span>;
}
function ConnectionCard({connection,from,to}){
 const {tools}=useCatalogData();
 const fromIdentity=useBrandIdentity(resolveComponentTool(from,tools)??{name:from.label});
 const toIdentity=useBrandIdentity(resolveComponentTool(to,tools)??{name:to.label});
 return <li className="connection-tile" style={{'--connection-from':fromIdentity.palette.start,'--connection-to':toIdentity.palette.end}}>
  <div className="connection-tile-route" aria-label={`${from.label} hacia ${to.label}, ${connection.protocol}`}>
   <Endpoint component={from}/>
   <span className="connection-tile-direction"><ArrowRight size={22} strokeWidth={1.5} aria-hidden="true"/></span>
   <Endpoint component={to}/>
  </div>
  {connection.protocol&&<span className="connection-protocol">{connection.protocol}</span>}
  <p>{connection.description}</p>
 </li>;
}
export function ProposalTabs({response}){
 const [tab,setTab]=useState('tools');
 const tabs=useRef([]);
 const connections=response.connections??[];
 const components=new Map(response.components.map(c=>[c.key,c]));
 const select=(index)=>{setTab(index===0?'tools':'connections');tabs.current[index]?.focus();};
 const onKeyDown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();select(e.key==='Home'?0:e.key==='End'?1:tab==='tools'?1:0);}};
 return <div className="proposal-tabs">
  <div role="tablist" aria-label="Propuesta de arquitectura" onKeyDown={onKeyDown}>
   {[['tools','Herramientas',response.components.length,Layers3],['connections','Conexiones',connections.length,Workflow]].map(([key,label,count,Icon],index)=><button key={key} ref={el=>{tabs.current[index]=el;}} id={'proposal-tab-'+key} type="button" role="tab" aria-selected={tab===key} aria-controls={'proposal-panel-'+key} tabIndex={tab===key?0:-1} onClick={()=>setTab(key)}><Icon size={17} aria-hidden="true"/>{label}<span>{count}</span></button>)}
  </div>
  <div className="proposal-panels">
   <section id="proposal-panel-tools" role="tabpanel" aria-labelledby="proposal-tab-tools" hidden={tab!=='tools'} tabIndex={0}>
    <ul className="proposal-tools">{response.components.map(component=><ToolRecommendation key={component.key} component={component}/>)}</ul>
   </section>
   <section id="proposal-panel-connections" role="tabpanel" aria-labelledby="proposal-tab-connections" hidden={tab!=='connections'} tabIndex={0}>
    {connections.length===0?<p className="proposal-empty">Esta propuesta no incluye conexiones.</p>:<ul className="connection-tiles">{connections.map((connection,index)=><ConnectionCard key={`${connection.from_key}-${connection.to_key}-${index}`} connection={connection} from={components.get(connection.from_key)} to={components.get(connection.to_key)}/>)}</ul>}
   </section>
  </div>
 </div>;
}
