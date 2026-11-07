import {useEffect,useId,useState} from 'react';
import {ArrowUpRight,ChevronDown,SignalLow,SignalMedium,SignalHigh,Check,Sparkles} from 'lucide-react';
import {Snippet} from './Snippet';

function ReviewBadge({idea}){
 const [open,setOpen]=useState(false);
 const [dismissed,setDismissed]=useState(false);
 const id=useId();
 useEffect(()=>{
  const dismiss=()=>{setDismissed(true);setOpen(false);};
  window.addEventListener('dismiss-review-tooltip',dismiss);
  return()=>window.removeEventListener('dismiss-review-tooltip',dismiss);
 },[]);
 const reviewed=idea.reviewStatus==='reviewed';
 const supported=reviewed||idea.reviewStatus==='suggested';
 if(!idea.reviewLabel)return null;
 if(!supported)return <span className="integration-review">{idea.reviewLabel}</span>;
 const Icon=reviewed?Check:Sparkles;
 const followPointer=event=>{
  if(event.pointerType==='touch')return;
  const wrap=event.currentTarget;
  const rect=wrap.getBoundingClientRect();
  const tooltip=wrap.querySelector('[role="tooltip"]');
  const bounds=wrap.closest('.integration')?.getBoundingClientRect();
  const right=Math.min(bounds?.right??window.innerWidth,window.innerWidth)-12;
  const x=Math.max(0,Math.min(event.clientX-rect.left+12,right-rect.left-tooltip.offsetWidth));
  wrap.style.setProperty('--review-x',`${x}px`);
  wrap.style.setProperty('--review-y',`${event.clientY-rect.bottom+16}px`);
 };
 const resetPosition=event=>{
  event.currentTarget.parentElement.style.removeProperty('--review-x');
  event.currentTarget.parentElement.style.removeProperty('--review-y');
 };
 return <span className="integration-review-wrap" onPointerEnter={event=>{followPointer(event);setDismissed(false);setOpen(true);}} onPointerMove={followPointer} onMouseLeave={()=>setOpen(false)}>
  <button type="button" className="integration-review" data-review={idea.reviewStatus} aria-describedby={open&&!dismissed?id:undefined}
   onFocus={event=>{resetPosition(event);setDismissed(false);setOpen(true);}} onBlur={()=>setOpen(false)} onClick={event=>{event.stopPropagation();setDismissed(false);setOpen(true);}}
   onKeyDown={event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();setDismissed(true);setOpen(false);}}}>
   <Icon size={13} strokeWidth={1.7} aria-hidden="true"/>{idea.reviewLabel}
  </button>
  <span id={id} role="tooltip" aria-hidden={!open||dismissed} data-open={open&&!dismissed} className="integration-review-tooltip">{reviewed?'Esta idea fue revisada por profesionales.':'Esta idea fue generada por IA y aún no ha sido revisada por profesionales.'}</span>
 </span>;
}

export function IntegrationIdeas({ideas}){
 const [opened,setOpened]=useState(ideas[0]?.id??null);
 const prefix=useId();
 if(!ideas.length)return <section className="detail-integrations integration-accordion"><h2>Ideas de integración</h2><p>No hay ideas de integración disponibles para esta herramienta.</p></section>;
 return <section className="detail-integrations integration-accordion"><h2>Ideas de integración</h2>
  {ideas.map((idea,index)=>{
   const expanded=opened===idea.id;
   const level=({'Básica':'low','Intermedia':'medium','Avanzada':'high'})[idea.difficulty]??'unknown';
   const LevelIcon=({low:SignalLow,medium:SignalMedium,high:SignalHigh})[level];
   const panelId=`${prefix}-panel-${index}`,headingId=`${prefix}-heading-${index}`;
   const facts=[['Stack compatible',idea.stack],['Dependencias',idea.dependencies],['Disparadores',idea.triggers]].filter(([,value])=>Array.isArray(value)?value.length:!!value);
   return <article className={'integration'+(expanded?' is-open':'')} key={idea.id}>
    <div className="integration-header" onClick={()=>setOpened(expanded?null:idea.id)}>
    <div className="integration-review-heading"><ReviewBadge idea={idea}/></div>
    <h3 className="integration-heading"><button id={headingId} type="button" className="integration-toggle" aria-expanded={expanded} aria-controls={panelId}>
     <span className="integration-title">{idea.title}</span>
     <span className="integration-header-field"><span>Tipo</span><span className="integration-type">{idea.type}</span></span>
     <span className="integration-header-field"><span>Dificultad</span><span className="integration-difficulty" data-level={level}>{LevelIcon&&<LevelIcon size={16} strokeWidth={2} aria-hidden="true"/>}{idea.difficulty}</span></span>
     <ChevronDown size={20} className="integration-chevron" aria-hidden="true"/>
    </button></h3>
    </div>
    <div id={panelId} role="region" aria-labelledby={headingId} aria-hidden={!expanded} inert={!expanded?true:undefined} className="integration-collapse"><div className="integration-collapse-clip"><div className="integration-content">
     {idea.summary&&<p className="integration-summary">{idea.summary}</p>}
     <div className="integration-columns">
      <dl className="integration-facts">{facts.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{Array.isArray(value)?<ul>{value.map((text,i)=><li key={i}>{text}</li>)}</ul>:value}</dd></div>)}</dl>
      <div className="integration-code">{idea.snippet?<Snippet text={idea.snippet} language={idea.snippetLanguage}/>:<div className="integration-code-empty">Código no disponible</div>}{idea.docs&&<a className="integration-docs" href={idea.docs} target="_blank" rel="noopener noreferrer">Consultar documentación <ArrowUpRight size={15} aria-hidden="true"/></a>}</div>
     </div>
    </div></div></div>
   </article>;
  })}
 </section>;
}
