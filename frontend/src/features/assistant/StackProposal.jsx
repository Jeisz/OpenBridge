import {ProposalTabs} from './ProposalTabs';

export function StackProposal({expanded,pending,hasResult,slow,response,originalPrompt}){
 const ok=response?.status==='ok';
 return <div className={'architecture-stage '+(expanded?'is-visible':'')} aria-busy={pending}><div className="architecture-stage-clip">
 <div className="stack-surface">
 <div className={'stack-content'+(!hasResult?' is-waiting':'')}>
 {hasResult&&ok&&<section className="stack-layers-panel" aria-label="Propuesta de arquitectura">
  <ProposalTabs key={response.id} response={response}/>
  <ResponseContext response={response} compact/>
  {originalPrompt&&<section className="proposal-original"><h3>Tu idea original</h3><p>{originalPrompt}</p></section>}
 </section>}
 {hasResult&&!ok&&<section className={'stack-outcome'+(response?.status==='needs_clarification'?' clarification-outcome':'')} aria-label={response?.status==='needs_clarification'?'Aclaraciones necesarias':'Sin evidencia suficiente'}>

 {response?.status==='needs_clarification'?<ol className="clarification-questions" key={response.id}>{response.clarification_questions.map((q,i)=><li className="clarification-question" onPointerMove={event=>{if(event.pointerType==='touch'||!matchMedia('(hover:hover) and (prefers-reduced-motion:no-preference)').matches)return;const card=event.currentTarget,rect=card.getBoundingClientRect();card.style.setProperty('--glare-x',`${event.clientX-rect.left}px`);card.style.setProperty('--glare-y',`${event.clientY-rect.top}px`);}} key={i} style={{'--question-delay':`${Math.min(i,5)*55}ms`}}><span className="clarification-number" aria-hidden="true">{String(i+1).padStart(2,'0')}</span><p>{q}</p></li>)}</ol>:null}
 <ResponseContext response={response}/>
 {originalPrompt&&response?.status!=='needs_clarification'&&<section className="proposal-original"><h3>Tu idea original</h3><p>{originalPrompt}</p></section>}</section>}
 </div></div></div></div>;
}
function ResponseContext({response}){
 return response&&<div className="proposal-context-open">{[["Supuestos",response.assumptions],["Limitaciones",response.limitations]].map(([title,items])=>items.length>0&&<section key={title} className={title==='Supuestos'?'context-panel context-assumptions':'context-panel context-limitations'}><h3>{title}</h3><ul>{items.map((v,i)=><li key={i}>{v}</li>)}</ul></section>)}</div>;
}
