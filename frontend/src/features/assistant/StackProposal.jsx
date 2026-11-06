import {useLayoutEffect,useRef} from 'react';
import {observeProposalHeight} from './observeProposalHeight.mjs';
import {ProposalTabs} from './ProposalTabs';

export function StackProposal({expanded,pending,hasResult,slow,response,originalPrompt}){
 const content=useRef(null);
 const surface=useRef(null);
 useLayoutEffect(()=>observeProposalHeight(content.current,surface.current),[]);
 const ok=response?.status==='ok';
 return <div className={'architecture-stage '+(expanded?'is-visible':'')} aria-busy={pending}><div className="architecture-stage-clip">
 <div className="stack-surface" ref={surface}>
 <div ref={content} className={'stack-content'+(!hasResult?' is-waiting':'')}>
 {hasResult&&ok&&<section className="stack-layers-panel" aria-label="Propuesta de arquitectura">
  <ProposalTabs key={response.id} response={response}/>
  <ResponseContext response={response} compact/>
  {originalPrompt&&<section className="proposal-original"><h3>Tu idea original</h3><p>{originalPrompt}</p></section>}
 </section>}
 {hasResult&&!ok&&<section className="stack-outcome" aria-label={response?.status==='needs_clarification'?'Aclaraciones necesarias':'Sin evidencia suficiente'}>

 {response?.status==='needs_clarification'?<><ol>{response.clarification_questions.map((q,i)=><li key={i}>{q}</li>)}</ol></>:null}
 <ResponseContext response={response}/>
 {originalPrompt&&<section className="proposal-original"><h3>Tu idea original</h3><p>{originalPrompt}</p></section>}</section>}
 </div></div></div></div>;
}
function ResponseContext({response}){
 return response&&<div className="proposal-context-open">{[["Supuestos",response.assumptions],["Limitaciones",response.limitations]].map(([title,items])=>items.length>0&&<section key={title} className={title==='Supuestos'?'context-panel context-assumptions':'context-panel context-limitations'}><h3>{title}</h3><ul>{items.map((v,i)=><li key={i}>{v}</li>)}</ul></section>)}</div>;
}
