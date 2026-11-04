import {useRef,useState} from 'react';
import {ArrowRight,ArrowUpRight,Box,ChevronDown,Layers3,Workflow} from 'lucide-react';
import {useCatalogData} from '../../data/CatalogProvider';
import {resolveComponentTool} from '../../data/assistant.mjs';
import {BrandIcon} from '../../AssistantBrandIcon';
import {useBrandIdentity} from '../../brandIdentity';

function ToolRecommendation({component}){
 const {tools}=useCatalogData();
 const tool=resolveComponentTool(component,tools);
 const identity=useBrandIdentity(tool??{name:component.label});
 return <li className="proposal-tool" style={{'--proposal-brand':identity.palette.start}}>
  <div className="proposal-tool-heading"><span className="proposal-brand" aria-hidden="true">{tool?<BrandIcon tool={tool}/>:<Box/>}</span><div><h3>{component.label}</h3><p>{component.role}</p></div></div>
  <details className="proposal-rationale"><summary>Por qué se recomienda</summary><p>{component.rationale}</p></details>
  {tool&&<a href={'#herramienta/'+tool.id}>Ver ficha <ArrowUpRight size={14} aria-hidden="true"/></a>}
 </li>;
}
function Endpoint({component}){
 const {tools}=useCatalogData();
 const tool=resolveComponentTool(component,tools);
 return <span className="proposal-endpoint"><span className="proposal-brand" aria-hidden="true">{tool?<BrandIcon tool={tool}/>:<Box/>}</span><span>{component.label}</span></span>;
}
export function ProposalTabs({response}){
 const [tab,setTab]=useState('tools');
 const [opened,setOpened]=useState(null);
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
    {connections.length===0?<p className="proposal-empty">Esta propuesta no incluye conexiones.</p>:<ul className="proposal-connections">{connections.map((connection,index)=><li key={`${connection.from_key}-${connection.to_key}-${index}`}>
     <button className="proposal-connection" type="button" aria-label={`${components.get(connection.from_key).label} hacia ${components.get(connection.to_key).label}, ${connection.protocol}`} aria-expanded={opened===index} aria-controls={'proposal-connection-'+index} onClick={()=>setOpened(opened===index?null:index)}>
      <Endpoint component={components.get(connection.from_key)}/><ArrowRight className="connection-arrow" size={20} aria-hidden="true"/><Endpoint component={components.get(connection.to_key)}/><span className="proposal-protocol">{connection.protocol}</span><ChevronDown className="connection-chevron" size={20} aria-hidden="true"/>
     </button>
     <div id={'proposal-connection-'+index} className={'proposal-explanation'+(opened===index?' is-open':'')} aria-hidden={opened!==index}><div><p>{connection.description}</p></div></div>
    </li>)}</ul>}
   </section>
  </div>
 </div>;
}
