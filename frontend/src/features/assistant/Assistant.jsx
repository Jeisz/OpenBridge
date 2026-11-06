import React,{useState,useLayoutEffect,useRef} from 'react';
import {PromptSuggestions} from './PromptSuggestions';
import {getAssistantError} from '../../errorPresentation.mjs';
import {RevealHeading} from '../../PageReveal';
import {HeroLights} from '../../HeroLights';
import {promptMotion} from '../../promptPresentation.mjs';
import {StackProposal} from './StackProposal';
import {PromptComposer} from './PromptComposer';
export function Assistant({flow,workspace=false}){
 const host=useRef(null);
 useLayoutEffect(()=>{
  const root=host.current,composer=root?.querySelector('.prompt-form-slot');if(!root||!composer)return;
  const measure=()=>root.style.setProperty('--assistant-dock-height',`${composer.getBoundingClientRect().height}px`);
  const observer=new ResizeObserver(measure);observer.observe(composer);measure();
  return()=>observer.disconnect();
 },[workspace]);
 useLayoutEffect(()=>{
  const slot=host.current?.querySelector('.prompt-form-slot');
  if(!workspace||!slot?.dataset.dockOrigin)return;
  const origin=JSON.parse(slot.dataset.dockOrigin);delete slot.dataset.dockOrigin;
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const target=slot.getBoundingClientRect();
  const options={duration:620,easing:'cubic-bezier(.16,1,.3,1)'};
  const form=slot.querySelector('form');
  const resize=form.animate([{height:`${origin.height}px`},{height:`${form.getBoundingClientRect().height}px`}],options);
  const animation=slot.animate([{translate:`${origin.left-target.left}px ${origin.top+origin.height-target.bottom}px`},{translate:'0px 0px'}],options);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const cancel=()=>{animation.cancel();resize.cancel();};
  window.addEventListener('resize',cancel);reduced.addEventListener('change',cancel);
  return()=>{cancel();window.removeEventListener('resize',cancel);reduced.removeEventListener('change',cancel);};
 },[workspace]);
 const [exampleReveal,setExampleReveal]=useState(null);
 const {assistantResponse,originalPrompt,slow,resultHeading,finished,pending,expanded,hasResult,input,newArchitecture,error,canRetry}=flow;
 const errorCopy=error?getAssistantError(error):null;
 const headerActive=expanded||Boolean(error);
 const heading=pending?'Preparando tu stack':errorCopy?errorCopy.title:assistantResponse?.title||({needs_clarification:'Precisemos tu idea',no_evidence:'Sin evidencia suficiente'}[assistantResponse?.status]||'Tu arquitectura');
 const description=pending?(slow?'La solicitud está tardando más de lo habitual.':'Estamos generando tu propuesta.'):errorCopy?errorCopy.description:assistantResponse?.summary||'';
 return (<div ref={host} className={'hero'+(workspace?' assistant-workspace':'')}><HeroLights inputRef={input}/><section id="asistente"><div className={'hero-inner'+(expanded?' has-architecture':'')+(error?' has-request-error':'')} style={Object.fromEntries([...Object.entries(promptMotion).filter(([key])=>key!=='ease').map(([key,value])=>[`--prompt-${key}-duration`,`${value}ms`]),['--prompt-ease',promptMotion.ease]])}>
 <div className="prompt-heading"><div className="prompt-heading-initial" aria-hidden={headerActive}><RevealHeading as="h1" text="De tu idea a tu stack" gradientWord="stack" mobileBreak/></div><h1 ref={resultHeading} tabIndex={-1} className="prompt-heading-result" aria-hidden={!headerActive}><span className={'assistant-heading-content'+(pending?' is-pending':'')}><span className="assistant-light-loader" aria-hidden="true"/><span key={heading} className="assistant-heading-copy">{pending?<>Preparando tu <span className="gradient-word"><span className="reveal-letter" data-glow="stack" style={{'--word-play-state':'running'}}>stack</span></span></>:heading}</span></span></h1></div>
 <div className="prompt-intro" role="status" aria-live="polite" aria-atomic="true"><p className="intro intro-initial" aria-hidden={headerActive}>Describe lo que quieres construir y descubre las herramientas open source para hacerlo realidad.</p><p id="prompt-error" className="intro intro-result" aria-hidden={!headerActive}><span key={description} className="assistant-heading-copy">{description}</span></p></div>
 <StackProposal expanded={expanded} pending={pending} hasResult={hasResult} slow={slow} response={assistantResponse} originalPrompt={originalPrompt}/>

 <PromptComposer {...flow} workspace={workspace} exampleReveal={exampleReveal}/>

 </div><PromptSuggestions flow={flow} onSelect={text=>setExampleReveal({text,id:performance.now()})}/></section>
 </div>
);
}
