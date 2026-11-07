import {useId,useRef,useState,useLayoutEffect} from 'react';
import {ArrowUpRight,Box,TriangleAlert,Layers3,Workflow} from 'lucide-react';
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
   {component.rationale&&<button type="button" className="proposal-reason-toggle ui-button ui-button--text" aria-expanded={expanded} aria-controls={rationaleId} onClick={()=>setExpanded(value=>!value)}>{expanded?'Ver menos':'Ver motivo'}</button>}
   {tool&&<a className="ui-button ui-button--secondary ui-button--compact" href={'#herramienta/'+tool.id}>Ver ficha <ArrowUpRight size={14} aria-hidden="true"/></a>}
  </div>
 </li>;
}
function Endpoint({component}){
 const {tools}=useCatalogData();
 const tool=resolveComponentTool(component,tools);
 const identity=useBrandIdentity(tool??{name:component.label});
 return <span className="connection-node" style={{'--node-start':identity.palette.start,'--node-end':identity.palette.end}}><span className="proposal-brand" aria-hidden="true">{tool?<BrandIcon tool={tool}/>:<Box/>}</span><span>{component.label}</span></span>;
}
function ConnectionGroup({from,connections,components}){
 const root=useRef(null);
 const markerId=useId().replaceAll(':','');
 const [paths,setPaths]=useState([]);
 useLayoutEffect(()=>{
  const element=root.current;
  const measure=()=>{
   const box=element.getBoundingClientRect();
   const source=element.querySelector('.connection-source').getBoundingClientRect();
   const mobile=window.matchMedia('(max-width:640px)').matches;
   const x=mobile?source.left-box.left+20:source.right-box.left;
   const y=mobile?source.bottom-box.top:source.top-box.top+source.height/2;
   const next=[...element.querySelectorAll('.connection-destination')].map(target=>{
    const end=target.getBoundingClientRect();
    const tx=end.left-box.left,ty=end.top-box.top+end.height/2;
    const bend=mobile?x:x+32;
    return mobile?`M ${x} ${y} V ${ty-12} Q ${x} ${ty} ${x+12} ${ty} H ${tx-4}`:`M ${x} ${y} H ${bend-12} C ${bend+12} ${y}, ${bend-12} ${ty}, ${bend+12} ${ty} H ${tx-4}`;
   });
   setPaths(previous=>JSON.stringify(previous)===JSON.stringify(next)?previous:next);
  };
  const observer=new ResizeObserver(measure);
  observer.observe(element);
  element.querySelectorAll('.connection-source,.connection-destination,.connection-branch').forEach(node=>observer.observe(node));
  measure();
  return()=>observer.disconnect();
 },[connections]);
 return <li className="connection-group" ref={root}>
  <svg className="connection-wires" aria-hidden="true"><defs><marker id={markerId} markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M 0 0 L 7 3.5 L 0 7 Z" fill="currentColor"/></marker></defs>{paths.map((path,index)=><path key={index} d={path} markerEnd={`url(#${markerId})`}/>)}</svg>
  <div className="connection-source"><Endpoint component={from}/></div>
  <ul className="connection-branches">{connections.map((connection,index)=><li className="connection-branch" key={`${connection.to_key}-${index}`}>
   <span className="sr-only">{from.label} hacia {components.get(connection.to_key).label}</span>
   <div className="connection-route-copy">{connection.protocol&&<span className="connection-route-protocol">{connection.protocol}</span>}{connection.description&&<p>{connection.description}</p>}</div>
   <div className="connection-destination"><Endpoint component={components.get(connection.to_key)}/></div>
  </li>)}</ul>
 </li>;
}
export function ProposalTabs({response}){
 const [tab,setTab]=useState('tools');
 const tabs=useRef([]);
 const connections=response.connections??[];
 const components=new Map(response.components.map(c=>[c.key,c]));
 const groups=new Map();
 connections.forEach(connection=>{
  if(!groups.has(connection.from_key))groups.set(connection.from_key,[]);
  groups.get(connection.from_key).push(connection);
 });
 const select=(index)=>{setTab(index===0?'tools':'connections');tabs.current[index]?.focus();};
 const onKeyDown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();select(e.key==='Home'?0:e.key==='End'?1:tab==='tools'?1:0);}};
 return <div className="proposal-tabs">
  <div role="tablist" data-active={tab} aria-label="Propuesta de arquitectura" onKeyDown={onKeyDown}>
   {[['tools','Herramientas',response.components.length,Layers3],['connections','Conexiones',connections.length,Workflow]].map(([key,label,count,Icon],index)=><button key={key} ref={el=>{tabs.current[index]=el;}} id={'proposal-tab-'+key} type="button" role="tab" aria-selected={tab===key} aria-controls={'proposal-panel-'+key} tabIndex={tab===key?0:-1} onClick={()=>setTab(key)}><Icon size={17} aria-hidden="true"/>{label}<span>{count}</span></button>)}
  </div>
  <div className="proposal-panels">
   <section id="proposal-panel-tools" role="tabpanel" aria-labelledby="proposal-tab-tools" hidden={tab!=='tools'} tabIndex={0}>
    <ul className="proposal-tools">{response.components.map(component=><ToolRecommendation key={component.key} component={component}/>)}</ul>
   </section>
   <section id="proposal-panel-connections" role="tabpanel" aria-labelledby="proposal-tab-connections" hidden={tab!=='connections'} tabIndex={0}>
    {connections.length===0?<p className="proposal-empty">Esta propuesta no incluye conexiones.</p>:<ul className="connection-map">{[...groups].map(([key,items])=><ConnectionGroup key={key} from={components.get(key)} connections={items} components={components}/>)}</ul>}
   </section>
  </div>
 </div>;
}
