import {useLayoutEffect,useRef} from 'react';
import {observeProposalHeight} from './observeProposalHeight.mjs';
import {ProposalTabs} from './ProposalTabs';

export function StackProposal({expanded,pending,hasResult,slow,response}){
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
 </section>}
 {hasResult&&!ok&&<section className="stack-outcome" aria-label={response?.status==='needs_clarification'?'Aclaraciones necesarias':'Sin evidencia suficiente'}>

 {response?.status==='needs_clarification'?<><ol>{response.clarification_questions.map((q,i)=><li key={i}>{q}</li>)}</ol></>:null}
 <ResponseContext response={response}/></section>}
 </div></div></div></div>;
}
function ResponseContext({response,compact=false}){
 if(compact)return (response.assumptions.length>0||response.limitations.length>0)&&<div className="assistant-context"><details><summary>Supuestos y limitaciones</summary>{[["Supuestos",response.assumptions],["Limitaciones",response.limitations]].map(([title,items])=>items.length>0&&<div key={title}><h3>{title}</h3><ul>{items.map((v,i)=><li key={i}>{v}</li>)}</ul></div>)}</details></div>;
 return response&&<div className="assistant-context">{response.assumptions.length>0&&<details><summary>Supuestos</summary><ul>{response.assumptions.map((v,i)=><li key={i}>{v}</li>)}</ul></details>}{response.limitations.length>0&&<details><summary>Limitaciones</summary><ul>{response.limitations.map((v,i)=><li key={i}>{v}</li>)}</ul></details>}</div>;
}
